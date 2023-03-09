# alpacked-test-assignment

Welcome to ~~The Hunger Games~~ Alpacked test assignment!

## Prerequisites

To complete this assignment you need to install tools and runtimes from the list below.

1. AWS CLI
2. Docker
3. Python(3.9 or higher)
4. NodeJS(16.18 or higher) -- in case of NodeJS lambda source code
4. Pulumi or CDK

## Assignment details

The main scope of this assignment is to check your troubleshooting skills and knowledge of DevOps tools like `bash`, `Docker`, `AWS`, `IaC(Pulumi or AWS CDK)` and one of the programming languages: `Python` or `NodeJS`.

There are 2 different infrastructure deployments(Pulumi and CDK) and 2 lambda source codes that have been written in Python and NodeJS respectively.

So, there are a few options that are available for you to complete this assignment:
- Pulumi + Python
- CDK + Python
- Pulumi + NodeJS
- CDK + NodeJS

Pulumi stack placed in `pulumi` folder.
CDK stack placed in `cdk` folder.

Lambda source code is placed in folder `lambdas` folder.

What does all this stuff do?

Pulumi or CDK are used for infrastructure deployment on AWS. (S3 bucket and lambda)

Lambda working as a custom watermark lib.

### How to work with the repo

1. Install all necessary tools
2. Choose your stack from the available options that have been described above.
3. Create dedicated branch in repo, do not push to master branch directly!
4. Run `source ./runtime.sh` script to choose runtime and install all dependencies.
5. Work with Pulumi or CDK to deploy infrastructure to AWS
6. Do whatever you want to get the expected result.

## What needs to be done:

There are some "easter eggs" in this repo, you need to find and fix all bugs that will appear during the completion of this assignment.
Create a list with all issues that you found, list must look like:
`file: line of code -- issue -- how you fixed it`

## Expected result:

In `images` folder there is zip archive with test images.<br>
After the zip archive is uploaded to an S3 bucket, lambda has to process these images and add a watermark to each image and upload a new zip archive with processed images back to the S3 bucket.<br>
After all job done, you should create pull request in your repo. Pull request branch should contain your changes and zip archive with processed images.

## Acceptance criteria:

All bugs are fixed, and lambda is working as expected.<br><br>

Good luck!