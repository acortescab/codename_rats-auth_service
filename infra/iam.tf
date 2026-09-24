data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ec2_role" {
  count = var.enable_iam_instance_profile ? 1 : 0

  name               = "${var.instance_name}-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json

  tags = merge(
    {
      Name        = "${var.instance_name}-role"
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "terraform"
    },
    var.extra_tags,
  )
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  count = var.enable_iam_instance_profile ? 1 : 0

  role       = aws_iam_role.ec2_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  count = var.enable_iam_instance_profile ? 1 : 0

  name = "${var.instance_name}-profile"
  role = aws_iam_role.ec2_role[0].name

  tags = merge(
    {
      Name        = "${var.instance_name}-profile"
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "terraform"
    },
    var.extra_tags,
  )
}
