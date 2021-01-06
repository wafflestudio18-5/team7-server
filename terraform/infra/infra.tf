resource "aws_key_pair" "written_admin" {
  key_name = "written_admin"
  public_key = file("~/.ssh/written_admin.pub")
}

data "aws_security_group" "written_security" {
  name = "written_security"
}

resource "aws_instance" "written_ec2" {
  ami = "ami-0a93a08544874b3b7" 
  instance_type = "t2.micro"
  key_name = aws_key_pair.written_admin.key_name
  vpc_security_group_ids = [
    data.aws_security_group.written_security.id
  ]
}

resource "aws_db_instance" "written_waffle" {
  allocated_storage = 8
  engine = "mysql"
  engine_version = "5.7"
  instance_class = "db.t2.micro"
  username = "admin"
  password = "toyproject"
  skip_final_snapshot = true
}
