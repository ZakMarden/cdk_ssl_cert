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

If successful, this should return a JSON containing the UserID, Account Number, and User ARN.

See [here](.github/workflows/aws_connect_test.yml) for an example workflow which uses this to test the AWS credentials. 

