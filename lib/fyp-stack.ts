import cdk = require("@aws-cdk/core");
import dynamodb = require("@aws-cdk/aws-dynamodb");
import { ConnectStack } from "./connect-stack";
import { BotStack } from "./bot-stack";
import { LexStack } from "./lex-stack";

export class FypStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    //DB for record user data
    const userRecord = new dynamodb.Table(this, "UserRecord", {
      partitionKey: {
        name: "phoneNumber",
        type: dynamodb.AttributeType.STRING,
      },
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
    });

    const userDeviceRecord = new dynamodb.Table(this, "UserDeviceRecord", {
      partitionKey: {
        name: "device_1",
        type: dynamodb.AttributeType.STRING,
      },
    });

    //DB for record remider elder eat medicine time
    const reminderRecord = new dynamodb.Table(this, "ReminderRecord", {
      partitionKey: {
        name: "phoneNumber",
        type: dynamodb.AttributeType.STRING,
      },
    });

    //DB for record call detail
    const callRecord = new dynamodb.Table(this, "CallRecord", {
      partitionKey: {
        name: "phoneNumber",
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: { name: "callTime", type: dynamodb.AttributeType.STRING },
    });

    //Build the connect stack
    new ConnectStack(
      this,
      "CallConnetStack",
      reminderRecord,
      callRecord,
      userDeviceRecord,
      userRecord
    );

    new BotStack(this, "BotStack");

    new LexStack(this, "LexStack", reminderRecord);
  }
}
