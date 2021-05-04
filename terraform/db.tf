# data "aws_ami" "amazon_linux" {
#   most_recent = true

#   filter {
#     name   = "name"
#     values = ["amzn-ami*amazon-ecs-optimized"]
#   }

#   filter {
#     name   = "architecture"
#     values = ["x86_64"]
#   }

#   filter {
#     name   = "virtualization-type"
#     values = ["hvm"]
#   }
#   owners = ["amazon", "self"]
# }


resource "aws_security_group" "ec2-sg-db" {
  name        = "allow-all-ec2-db"
  description = "allow all"
  vpc_id      = data.aws_vpc.main.id
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "jefferson.moura"
  }
}


module "elb" {
  source  = "terraform-aws-modules/elb/aws"
  version = "2.3.0"

  name = "db-elb"

  subnets         = module.vpc.public_subnets
  security_groups = [aws_security_group.ec2-sg-db.id]
  internal        = false

  listener = [
    {
      instance_port     = 5432
      instance_protocol = "TCP"
      lb_port           = 5432
      lb_protocol       = "TCP"
    },
    {
      instance_port     = 27017
      instance_protocol = "TCP"
      lb_port           = 27017
      lb_protocol       = "TCP"
    },
  ]

  health_check = {
    target              = "TCP:5432"
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
  }


  tags = {
    "env"       = "dev"
    "createdBy" = "jefferson.moura"
  }
}



resource "aws_launch_configuration" "lc-db" {
  name          = "challenge_ecs_db"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "t2.micro"
  lifecycle {
    create_before_destroy = true
  }
  iam_instance_profile        = aws_iam_instance_profile.ecs_service_role_db.name
  key_name                    = var.key_name
  security_groups             = [aws_security_group.ec2-sg-db.id]
  associate_public_ip_address = true
  user_data                   = <<EOF
#! /bin/bash
sudo apt-get update
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo docker run -d \
-p 5432:5432 \
-e POSTGRES_PASSWORD='admin' \
-e POSTGRES_USER='admin' \
jefferson22alcantara/challenge-job:pg
sudo docker run -d --name mongodb \
-e MONGO_INITDB_ROOT_USERNAME='admin' \
-e MONGO_INITDB_ROOT_PASSWORD='admin' \
-p 27017:27017 \
mongo

EOF
}

resource "aws_autoscaling_group" "asg-db" {
  name                      = "challenge-asg-db"
  launch_configuration      = aws_launch_configuration.lc-db.name
  min_size                  = 1
  max_size                  = 1
  desired_capacity          = 1
  health_check_type         = "ELB"
  health_check_grace_period = 60
  vpc_zone_identifier       = module.vpc.public_subnets
  load_balancers            = [module.elb.this_elb_id]
  protect_from_scale_in     = true
  lifecycle {
    create_before_destroy = true
  }
}


