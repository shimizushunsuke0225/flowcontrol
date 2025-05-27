output "lambda_function_name" {
  description = "Name of the created Lambda function"
  value       = aws_lambda_function.cloudfront_behavior_switcher.function_name
}

output "lambda_function_arn" {
  description = "ARN of the created Lambda function"
  value       = aws_lambda_function.cloudfront_behavior_switcher.arn
}

output "lambda_invoke_arn" {
  description = "Invoke ARN of the created Lambda function"
  value       = aws_lambda_function.cloudfront_behavior_switcher.invoke_arn
}