import pulumi
from pulumi import Input
from typing import Optional, Dict, TypedDict, Any
import pulumi_aws as aws

class SecGroupArgs(TypedDict, total=False):
    vpcId: Input[Any]

class SecGroup(pulumi.ComponentResource):
    def __init__(self, name: str, args: SecGroupArgs, opts:Optional[pulumi.ResourceOptions] = None):
        super().__init__("components:index:SecGroup", name, args, opts)

        #sec groups
        alb_sec_group = aws.ec2.SecurityGroup(f"{name}-alb_sec_group",
            name="alb_security_group",
            vpc_id=args["vpcId"],
            opts = pulumi.ResourceOptions(parent=self))

        web_sec_group = aws.ec2.SecurityGroup(f"{name}-web_sec_group",
            name="web_security_group",
            vpc_id=args["vpcId"],
            opts = pulumi.ResourceOptions(parent=self))

        db_sec_group = aws.ec2.SecurityGroup(f"{name}-db_sec_group",
            name="db_security_group",
            vpc_id=args["vpcId"],
            opts = pulumi.ResourceOptions(parent=self))

        alb_http = aws.vpc.SecurityGroupIngressRule(f"{name}-alb_http",
            security_group_id=alb_sec_group.id,
            from_port=80,
            to_port=80,
            ip_protocol="tcp",
            cidr_ipv4="0.0.0.0/0",
            description="Allow HTTP from Internet to ALB",
            opts = pulumi.ResourceOptions(parent=self))

        alb_https = aws.vpc.SecurityGroupIngressRule(f"{name}-alb_https",
            security_group_id=alb_sec_group.id,
            from_port=443,
            to_port=443,
            ip_protocol="tcp",
            cidr_ipv4="0.0.0.0/0",
            description="Allow HTTPS from Internet to ALB",
            opts = pulumi.ResourceOptions(parent=self))

        web_http = aws.vpc.SecurityGroupIngressRule(f"{name}-web_http",
            security_group_id=web_sec_group.id,
            from_port=80,
            to_port=80,
            ip_protocol="tcp",
            referenced_security_group_id=alb_sec_group.id,
            description="Allow HTTP from ALB to Web Servers",
            opts = pulumi.ResourceOptions(parent=self))

        db_mysql = aws.vpc.SecurityGroupIngressRule(f"{name}-db_mysql",
            security_group_id=db_sec_group.id,
            from_port=3306,
            to_port=3306,
            ip_protocol="tcp",
            referenced_security_group_id=web_sec_group.id,
            description="Allow MySQL from Web Servers to DB",
            opts = pulumi.ResourceOptions(parent=self))

        # Egress rules using aws_vpc_security_group_egress_rule:
        alb_egress = aws.vpc.SecurityGroupEgressRule(f"{name}-alb_egress",
            security_group_id=alb_sec_group.id,
            from_port=0,
            to_port=0,
            ip_protocol="-1",
            cidr_ipv4="0.0.0.0/0",
            description="Allow all outbound from ALB",
            opts = pulumi.ResourceOptions(parent=self))

        web_egress = aws.vpc.SecurityGroupEgressRule(f"{name}-web_egress",
            security_group_id=web_sec_group.id,
            from_port=0,
            to_port=0,
            ip_protocol="-1",
            cidr_ipv4="0.0.0.0/0",
            description="Allow all outbound from Web Servers",
            opts = pulumi.ResourceOptions(parent=self))

        db_egress = aws.vpc.SecurityGroupEgressRule(f"{name}-db_egress",
            security_group_id=db_sec_group.id,
            from_port=0,
            to_port=0,
            ip_protocol="-1",
            cidr_ipv4="0.0.0.0/0",
            description="Allow all outbound from DB",
            opts = pulumi.ResourceOptions(parent=self))

        self.albSecGroupId = alb_sec_group.id
        self.webSecGroupId = web_sec_group.id
        self.dbSecGroupId = db_sec_group.id
        self.register_outputs({
            'albSecGroupId': alb_sec_group.id, 
            'webSecGroupId': web_sec_group.id, 
            'dbSecGroupId': db_sec_group.id
        })