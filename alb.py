import pulumi
from pulumi import Input
from typing import Optional, Dict, TypedDict, Any
import pulumi_aws as aws

class AlbArgs(TypedDict, total=False):
    projectName: Input[Any]
    pubSubNat1: Input[Any]
    pubSubNat2: Input[Any]
    vpcId: Input[Any]
    albSecGroupId: Input[Any]

class Alb(pulumi.ComponentResource):
    def __init__(self, name: str, args: AlbArgs, opts:Optional[pulumi.ResourceOptions] = None):
        super().__init__("components:index:Alb", name, args, opts)

        # create application load balancer
        alb = aws.lb.LoadBalancer(f"{name}-alb",
            name=f"{args["projectName"]}-alb",
            internal=False,
            load_balancer_type="application",
            security_groups=[args["albSecGroupId"]],
            subnets=[
                args["pubSubNat1"],
                args["pubSubNat2"],
            ],
            enable_deletion_protection=False,
            tags={
                "Name": f"{args["projectName"]}-alb",
            },
            opts = pulumi.ResourceOptions(parent=self))

        # create target group for load balancer
        alb_target = aws.lb.TargetGroup(f"{name}-alb_target",
            name=f"{args["projectName"]}-tg",
            port=80,
            protocol="HTTP",
            vpc_id=args["vpcId"],
            health_check={
                "path": "/",
                "protocol": "HTTP",
                "matcher": "200-399",
                "interval": 30,
                "timeout": 5,
                "healthy_threshold": 5,
                "unhealthy_threshold": 2,
            },
            opts = pulumi.ResourceOptions(parent=self))

        # create listener
        alb_listener = aws.lb.Listener(f"{name}-alb_listener",
            load_balancer_arn=alb.arn,
            port=80,
            protocol="HTTP",
            default_actions=[{
                "type": "forward",
                "target_group_arn": alb_target.arn,
            }],
            opts = pulumi.ResourceOptions(parent=self))

        self.targetGroupArn = alb_target.arn
        self.albDns = alb.dns_name
        self.albZoneId = alb.zone_id
        self.register_outputs({
            'targetGroupArn': alb_target.arn, 
            'albDns': alb.dns_name, 
            'albZoneId': alb.zone_id
        })