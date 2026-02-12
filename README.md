# cdk_ssl_cert
CDK stack for provisioning the SSL/TLS certificate for my personal site

### Step 1. Install CDK
First we need to initialise the CDK app, and specify a language, here I am using Python.
This command will create the CDK app, it needs to be run in an empty directory, and will use the directory name when generating resource names, so consider the name you pick.

```
cdk init app --language python
```

When using Python, CDK will automatically set up a virtual environment, to enable it in the terminal use the following command;

```
source .venv/bin/activate
```

### Step 2. Connect GitHub to AWS
Using OpenID Connect (OIDC), we can connect the repository to our AWS account, this will let us run AWS/CDK commands with GitHub Actions workflows. There are a few other ways of doing this (access keys etc.) but the advantage of OIDC is you don't need long-lived credentials.

First we go to the IAM page in AWS, then 'Identity Providers', then add a new provider. Select OpenID Connect, and use the provider URL and audience details for GitHub (found [here](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)).

Then we need to assign a role to that identity provider, go to the newly created provider and click 'Assign Role'. Then choose 'Web identity' and fill in the details; for 'GitHub organisation', put your GitHub account name (e.g. 'ZakMarden' for me). Then add the neccessary permissions. Once the role has been created, make a note of the ARN.

Next we need to set up the AWS secrets in our repository, so they can be securely used by our workflows. To do this we go the settings page, then 'Secrets and Variables', then 'Actions'. Here we need to make two new repository secrets, one for the role ARN, and one for AWS region (I call them AWS_ROLE_ARN and AWS_REGION).

Now the secrets are setup they are ready to be used in our workflows - so we need to make a step in the workflow for configuring our AWS access, this will look something like this;

```
- name: Configure AWS Credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: ${{ secrets.AWS_REGION }}
```

If everything has been setup correctly, this step will generate temporary access credentials, with the permissions we chose, so that subsequent steps can run AWS commands.

We can test this has worked by creating a workflow to run following command;

```
aws sts get-caller-identity
```

If successful, this should return the UserID, Account Number, and User ARN. See [here](.github/workflows/aws_connect_test.yml) for an example workflow which uses this to test the AWS credentials.

### Step 3. Make the Stack
Our stack will use the [Certificate](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_certificatemanager/Certificate.html) construct for creating the certificate itself. There are two main parameters which need to be set for this; domain_name and validation. 

'domain_name' is the domain we want the certificate for (e.g. example.com), I am also using the subject_alternative_names parameter, with a wildcard (e.g. *.example.com). This means that the certificate will cover all subdomains, and the root/apex domain. 

'validation' tells the certificate manager how we are going to prove that we own the domain, as I've already got a hosted zone set up, with Route53 as the DNS provider, I will use the 'from_dns' method to validate the certificate. This works on the principle that if you can add a DNS record, then you own the domain. It does this by requesting a unique CNAME record is added. A CNAME, or canonical name, is a record which redirects requests for one domain to another. This CNAME record acts as a key-value pair, in simple terms the certificate manager says; add a record to your DNS, so that requests to abc123.example.com are mapped to xyz789.aws.com. Ther certificate manager then looks up abc123.example.com, and if they find the request is mapped to xyz789.aws.com, they know the record must have been added, and that you own the domain.

```
certificate = acm.Certificate(
      self,
      "SiteCertificate",
      certificate_name=f"cert-{domain_name}",
      domain_name=domain_name,
      subject_alternative_names=[f"*.{domain_name}"],
      validation=acm.CertificateValidation.from_dns(hosted_zone)
  )
```

To use this method for validation, we need to provide the hosted zone for the domain, this means we need to add a [HostedZone](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_route53/HostedZone.html) construct to our stack. As I've already got the hosted zone setup, I just need to import it into the stack, rather than create it. To do this I'll use the 'from_hosted_zone_id' method, which allows me to import the zone using it's ID.

```
hosted_zone = route53.HostedZone.from_hosted_zone_id(
      self,
      "HostedZone",
      hosted_zone_id=hosted_zone_id
  )
```

To avoid having to hardcode any sensitive details, I am passing the domain name and hosted zone id into the stack from environment variables, these need to be passed as arguments for the stack class;

```
def __init__(self, scope: Construct, construct_id: str, domain_name: str, hosted_zone_id: str, **kwargs) -> None:
```

For the variables to be accessed by the stack, they need declaring in our CDK App app.py file, as follows;

```
CertAppStack(app, "CertAppStack",
    domain_name=os.getenv('DOMAIN_NAME'),
    hosted_zone_id=os.getenv('HOSTED_ZONE_ID'),
    env=cdk.Environment(account=os.getenv('AWS_ACCOUNT'), region=os.getenv('CDK_CERT_REGION')),
    )
```

Finally, we also need to ensure that the CDK environment is set up correctly, by passing in our AWS account ID, and the region. It's important to note here that as I will be using CloudFront as the CDN for the site, the certificate needs to be in the 'us-east-1' region, which is a requirment for CloudFront to use the certificate. As seen above I am also passing these in as environment variables.


