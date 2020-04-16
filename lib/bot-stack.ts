import cdk = require("@aws-cdk/core");
import iam = require("@aws-cdk/aws-iam");
import _lambda = require("@aws-cdk/aws-lambda");
import path = require("path");
import apigateway = require("@aws-cdk/aws-apigateway");

export class BotStack extends cdk.Construct {
  constructor(scope: cdk.Construct, id: string) {
    super(scope, id);

    const role = new iam.Role(this, "BotRole", {
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
          "apigateway:*",
          "lex:*",
        ],
      })
    );

    //Line
    //Lambda Function
    const LineBot = new _lambda.Function(this, "LineBot", {
      runtime: _lambda.Runtime.PYTHON_3_8,
      handler: "app.lambda_handler",
      code: _lambda.Code.fromAsset(path.join(__dirname, "./lambda/LineBot")),
      environment: {
        ACCESS_TOKEN:
          "vRlJ4Rl0JJNammMWmDiuuM50fraBdDNjr8s1dR5zRgGTFlh5UfB6K9IPzYM+jJQ9MPC+5OqX09J3auvmIdhHYjVZBiXaQIGAFYFxwB0zaIg1a19S1U20nigKdX3H5rdt8xXru9kULrOFR8qQaJu1wwdB04t89/1O/w1cDnyilFU=",
        SECRET: "ff3fba95cffd3f66de878972ee200b21",
      },
      role: role,
      tracing: _lambda.Tracing.ACTIVE,
    });

    //apigateway
    const Line_api = new apigateway.LambdaRestApi(this, "LineBotapi", {
      handler: LineBot,
      proxy: false,
    });

    const LineItems = Line_api.root.addResource("LineBot");
    LineItems.addMethod("POST");

    //Telegram
    //Lambda Function
    const TelegramBot = new _lambda.Function(this, "TelegramBot", {
      runtime: _lambda.Runtime.PYTHON_3_8,
      handler: "app.lambda_handler",
      code: _lambda.Code.fromAsset(
        path.join(__dirname, "./lambda/TelegramBot")
      ),
      environment: {
        TELE_TOKEN: "813409289:AAHyfynRIPtJfVG5HzH_oO5b97Oxq0pWL90",
      },
      role: role,
      tracing: _lambda.Tracing.ACTIVE,
    });

    //apigateway
    const Telegram_api = new apigateway.LambdaRestApi(this, "TelegramBotapi", {
      handler: TelegramBot,
      proxy: false,
    });

    const TelegramItems = Telegram_api.root.addResource("TelegramBot");
    TelegramItems.addMethod("POST");
  }
}
