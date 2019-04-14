# rs-tracker-lambda
Grab rs stats from API and store in S3 AWS lambda.

## usage

`./package.sh` will generate a .zip object in `../`

can be used with some basic terraform:

```
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
            username = "<<your_username>>"
        }
    }
}
```