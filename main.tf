provider "aws" {
  region = "ap-northeast-1"
}

# Lambda用のZIPファイルを作成
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/app.py"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_lambda_function" "cloudfront_behavior_switcher" {
  function_name = "ptl-inf-pocverify-cloudfront-behavior-switcher"
  handler       = "app.lambda_handler"
  runtime       = "python3.12"
  role          = aws_iam_role.lambda_role.arn
  filename      = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout       = 30

  environment {
    variables = {
      DIST_ID       = var.distribution_id
      SORRY_PATTERN = var.sorry_pattern
    }
  }

  depends_on = [data.archive_file.lambda_zip]
}

resource "aws_iam_role" "lambda_role" {
  name = "ptl-inf-pocverify-cloudfront-switcher-role"

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
  name        = "ptl-inf-pocverify-cloudfront-switcher-policy"
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