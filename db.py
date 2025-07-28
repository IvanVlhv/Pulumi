import pulumi
from pulumi import Input
from typing import Optional, Dict, TypedDict, Any
import pulumi_aws as aws

class DbArgs(TypedDict, total=False):
    projectName: Input[Any]
    privSubDb1: Input[Any]
    privSubDb2: Input[Any]
    dbUsername: Input[Any]
    dbPassword: Input[Any]
    dbSecGroupId: Input[Any]

class Db(pulumi.ComponentResource):
    def __init__(self, name: str, args: DbArgs, opts:Optional[pulumi.ResourceOptions] = None):
        super().__init__("components:index:Db", name, args, opts)

        db_subnet_group = aws.rds.SubnetGroup(f"{name}-db_subnet_group",
            name="db-subnet-group",
            subnet_ids=[
                args["privSubDb1"],
                args["privSubDb2"],
            ],
            opts = pulumi.ResourceOptions(parent=self))

        db = aws.rds.Instance(f"{name}-db",
            identifier="zavrsni-db",
            engine="mysql",
            engine_version="8.0",
            instance_class=aws.rds.InstanceType.T3_MICRO,
            allocated_storage=20,
            username=args["dbUsername"],
            password=args["dbPassword"],
            db_subnet_group_name=db_subnet_group.name,
            vpc_security_group_ids=[args["dbSecGroupId"]],
            skip_final_snapshot=True,
            opts = pulumi.ResourceOptions(parent=self))

        self.dbEndpoint = db.endpoint
        self.register_outputs({
            'dbEndpoint': db.endpoint
        })