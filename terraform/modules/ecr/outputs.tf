output "repository_names" {
  description = "List of ECR repository names"
  value       = aws_ecr_repository.main[*].name
}

output "repository_urls" {
  description = "List of ECR repository URLs"
  value       = aws_ecr_repository.main[*].repository_url
}

output "repository_arns" {
  description = "List of ECR repository ARNs"
  value       = aws_ecr_repository.main[*].arn
}
