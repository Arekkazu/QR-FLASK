output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.app.id
}

output "public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.app.public_ip
}

output "ssh_command" {
  description = "SSH command for connecting to the EC2 instance"
  value       = "ssh -i <path-to-private-key.pem> ec2-user@${aws_instance.app.public_ip}"
}

output "app_url" {
  description = "URL to access the Flask app"
  value       = "http://${aws_instance.app.public_ip}"
}
