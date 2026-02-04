#!/usr/bin/env python3
import os

import aws_cdk as cdk

from dotenv import load_dotenv
load_dotenv()

from cert_app.cert_app_stack import CertAppStack

app = cdk.App()

CertAppStack(app, "CertAppStack",
    domain_name=os.getenv('DOMAIN_NAME'),
    hosted_zone_id=os.getenv('HOSTED_ZONE_ID'),
    env=cdk.Environment(account=os.getenv('AWS_ACCOUNT'), region=os.getenv('CDK_CERT_REGION')),
    )

app.synth()
