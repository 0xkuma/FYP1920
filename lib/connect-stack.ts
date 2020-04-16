import cdk = require("@aws-cdk/core");
import iam = require("@aws-cdk/aws-iam");
import sfn = require("@aws-cdk/aws-stepfunctions");
import tasks = require("@aws-cdk/aws-stepfunctions-tasks");
import sqs = require("@aws-cdk/aws-sqs");
import {
  SqsEventSource,
  DynamoEventSource,
} from "@aws-cdk/aws-lambda-event-sources";
import _lambda = require("@aws-cdk/aws-lambda");
import events = require("@aws-cdk/aws-events");
import targets = require("@aws-cdk/aws-events-targets");
import path = require("path");
import { Table } from "@aws-cdk/aws-dynamodb";

export class ConnectStack extends cdk.Construct {
  constructor(
    scope: cdk.Construct,
    id: string,
    reminderRecord: Table,
    callRecord: Table,
    userDeviceRecord: Table,
    userRecord: Table
  ) {
    super(scope, id);

    //IAM
    const role = new iam.Role(this, "OutboundVoiceContact", {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
    });

    role.addToPolicy(
      new iam.PolicyStatement({
        resources: ["*"],
        actions: [
          "sqs:*",
          "lambda:*",
          "states:*",
          "events:*",
          "xray:*",
          "dynamodb:*",
          "cloudwatch:*",
          "connect:*",
          "logs:*",
          "sns:*",
        ],
      })
    );

    const streamRole = new iam.Role(this, "CallRecordProcessRole", {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
    });

    streamRole.addToPolicy(
      new iam.PolicyStatement({
        resources: ["*"],
        actions: [
          "lambda:*",
          "states:*",
          "events:*",
          "xray:*",
          "dynamodb:*",
          "cloudwatch:*",
          "connect:*",
          "logs:*",
        ],
      })
    );
    //End for IAM

    //SQS
    const connect_dead_sqs = new sqs.Queue(
      this,
      "DeadLetterQueueToOutBoundVoiceContact",
      {
        visibilityTimeout: cdk.Duration.seconds(15),
        retentionPeriod: cdk.Duration.hours(1),
      }
    );
    const connect_sqs = new sqs.Queue(this, "QueueToOutBoundVoiceContact", {
      deadLetterQueue: { queue: connect_dead_sqs, maxReceiveCount: 1 },
      visibilityTimeout: cdk.Duration.seconds(5),
      retentionPeriod: cdk.Duration.minutes(1),
    });
    //End for SQS

    //Lambda Function
    const sfnCreateCallRecord = new _lambda.Function(
      this,
      "sfnCreateCallRecord",
      {
        runtime: _lambda.Runtime.PYTHON_3_8,
        handler: "sfnCreateCallRecord.lambda_handler",
        code: _lambda.Code.fromAsset(
          path.join(__dirname, "./lambda/SfnCreateCallRecord")
        ),
        environment: { tableName: callRecord.tableName },
        role: role,
        tracing: _lambda.Tracing.ACTIVE,
      }
    );

    const sfnUpdateCallRecord = new _lambda.Function(
      this,
      "sfnUpdateCallRecord",
      {
        runtime: _lambda.Runtime.PYTHON_3_8,
        handler: "sfnUpdateCallRecord.lambda_handler",
        code: _lambda.Code.fromAsset(
          path.join(__dirname, "./lambda/SfnUpdateCallRecord")
        ),
        environment: { tableName: callRecord.tableName },
        role: role,
        tracing: _lambda.Tracing.ACTIVE,
      }
    );

    const IoTSNS = new _lambda.Function(this, "IoTSNS", {
      runtime: _lambda.Runtime.PYTHON_3_8,
      handler: "IoTSNS.lambda_handler",
      code: _lambda.Code.fromAsset(path.join(__dirname, "./lambda/IoTSNS")),
      role: role,
      tracing: _lambda.Tracing.ACTIVE,
    });

    const send_task_success = new _lambda.Function(this, "send_task_success", {
      runtime: _lambda.Runtime.PYTHON_3_8,
      handler: "send_task_success.lambda_handler",
      code: _lambda.Code.fromAsset(
        path.join(__dirname, "./lambda/send_task_success")
      ),
      role: role,
      tracing: _lambda.Tracing.ACTIVE,
    });

    //Grant Permission for Amazon Connect to invoke lambda
    send_task_success.addPermission(
      "allowConnectInvocation_send_task_success",
      {
        principal: new iam.ServicePrincipal("connect.amazonaws.com"),
        sourceAccount: "283070137225",
        sourceArn:
          "arn:aws:connect:us-east-1:283070137225:instance/a142f0e1-2d80-4b8b-9efd-d2053580963b",
        action: "lambda:InvokeFunction",
      }
    );

    const connectInvoke = new _lambda.Function(this, "ConnectInvoke", {
      runtime: _lambda.Runtime.PYTHON_3_8,
      handler: "ConnectInvoke.lambda_handler",
      code: _lambda.Code.fromAsset(
        path.join(__dirname, "./lambda/ConnectInvoke")
      ),
      environment: {
        tableName: callRecord.tableName,
      },
      role: role,
      tracing: _lambda.Tracing.ACTIVE,
    });

    //Grant Permission for Amazon Connect to invoke lambda
    connectInvoke.addPermission("allowConnectInvocation_connectInvoke", {
      principal: new iam.ServicePrincipal("connect.amazonaws.com"),
      sourceAccount: "283070137225",
      sourceArn:
        "arn:aws:connect:us-east-1:283070137225:instance/a142f0e1-2d80-4b8b-9efd-d2053580963b",
      action: "lambda:InvokeFunction",
    });

    new _lambda.Function(this, "OutBoundVoiceContact", {
      runtime: _lambda.Runtime.PYTHON_3_8,
      handler: "OutBoundVoiceContact.lambda_handler",
      code: _lambda.Code.fromAsset(
        path.join(__dirname, "./lambda/OutBoundVoiceContact")
      ),
      environment: {
        send_task_success_arn: send_task_success.functionArn,
        connectInvoke_arn: connectInvoke.functionArn,
      },
      role: role,
      tracing: _lambda.Tracing.ACTIVE,
    }).addEventSource(new SqsEventSource(connect_sqs));

    //End for Lambda

    //StepFunction
    const start = new sfn.Pass(this, "Start");

    const voiceCallIterator = new sfn.Map(this, "VoiceCallIterator");

    const createCallRecord = new sfn.Task(this, "CreateCallRecord", {
      task: new tasks.InvokeFunction(sfnCreateCallRecord),
    });

    const wait = new sfn.Wait(this, "Wait For Send SNS", {
      time: sfn.WaitTime.secondsPath("$.waitTime"),
    });

    const sendSNS = new sfn.Task(this, "SendSNS", {
      task: new tasks.InvokeFunction(IoTSNS),
    }).next(wait);

    const callSQS = new sfn.Task(this, "CallSQS", {
      task: new tasks.SendToQueue(connect_sqs, {
        integrationPattern: sfn.ServiceIntegrationPattern.WAIT_FOR_TASK_TOKEN,
        messageBody: sfn.TaskInput.fromObject({
          "Message.$": "$",
          TaskToken: sfn.Context.taskToken,
        }),
      }),
      timeout: cdk.Duration.seconds(15),
    });

    const timeOutUpdateTimeoutCallRecord = new sfn.Task(
      this,
      "TimeoutUpdateCallRecord",
      {
        task: new tasks.InvokeFunction(sfnUpdateCallRecord),
      }
    );

    const warningHandle = new sfn.Pass(this, "WarningHandle")
      .next(sendSNS)
      .next(createCallRecord);

    const medicineHandle = new sfn.Pass(this, "MedicineHandle").next(
      createCallRecord
    );

    const urgentHandle = new sfn.Pass(this, "UrgentHandle");

    const definition = start.next(
      voiceCallIterator.iterator(
        new sfn.Choice(this, "Type")
          .when(
            sfn.Condition.stringEquals("$.choose", "warning"),
            warningHandle
          )
          .when(
            sfn.Condition.stringEquals("$.choose", "medicine"),
            medicineHandle
          )
          .when(sfn.Condition.stringEquals("$.choose", "urgent"), urgentHandle)
          .afterwards()
          .next(
            callSQS.addCatch(timeOutUpdateTimeoutCallRecord, {
              errors: ["States.Timeout"],
              resultPath: sfn.DISCARD,
            })
          )
      )
    );

    const sfnMachine = new sfn.StateMachine(this, "StateMachine", {
      definition,
    });
    //End for StepFunction

    // Lambda Function for Sfn usage
    const cron_lambda = new _lambda.Function(
      this,
      "CronToCallOutBoundVoiceContact",
      {
        runtime: _lambda.Runtime.PYTHON_3_8,
        handler: "CronToCallOutBoundVoiceContact.lambda_handler",
        code: _lambda.Code.fromAsset(
          path.join(__dirname, "./lambda/CronToCallOutBoundVoiceContact")
        ),
        environment: {
          StepfunctionArn: sfnMachine.stateMachineArn,
          tableName: reminderRecord.tableName,
        },
        role: role,
        tracing: _lambda.Tracing.ACTIVE,
        timeout: cdk.Duration.seconds(15),
      }
    );

    reminderRecord.grantReadWriteData(cron_lambda);

    const rule = new events.Rule(this, "RuleCallOutBoundVoiceContact", {
      description: "OutBoundVoiceContact invoke each min",
      enabled: false,
      schedule: events.Schedule.cron({
        minute: "/1",
      }),
    });
    rule.addTarget(new targets.LambdaFunction(cron_lambda));

    new _lambda.Function(this, "IoTTriggerLambda", {
      runtime: _lambda.Runtime.PYTHON_3_8,
      handler: "IoTTriggerLambda.lambda_handler",
      code: _lambda.Code.fromAsset(
        path.join(__dirname, "./lambda/IoTTriggerLambda")
      ),
      environment: {
        tableName: userDeviceRecord.tableName,
        StepfunctionArn: sfnMachine.stateMachineArn,
      },
      role: role,
      tracing: _lambda.Tracing.ACTIVE,
    });

    new _lambda.Function(this, "CallRecordProcess", {
      runtime: _lambda.Runtime.PYTHON_3_8,
      handler: "CallRecordProcess.lambda_handler",
      code: _lambda.Code.fromAsset(
        path.join(__dirname, "./lambda/CallRecordProcess")
      ),
      environment: {
        tableName: userRecord.tableName,
        StepfunctionArn: sfnMachine.stateMachineArn,
      },
      role: streamRole,
      tracing: _lambda.Tracing.ACTIVE,
    }).addEventSource(
      new DynamoEventSource(userRecord, {
        startingPosition: _lambda.StartingPosition.LATEST,
      })
    );
    // End of this part
  }
}
