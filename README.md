# rs-tracker-lambda
Grab rs stats from API and store in S3 AWS lambda.

This works in conjunction with the web app in my `ami-nginx` repo and the `rs-api` container in https://github.com/mdinos/mdinos-docker

## usage

Firstly, set environment variable (which s3 bucket to use):
`$ bucket='rs-tracker-lambda-bucket'`

You'll have to add a line invoking the lambda locally (neither of these input vars are used in the script:
```
lambda_handler('event','context')
```

Run the script:
```
python rs_tracker_lambda.py
```

I recommend using [aws-profile](https://github.com/jrstarke/aws-profile) (it's installable as a [pip](https://pypi.org/project/aws-profile/)) to manage your credentials when running locally - set up a role with the following permissions: (example terraform)
```hcl
actions = [
      "s3:PutObject",
      "s3:GetObject"
    ]
resources = [
      "arn:aws:s3:::${var.lambda_name}*",
    ]
```

and invoke locally like so:

```shell
aws-profile -p lambda-profile python rs_tracker_lambda.py
```

For creating the actual role for the lambda to run itself, you'll need a couple more permissions (if you want to use cloudwatch logs): (example terraform)
```hcl
statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "arn:aws:logs:${var.region}:${var.account_number}:log-group:/aws/lambda/${var.lambda_name}:*",
    ]
  }
```

## packaging to lambda format
`./package.sh` will generate a .zip object in `../`

can be used with some basic terraform:

```hcl
resource "aws_lambda_function" "rs_tracker_lamda" {
    filename         = "rs_tracker_lambda.zip"
    function_name    = "rs_tracker_lambda"
    role             = "<<your role here folks>>"
    handler          = "rs_tracker_lambda.lambda_handler"
    source_code_hash = "${base64sha256("rs_tracker_lambda.zip")}"
    runtime          = "python3.6"
    timeout = "30"
  
    environment {
        variables = {
            bucket = "<<your s3 bucket>>"
        }
    }
}
```

In your S3 bucket, you will need a users.json file at the base level, like this:
```json
{ "users" : ["user_1", "user_n"] }
```

## requirements

Pips will be installed by package.sh when zipped, but to install dependencies for development, cd to directory and::
```bash
pip install pipreqs
pipreqs ./
pip install -r requirements.txt
```
