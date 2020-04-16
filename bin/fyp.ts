#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { FypStack } from '../lib/fyp-stack';

const app = new cdk.App();
new FypStack(app, 'FypStack');
