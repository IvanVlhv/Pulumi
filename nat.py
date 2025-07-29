import pulumi
from pulumi import Input
from typing import Optional, Dict, TypedDict, Any
import pulumi_aws as aws

class NatArgs(TypedDict, total=False):
    igwId: Input[Any]
    vpcId: Input[Any]
    pubSubNat1: Input[Any]
    pubSubNat2: Input[Any]
    privSubWeb1: Input[Any]
    privSubWeb2: Input[Any]
    privSubDb1: Input[Any]
    privSubDb2: Input[Any]

class Nat(pulumi.ComponentResource):
    def __init__(self, name: str, args: NatArgs, opts:Optional[pulumi.ResourceOptions] = None):
        super().__init__("components:index:Nat", name, args, opts)

        # eip-nat in public subnet 1
        eip_nat1 = aws.ec2.Eip(f"{name}-eip_nat_1", tags={
            "Name": "eip_nat_1",
        },
        opts = pulumi.ResourceOptions(parent=self))

        # eip-nat in public subnet 2
        eip_nat2 = aws.ec2.Eip(f"{name}-eip_nat_2", tags={
            "Name": "eip_nat_2",
        },
        opts = pulumi.ResourceOptions(parent=self))

        # nat gateway in public subnet 1
        nat1 = aws.ec2.NatGateway(f"{name}-nat_1",
            allocation_id=eip_nat1.id,
            subnet_id=args["pubSubNat1"],
            tags={
                "Name": "nat-1",
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[args["igw"]]))

        # nat gateway in public subnet 2
        nat2 = aws.ec2.NatGateway(f"{name}-nat_2",
            allocation_id=eip_nat2.id,
            subnet_id=args["pubSubNat2"],
            tags={
                "Name": "nat-2",
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[args["igw"]]))

        # private route table 1
        private_rt1 = aws.ec2.RouteTable(f"{name}-private_rt_1",
            vpc_id=args["vpcId"],
            routes=[{
                "cidr_block": "0.0.0.0/0",
                "nat_gateway_id": nat1.id,
            }],
            tags={
                "Name": "private_rt_1",
            },
            opts = pulumi.ResourceOptions(parent=self))

        # private network for priv_sub_web_1 with route table 1
        priv_sub_web1_rt = aws.ec2.RouteTableAssociation(f"{name}-priv_sub_web_1_rt",
            subnet_id=args["privSubWeb1"],
            route_table_id=private_rt1.id,
            opts = pulumi.ResourceOptions(parent=self))

        # private network for priv_sub_web_2 with route table 1
        priv_sub_web2_rt = aws.ec2.RouteTableAssociation(f"{name}-priv_sub_web_2_rt",
            subnet_id=args["privSubWeb2"],
            route_table_id=private_rt1.id,
            opts = pulumi.ResourceOptions(parent=self))

        # private route table 2
        private_rt2 = aws.ec2.RouteTable(f"{name}-private_rt_2",
            vpc_id=args["vpcId"],
            routes=[{
                "cidr_block": "0.0.0.0/0",
                "nat_gateway_id": nat2.id,
            }],
            tags={
                "Name": "private_rt_2",
            },
            opts = pulumi.ResourceOptions(parent=self))

        # private network for priv_sub_db_1 with route table 2
        priv_sub_db1_rt = aws.ec2.RouteTableAssociation(f"{name}-priv_sub_db_1_rt",
            subnet_id=args["privSubDb1"],
            route_table_id=private_rt2.id,
            opts = pulumi.ResourceOptions(parent=self))

        # private network for priv_sub_db_2 with route table 2
        priv_sub_db2_rt = aws.ec2.RouteTableAssociation(f"{name}-priv_sub_db_2_rt",
            subnet_id=args["privSubDb2"],
            route_table_id=private_rt2.id,
            opts = pulumi.ResourceOptions(parent=self))

        self.eipNat1Id = eip_nat1.id
        self.eipNat2Id = eip_nat2.id
        self.nat1Id = nat1.id
        self.nat2Id = nat2.id
        self.privateRt1Id = private_rt1.id
        self.privateRt2Id = private_rt2.id
        self.register_outputs({
            "eipNat1Id": eip_nat1.id,
            "eipNat2Id": eip_nat2.id,
            "nat1Id": nat1.id,
            "nat2Id": nat2.id,
            "privateRt1Id": private_rt1.id,
            "privateRt2Id": private_rt2.id,
        })