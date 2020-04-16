import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import Fyp = require('../lib/fyp-stack');

test('Empty Stack', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new Fyp.FypStack(app, 'MyTestStack');
    // THEN
    expectCDK(stack).to(matchTemplate({
      "Resources": {}
    }, MatchStyle.EXACT))
});
