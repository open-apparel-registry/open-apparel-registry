#
# Bastion security group resources
#
resource "aws_security_group_rule" "bastion_ssh_ingress" {
  type        = "ingress"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["${var.external_access_cidr_block}"]

  security_group_id = "${module.vpc.bastion_security_group_id}"
}

resource "aws_security_group_rule" "bastion_ssh_egress" {
  type        = "egress"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["${module.vpc.cidr_block}"]

  security_group_id = "${module.vpc.bastion_security_group_id}"
}

resource "aws_security_group_rule" "bastion_rds_enc_egress" {
  type      = "egress"
  from_port = "${module.database_enc.port}"
  to_port   = "${module.database_enc.port}"
  protocol  = "tcp"

  security_group_id        = "${module.vpc.bastion_security_group_id}"
  source_security_group_id = "${module.database_enc.database_security_group_id}"
}

resource "aws_security_group_rule" "bastion_app_egress" {
  type      = "egress"
  from_port = "${var.app_port}"
  to_port   = "${var.app_port}"
  protocol  = "tcp"

  security_group_id        = "${module.vpc.bastion_security_group_id}"
  source_security_group_id = "${aws_security_group.app.id}"
}

resource "aws_security_group_rule" "bastion_http_egress" {
  type             = "egress"
  from_port        = "80"
  to_port          = "80"
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]

  security_group_id = "${module.vpc.bastion_security_group_id}"
}

resource "aws_security_group_rule" "bastion_https_egress" {
  type             = "egress"
  from_port        = "443"
  to_port          = "443"
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]

  security_group_id = "${module.vpc.bastion_security_group_id}"
}

#
# App ALB security group resources
#
resource "aws_security_group_rule" "alb_https_ingress" {
  type             = "ingress"
  from_port        = 443
  to_port          = 443
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]

  security_group_id = "${aws_security_group.alb.id}"
}

resource "aws_security_group_rule" "alb_app_egress" {
  type      = "egress"
  from_port = "${var.app_port}"
  to_port   = "${var.app_port}"
  protocol  = "tcp"

  security_group_id        = "${aws_security_group.alb.id}"
  source_security_group_id = "${aws_security_group.app.id}"
}

#
# RDS security group resources
#
resource "aws_security_group_rule" "rds_enc_app_ingress" {
  type      = "ingress"
  from_port = "${module.database_enc.port}"
  to_port   = "${module.database_enc.port}"
  protocol  = "tcp"

  security_group_id        = "${module.database_enc.database_security_group_id}"
  source_security_group_id = "${aws_security_group.app.id}"
}

resource "aws_security_group_rule" "rds_enc_batch_ingress" {
  type      = "ingress"
  from_port = "${module.database_enc.port}"
  to_port   = "${module.database_enc.port}"
  protocol  = "tcp"

  security_group_id        = "${module.database_enc.database_security_group_id}"
  source_security_group_id = "${aws_security_group.batch.id}"
}

resource "aws_security_group_rule" "rds_enc_bastion_ingress" {
  type      = "ingress"
  from_port = "${module.database_enc.port}"
  to_port   = "${module.database_enc.port}"
  protocol  = "tcp"

  security_group_id        = "${module.database_enc.database_security_group_id}"
  source_security_group_id = "${module.vpc.bastion_security_group_id}"
}

#
# ECS container instance security group resources
#
resource "aws_security_group_rule" "app_https_egress" {
  type             = "egress"
  from_port        = 443
  to_port          = 443
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]

  security_group_id = "${aws_security_group.app.id}"
}

resource "aws_security_group_rule" "app_rds_enc_egress" {
  type      = "egress"
  from_port = "${module.database_enc.port}"
  to_port   = "${module.database_enc.port}"
  protocol  = "tcp"

  security_group_id        = "${aws_security_group.app.id}"
  source_security_group_id = "${module.database_enc.database_security_group_id}"
}

resource "aws_security_group_rule" "app_alb_ingress" {
  type      = "ingress"
  from_port = "${var.app_port}"
  to_port   = "${var.app_port}"
  protocol  = "tcp"

  security_group_id        = "${aws_security_group.app.id}"
  source_security_group_id = "${aws_security_group.alb.id}"
}

resource "aws_security_group_rule" "app_bastion_ingress" {
  type      = "ingress"
  from_port = "${var.app_port}"
  to_port   = "${var.app_port}"
  protocol  = "tcp"

  security_group_id        = "${aws_security_group.app.id}"
  source_security_group_id = "${module.vpc.bastion_security_group_id}"
}

#
# Batch container instance security group resources
#
resource "aws_security_group_rule" "batch_https_egress" {
  type        = "egress"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = "${aws_security_group.batch.id}"
}

resource "aws_security_group_rule" "batch_rds_enc_egress" {
  type      = "egress"
  from_port = "${module.database_enc.port}"
  to_port   = "${module.database_enc.port}"
  protocol  = "tcp"

  security_group_id        = "${aws_security_group.batch.id}"
  source_security_group_id = "${module.database_enc.database_security_group_id}"
}

resource "aws_security_group_rule" "batch_bastion_ingress" {
  type      = "ingress"
  from_port = 22
  to_port   = 22
  protocol  = "tcp"

  security_group_id        = "${aws_security_group.batch.id}"
  source_security_group_id = "${module.vpc.bastion_security_group_id}"
}
