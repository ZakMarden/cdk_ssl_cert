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

