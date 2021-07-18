#/usr/bin/env python3
import boto3

# 64-bit Amazon Linux 2
AMAZON_LINUX_AMI = "ami-0233c2d874b811deb"

# Free tier
SMALLEST_INSTANCE_TYPE = "t2.micro"

# us-east-1 is us-fail-1
# Reminder to self: GCP is us-east1, AWS is us-east-1
REGION = "us-east-2"


def turnup_sample_instance():
    pass


if __name__ == "__main__":
    turnup_sample_instance()
