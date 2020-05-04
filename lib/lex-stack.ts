import cdk = require("@aws-cdk/core");
import iam = require("@aws-cdk/aws-iam");
import _lambda = require("@aws-cdk/aws-lambda");
import path = require("path");
import dynamodb = require("@aws-cdk/aws-dynamodb");
import { Table } from "@aws-cdk/aws-dynamodb";

export class LexStack extends cdk.Construct {
  constructor(scope: cdk.Construct, id: string, reminderRecord: Table) {
    super(scope, id);

    const role = new iam.Role(this, "LexRole", {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
    });

    role.addToPolicy(
      new iam.PolicyStatement({
        resources: ["*"],
        actions: [
          "lambda:*",
          "states:*",
          "events:*",
          "xray:*",
          "cloudwatch:*",
          "logs:*",
          "dynamodb:*",
          "sns:*",
        ],
      })
    );

    //DB
    const LineUser = new dynamodb.Table(this, "LineUser", {
      partitionKey: {
        name: "userID",
        type: dynamodb.AttributeType.STRING,
      },
    });

    const TelegramUser = new dynamodb.Table(this, "TelegramUser", {
      partitionKey: {
        name: "userID",
        type: dynamodb.AttributeType.STRING,
      },
    });

    //Lambda Function
    const ReminderController = new _lambda.Function(
      this,
      "ReminderController",
      {
        runtime: _lambda.Runtime.PYTHON_3_8,
        handler: "lambda_function.lambda_handler",
        code: _lambda.Code.fromAsset(
          path.join(__dirname, "./lambda/reminder_controller")
        ),
        environment: {
          tableName: reminderRecord.tableName,
        },
        role: role,
        tracing: _lambda.Tracing.ACTIVE,
      }
    );
  }
}
