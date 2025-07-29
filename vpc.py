import pulumi
from pulumi import Input
from typing import Optional, Dict, TypedDict, Any
import pulumi_aws as aws

class VpcArgs(TypedDict, total=False):
    vpcCidr: Input[Any]
    pubSubNat1: Input[Any]
    pubSubNat2: Input[Any]
    privSubWeb1: Input[Any]
    privSubWeb2: Input[Any]
    privSubDb1: Input[Any]
    privSubDb2: Input[Any]
    projectName: Input[Any]
    awsRegion: Input[Any]

class Vpc(pulumi.ComponentResource):
    def __init__(self, name: str, args: VpcArgs, opts:Optional[pulumi.ResourceOptions] = None):
        super().__init__("components:index:Vpc", name, args, opts)

        #vpc
        vpc = aws.ec2.Vpc(f"{name}-vpc",
            cidr_block=args["vpcCidr"],
            instance_tenancy="default",
            enable_dns_hostnames=True,
            enable_dns_support=True,
            tags={
                "Name": f"{args["projectName"]}-vpc",
            },
            opts = pulumi.ResourceOptions(parent=self))

        #internet gateway 
        internet_gateway = aws.ec2.InternetGateway(
            f"{name}-internet_gateway",
            vpc_id=vpc.id,
            tags={
                "Name": f"{args["projectName"]}-igw",
            },
            opts=pulumi.ResourceOptions(parent=self),
        )

        #available zones
        available_zones = aws.get_availability_zones_output()

        #public subnet pub_sub_nat_1
        pub_sub_nat1_subnet = aws.ec2.Subnet(f"{name}-pub_sub_nat_1",
            vpc_id=vpc.id,
            cidr_block=args["pubSubNat1"],
            availability_zone=available_zones.names[0],
            map_public_ip_on_launch=True,
            tags={
                "Name": "pub_sub_nat_1",
            },
            opts = pulumi.ResourceOptions(parent=self))

        #public subnet pub_sub_nat_2
        pub_sub_nat2_subnet = aws.ec2.Subnet(f"{name}-pub_sub_nat_2",
            vpc_id=vpc.id,
            cidr_block=args["pubSubNat2"],
            availability_zone=available_zones.names[1],
            map_public_ip_on_launch=True,
            tags={
                "Name": "pub_sub_nat_2",
            },
            opts = pulumi.ResourceOptions(parent=self))

        #route table and public route
        public_route_table = aws.ec2.RouteTable(f"{name}-public_route_table",
            vpc_id=vpc.id,
            routes=[{
                "cidr_block": "0.0.0.0/0",
                "gateway_id": internet_gateway.id,
            }],
            tags={
                "Name": "public_route_table",
            },
            opts = pulumi.ResourceOptions(parent=self))

        # connect public subnet pub_sub_nat_1 to public route table
        pb1a_rt_connection = aws.ec2.RouteTableAssociation(f"{name}-pb1a_rt_connection",
            subnet_id=pub_sub_nat1_subnet.id,
            route_table_id=public_route_table.id,
            opts = pulumi.ResourceOptions(parent=self))

        # connect public subnet pub_sub_nat_2 to public route table
        pb2b_rt_connection = aws.ec2.RouteTableAssociation(f"{name}-pb2b_rt_connection",
            subnet_id=pub_sub_nat2_subnet.id,
            route_table_id=public_route_table.id,
            opts = pulumi.ResourceOptions(parent=self))

        # private subnet priv_sub_web_1
        priv_sub_web1_subnet = aws.ec2.Subnet(f"{name}-priv_sub_web_1",
            vpc_id=vpc.id,
            cidr_block=args["privSubWeb1"],
            availability_zone=available_zones.names[0],
            map_public_ip_on_launch=False,
            tags={
                "Name": "priv_sub_web_1",
            },
            opts = pulumi.ResourceOptions(parent=self))

        # private subnet priv_sub_web_2
        priv_sub_web2_subnet = aws.ec2.Subnet(f"{name}-priv_sub_web_2",
            vpc_id=vpc.id,
            cidr_block=args["privSubWeb2"],
            availability_zone=available_zones.names[1],
            map_public_ip_on_launch=False,
            tags={
                "Name": "priv_sub_web_2",
            },
            opts = pulumi.ResourceOptions(parent=self))

        # private subnet priv_sub_db_1
        priv_sub_db1_subnet = aws.ec2.Subnet(f"{name}-priv_sub_db_1",
            vpc_id=vpc.id,
            cidr_block=args["privSubDb1"],
            availability_zone=available_zones.names[0],
            map_public_ip_on_launch=False,
            tags={
                "Name": "priv_sub_db_1",
            },
            opts = pulumi.ResourceOptions(parent=self))

        # private subnet priv_sub_db_2
        priv_sub_db2_subnet = aws.ec2.Subnet(f"{name}-priv_sub_db_2",
            vpc_id=vpc.id,
            cidr_block=args["privSubDb2"],
            availability_zone=available_zones.names[1],
            map_public_ip_on_launch=False,
            tags={
                "Name": "priv_sub_db_2",
            },
            opts = pulumi.ResourceOptions(parent=self))

        self.projectName = args["projectName"]
        self.awsRegion = args["awsRegion"]
        self.igwId = internet_gateway.id
        self.vpcId = vpc.id
        self.pubSubNat1Id = pub_sub_nat1_subnet.id
        self.pubSubNat2Id = pub_sub_nat2_subnet.id
        self.privSubWeb1Id = priv_sub_web1_subnet.id
        self.privSubWeb2Id = priv_sub_web2_subnet.id
        self.privSubDb1Id = priv_sub_db1_subnet.id
        self.privSubDb2Id = priv_sub_db2_subnet.id
        self.register_outputs({
            'projectName': args["projectName"], 
            'awsRegion': args["awsRegion"], 
            'igwId': internet_gateway.id, 
            'vpcId': vpc.id, 
            'pubSubNat1Id': pub_sub_nat1_subnet.id, 
            'pubSubNat2Id': pub_sub_nat2_subnet.id, 
            'privSubWeb1Id': priv_sub_web1_subnet.id, 
            'privSubWeb2Id': priv_sub_web2_subnet.id, 
            'privSubDb1Id': priv_sub_db1_subnet.id, 
            'privSubDb2Id': priv_sub_db2_subnet.id
        })