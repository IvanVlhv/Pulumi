import pulumi
from pulumi import Input
from typing import Optional, Dict, TypedDict, Any
import pulumi_aws as aws

class WebArgs(TypedDict, total=False):
    projectName: Input[Any]
    webSecGroupId: Input[Any]
    privSubWeb1: Input[Any]
    privSubWeb2: Input[Any]
    targetGroupArn: Input[Any]
    instanceType: Input[Any]
    keyName: Input[Any]
    userData: Input[Any]
    minSize: Input[float]
    maxSize: Input[float]
    desiredCapacity: Input[float]
    cpuTarget: Input[float]

class Web(pulumi.ComponentResource):
    def __init__(self, name: str, args: WebArgs, opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("components:index:Web", name, args, opts)

        # fetch latest amazon linux ami
        amazon_linux = aws.ec2.get_ami_output(most_recent=True,
            owners=["amazon"],
            filters=[{
                "name": "name",
                "values": ["amzn2-ami-hvm-*-x86_64-gp2"],
            }])

        assume_role = aws.iam.get_policy_document_output(statements=[{
            "effect": "Allow",
            "actions": ["sts:AssumeRole"],
            "principals": [{
                "type": "Service",
                "identifiers": ["ec2.amazonaws.com"],
            }],
        }])

        ssm_role = aws.iam.Role(f"{name}-ssm_role",
            name=f"{args["projectName"]}-ssm-role",
            assume_role_policy=assume_role.json,
            opts = pulumi.ResourceOptions(parent=self))

        ssm_core = aws.iam.RolePolicyAttachment(f"{name}-ssm_core",
            role=ssm_role.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
            opts = pulumi.ResourceOptions(parent=self))

        ssm_instance_profile = aws.iam.InstanceProfile(f"{name}-ssm_instance_profile",
            name=f"{args["projectName"]}-ssm-instance-profile",
            role=ssm_role.name,
            opts = pulumi.ResourceOptions(parent=self))

        # launch template for autoscaling group
        web = aws.ec2.LaunchTemplate(f"{name}-web",
            name_prefix=f"{args["projectName"]}-launch-template",
            image_id=amazon_linux.id,
            instance_type=args["instanceType"],
            key_name=args["keyName"],
            vpc_security_group_ids=[args["webSecGroupId"]],
            user_data=args["userData"],
            iam_instance_profile={
                "name": ssm_instance_profile.name,
            },
            opts = pulumi.ResourceOptions(parent=self))
        # Determine autoscaling configuration with sane defaults if values are
        # not provided via the component arguments.
        desired_capacity = args.get("desiredCapacity", 1)
        min_size = args.get("minSize", desired_capacity)
        max_size = args.get("maxSize", max(min_size, desired_capacity))

        # autoscaling group for web instances
        web_asg = aws.autoscaling.Group(f"{name}-web_asg",
            name_prefix=f"{args["projectName"]}-asg",
            desired_capacity=desired_capacity,
            min_size=min_size,
            max_size=max_size,
            vpc_zone_identifiers=[
                args["privSubWeb1"],
                args["privSubWeb2"],
            ],
            target_group_arns=[args["targetGroupArn"]],
            launch_template={
                "id": web.id,
                "version": "$Latest",
            },
            tags=[{
                "key": "Name",
                "value": f"{args["projectName"]}-web",
                "propagate_at_launch": True,
            }],
            opts = pulumi.ResourceOptions(parent=self))

        # tracking policy based on average CPU utilization
        cpu_target = args.get("cpuTarget", 50)
        cpu_target_policy = aws.autoscaling.Policy(f"{name}-cpu_target",
            name=f"{args["projectName"]}-cpu-policy",
            autoscaling_group_name=web_asg.name,
            policy_type="TargetTrackingScaling",
            target_tracking_configuration={
                "predefined_metric_specification": {
                    "predefined_metric_type": "ASGAverageCPUUtilization",
                },
                "target_value": cpu_target,
            },
            opts = pulumi.ResourceOptions(parent=self))

        self.autoscalingGroupName = web_asg.name
        self.register_outputs({
            'autoscalingGroupName': web_asg.name
        })