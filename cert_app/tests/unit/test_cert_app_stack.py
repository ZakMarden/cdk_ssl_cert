import aws_cdk as core
import aws_cdk.assertions as assertions

from cert_app.cert_app_stack import CertAppStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cert_app/cert_app_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CertAppStack(app, "cert-app")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
