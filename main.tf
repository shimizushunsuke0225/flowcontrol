provider "aws" {
  region = "us-east-1"
}

resource "aws_lambda_function" "cloudfront_behavior_switcher" {
  function_name = "cloudfront-behavior-switcher"
  handler       = "app.lambda_handler"
  runtime       = "python3.12"
  role          = aws_iam_role.lambda_role.arn
  filename      = "${path.module}/lambda_function.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_function.zip")
  timeout       = 30

  environment {
    variables = {
      DIST_ID       = var.distribution_id
      SORRY_PATTERN = var.sorry_pattern
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name = "cloudfront_behavior_switcher_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "cloudfront_behavior_switcher_policy"
  description = "Policy for CloudFront behavior switcher Lambda"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudfront:GetDistribution",
          "cloudfront:GetDistributionConfig",
          "cloudfront:UpdateDistribution"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Lambda関数のデプロイパッケージを作成するためのnullリソース
resource "null_resource" "lambda_package" {
  triggers = {
    source_code = filemd5("${path.module}/app.py")
  }

  provisioner "local-exec" {
    command = <<EOT
      cd ${path.module}
      zip -r lambda_function.zip app.py
    EOT
  }
}