resource "aws_ecs_cluster" "web-cluster" {
  name               = var.cluster_name
  capacity_providers = [aws_ecs_capacity_provider.test.name]
  tags = {
    "env"       = "dev"
    "createdBy" = "jefferson.moura"
  }
}

/* Security Group for ECS */ ### TO FARGATE 
# resource "aws_security_group" "ecs_service" {
#   vpc_id      = data.aws_vpc.main.id
#   name        = "ecs-service-sg"
#   description = "Allow egress from container"

#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   ingress {
#     from_port   = 8
#     to_port     = 0
#     protocol    = "icmp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   tags = {
#     "Name"      = "ecs-service-sg"
#     "env"       = "dev"
#     "createdBy" = "jefferson.moura"
#   }
# }


## TO EC2 
resource "aws_ecs_capacity_provider" "test" {
  name = "capacity-provider-test"
  auto_scaling_group_provider {
    auto_scaling_group_arn         = aws_autoscaling_group.asg.arn
    managed_termination_protection = "ENABLED"

    managed_scaling {
      status          = "ENABLED"
      target_capacity = 85
    }
  }
}


/* the task definition for the web service */
data "template_file" "challenge_web_app" {
  template = file("container-definitions/container-def.json")

  vars = {
    POSTGRESS_DB_HOST     = "${module.elb.this_elb_dns_name}"
    MONGO_DB_HOST         = "${module.elb.this_elb_dns_name}"
    AWS_SECRET_ACCESS_KEY = "${var.AWS_SECRET_ACCESS_KEY}"
    AWS_ACCESS_KEY_ID     = "${var.AWS_ACCESS_KEY_ID}"
  }
}

data "template_file" "worker1" {
  template = file("container-definitions/worker1.json")

  vars = {
    POSTGRESS_DB_HOST     = "${module.elb.this_elb_dns_name}"
    MONGO_DB_HOST         = "${module.elb.this_elb_dns_name}"
    AWS_SECRET_ACCESS_KEY = "${var.AWS_SECRET_ACCESS_KEY}"
    AWS_ACCESS_KEY_ID     = "${var.AWS_ACCESS_KEY_ID}"
  }
}

data "template_file" "worker2" {
  template = file("container-definitions/worker2.json")

  vars = {
    POSTGRESS_DB_HOST     = "${module.elb.this_elb_dns_name}"
    MONGO_DB_HOST         = "${module.elb.this_elb_dns_name}"
    AWS_SECRET_ACCESS_KEY = "${var.AWS_SECRET_ACCESS_KEY}"
    AWS_ACCESS_KEY_ID     = "${var.AWS_ACCESS_KEY_ID}"
  }
}

data "template_file" "worker3" {
  template = file("container-definitions/worker3.json")

  vars = {
    POSTGRESS_DB_HOST     = "${module.elb.this_elb_dns_name}"
    MONGO_DB_HOST         = "${module.elb.this_elb_dns_name}"
    AWS_SECRET_ACCESS_KEY = "${var.AWS_SECRET_ACCESS_KEY}"
    AWS_ACCESS_KEY_ID     = "${var.AWS_ACCESS_KEY_ID}"
  }
}

resource "aws_ecs_task_definition" "worker1" {
  family                = "worker1"
  container_definitions = "${data.template_file.worker1.rendered}"
  network_mode          = "bridge" ###awsvpc  to FARGATE 
  tags = {
    "env"       = "dev"
    "createdBy" = "jefferson.moura"
  }
}
resource "aws_ecs_task_definition" "worker2" {
  family                = "worker2"
  container_definitions = "${data.template_file.worker2.rendered}"
  network_mode          = "bridge" ###awsvpc  to FARGATE 
  tags = {
    "env"       = "dev"
    "createdBy" = "jefferson.moura"
  }
}
resource "aws_ecs_task_definition" "worker3" {
  family                = "worker3"
  container_definitions = "${data.template_file.worker3.rendered}"
  network_mode          = "bridge" ###awsvpc  to FARGATE 
  tags = {
    "env"       = "dev"
    "createdBy" = "jefferson.moura"
  }
}


# update file container-def, so it's pulling image from ecr
resource "aws_ecs_task_definition" "task-definition-test" {
  family                = "web"
  container_definitions = "${data.template_file.challenge_web_app.rendered}"
  # requires_compatibilities = ["FARGATE"]  ## TO FARGATE 
  network_mode = "bridge" ###awsvpc  to FARGATE 
  # cpu          = "1024"
  # memory       = "2048"
  tags = {
    "env"       = "dev"
    "createdBy" = "jefferson.moura"
  }
  # execution_role_arn = "${aws_iam_role.ecs_execution_role.arn}"  ###TO FARGATE 
  # task_role_arn      = "${aws_iam_role.ecs_execution_role.arn}"  ###TO FARGATE 
}
resource "aws_ecs_service" "service" {
  name            = "web-service"
  cluster         = aws_ecs_cluster.web-cluster.id
  task_definition = aws_ecs_task_definition.task-definition-test.arn
  desired_count   = 1
  ordered_placement_strategy { #### TO EC2 
    type  = "binpack"          #### TO EC2 
    field = "cpu"              #### TO EC2 
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.lb_target_group.arn
    container_name   = "challenge-web-app"
    container_port   = 80
  }
  lifecycle {
    ignore_changes = [desired_count]
  }
  # network_configuration {
  #   security_groups = ["${module.vpc.default_security_group_id}", "${aws_security_group.ecs_service.id}"]
  #   subnets         = "${module.vpc.public_subnets}"
  # }
  launch_type = "EC2" ### FARGATE  TO FARGATE 
  ###depends_on  = [aws_lb_listener.web-listener, aws_iam_role_policy.ecs_service_role_policy] FARGATE 
  depends_on = [aws_lb_listener.web-listener]

}
resource "aws_ecs_service" "service-worker-1" {
  name    = "service-worker-1"
  cluster = aws_ecs_cluster.web-cluster.id
  #task_definition = "${aws_ecs_task_definition.task-definition-test.family}:${max("${aws_ecs_task_definition.task-definition-test.revision}", "${data.aws_ecs_task_definition.task-definition-test.revision}")}"
  task_definition = aws_ecs_task_definition.worker1.arn
  desired_count   = 1
  ordered_placement_strategy { #### TO EC2 
    type  = "binpack"          #### TO EC2 
    field = "cpu"              #### TO EC2 
  }

  lifecycle {
    ignore_changes = [desired_count]
  }

  launch_type = "EC2" ### FARGATE  TO FARGATE 

}

resource "aws_ecs_service" "service-worker-2" {
  name    = "service-worker-2"
  cluster = aws_ecs_cluster.web-cluster.id
  #task_definition = "${aws_ecs_task_definition.task-definition-test.family}:${max("${aws_ecs_task_definition.task-definition-test.revision}", "${data.aws_ecs_task_definition.task-definition-test.revision}")}"
  task_definition = aws_ecs_task_definition.worker2.arn
  desired_count   = 1
  ordered_placement_strategy { #### TO EC2 
    type  = "binpack"          #### TO EC2 
    field = "cpu"              #### TO EC2 
  }

  lifecycle {
    ignore_changes = [desired_count]
  }

  launch_type = "EC2" ### FARGATE  TO FARGATE 

}

resource "aws_ecs_service" "service-worker-3" {
  name    = "service-worker-3"
  cluster = aws_ecs_cluster.web-cluster.id
  #task_definition = "${aws_ecs_task_definition.task-definition-test.family}:${max("${aws_ecs_task_definition.task-definition-test.revision}", "${data.aws_ecs_task_definition.task-definition-test.revision}")}"
  task_definition = aws_ecs_task_definition.worker3.arn
  desired_count   = 1
  ordered_placement_strategy { #### TO EC2 
    type  = "binpack"          #### TO EC2 
    field = "cpu"              #### TO EC2 
  }

  lifecycle {
    ignore_changes = [desired_count]
  }

  launch_type = "EC2" ### FARGATE  TO FARGATE 

}

resource "aws_cloudwatch_log_group" "log_group" {
  name = "/ecs/frontend-container"
  tags = {
    "env"       = "dev"
    "createdBy" = "jefferson.moura"
  }
}

