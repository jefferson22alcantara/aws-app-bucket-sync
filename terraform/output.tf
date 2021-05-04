output "alb_dns" {
  value = aws_lb.challenge-lb.dns_name
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "public_subnets" {
  value = module.vpc.public_subnets
}

output "private_subnets" {
  value = module.vpc.private_subnets
}
output "igw_id" {
  value = module.vpc.igw_id
}

output "this_elb_dns_name" {
  description = "The DNS name of the ELB"
  value       = module.elb.this_elb_dns_name
}
# output "elb_dns_name" {
#   value = module.elb.this_elb_dns_name
# }

# output "this_elb_id" {
#   value = module.elb.this_elb_id
# }
# output "elb_id" {
#   description = "The name of the ELB"
#   value       = module.elb.elb_id
# }

# output "elb_name" {
#   description = "The name of the ELB"
#   value       = module.elb.elb_name
# }

# output "elb_dns_name" {
#   description = "The DNS name of the ELB"
#   value       = module.elb.elb_dns_name
# }
