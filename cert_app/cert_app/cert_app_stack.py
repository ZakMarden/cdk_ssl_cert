from aws_cdk import (
    RemovalPolicy,
    Stack,
    aws_route53 as route53,
    aws_certificatemanager as acm,
)
from constructs import Construct

class CertAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, domain_name: str, hosted_zone_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        hosted_zone = route53.HostedZone.from_hosted_zone_id(
            self,
            "HostedZone",
            hosted_zone_id=hosted_zone_id
        )

        certificate = acm.Certificate(
            self,
            "SiteCertificate",
            certificate_name=f"cert-{domain_name}",
            domain_name=domain_name,
            subject_alternative_names=[f"*.{domain_name}"],
            validation=acm.CertificateValidation.from_dns(hosted_zone)
        )

        certificate.apply_removal_policy(RemovalPolicy.DESTROY)