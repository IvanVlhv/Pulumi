import pulumi
from alb import Alb
from db import Db
from nat import Nat
from sec_group import SecGroup
from vpc import Vpc
from web import Web
import pulumi_std as std


def not_implemented(msg):
    raise NotImplementedError(msg)

config = pulumi.Config()
project_name = config.require_object("projectName")
aws_region = config.require_object("awsRegion")
vpc_cidr = config.require_object("vpcCidr")
pub_sub_nat1 = config.require_object("pubSubNat1")
pub_sub_nat2 = config.require_object("pubSubNat2")
priv_sub_web1 = config.require_object("privSubWeb1")
priv_sub_web2 = config.require_object("privSubWeb2")
priv_sub_db1 = config.require_object("privSubDb1")
priv_sub_db2 = config.require_object("privSubDb2")
db_username = config.require_object("dbUsername")
db_password = config.require_object("dbPassword")
web_instance_type = config.require_object("webInstanceType")
key_name = config.require_object("keyName")
vpc = Vpc("vpc", {
    'awsRegion': aws_region, 
    'projectName': project_name, 
    'vpcCidr': vpc_cidr, 
    'pubSubNat1': pub_sub_nat1, 
    'pubSubNat2': pub_sub_nat2, 
    'privSubWeb1': priv_sub_web1, 
    'privSubWeb2': priv_sub_web2, 
    'privSubDb1': priv_sub_db1, 
    'privSubDb2': priv_sub_db2})
nat = Nat("nat", {
    'igwId': vpc.igw_id, 
    'vpcId': vpc.vpc_id, 
    'pubSubNat1': vpc.pub_sub_nat1_id, 
    'pubSubNat2': vpc.pub_sub_nat2_id, 
    'privSubWeb1': vpc.priv_sub_web1_id, 
    'privSubWeb2': vpc.priv_sub_web2_id, 
    'privSubDb1': vpc.priv_sub_db1_id, 
    'privSubDb2': vpc.priv_sub_db2_id})
sec_group = SecGroup("secGroup", {
    'vpcId': vpc.vpc_id})
alb = Alb("alb", {
    'projectName': vpc.project_name, 
    'vpcId': vpc.vpc_id, 
    'albSecGroupId': sec_group.alb_sec_group_id, 
    'pubSubNat1': vpc.pub_sub_nat1_id, 
    'pubSubNat2': vpc.pub_sub_nat2_id})
web = Web("web", {
    'projectName': vpc.project_name, 
    'webSecGroupId': sec_group.web_sec_group_id, 
    'privSubWeb1': vpc.priv_sub_web1_id, 
    'privSubWeb2': vpc.priv_sub_web2_id, 
    'targetGroupArn': alb.target_group_arn, 
    'instanceType': web_instance_type, 
    'keyName': key_name, 
    'userData': std.index.filebase64(input=f"{not_implemented('path.module')}/install_snakegame.sh")["result"]})
db = Db("db", {
    'projectName': vpc.project_name, 
    'dbUsername': db_username, 
    'dbPassword': db_password, 
    'dbSecGroupId': sec_group.db_sec_group_id, 
    'privSubDb1': vpc.priv_sub_db1_id, 
    'privSubDb2': vpc.priv_sub_db2_id})
pulumi.export("albDns", alb.alb_dns)
