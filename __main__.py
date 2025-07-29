import os
import pulumi

from alb import Alb
from db import Db
from nat import Nat
from sec_group import SecGroup
from vpc import Vpc
from web import Web
import base64

module_path = os.path.dirname(os.path.abspath(__file__))

config = pulumi.Config()
project_name = config.require("projectName")
aws_region = config.require("awsRegion")
vpc_cidr = config.require("vpcCidr")
pub_sub_nat1 = config.require("pubSubNat1")
pub_sub_nat2 = config.require("pubSubNat2")
priv_sub_web1 = config.require("privSubWeb1")
priv_sub_web2 = config.require("privSubWeb2")
priv_sub_db1 = config.require("privSubDb1")
priv_sub_db2 = config.require("privSubDb2")
db_username = config.require("dbUsername")
db_password = config.require_secret("dbPassword")
wweb_instance_type = config.require("webInstanceType")
key_name = config.require("keyName")

vpc = Vpc(
    "vpc",
    {
        "awsRegion": aws_region,
        "projectName": project_name,
        "vpcCidr": vpc_cidr,
        "pubSubNat1": pub_sub_nat1,
        "pubSubNat2": pub_sub_nat2,
        "privSubWeb1": priv_sub_web1,
        "privSubWeb2": priv_sub_web2,
        "privSubDb1": priv_sub_db1,
        "privSubDb2": priv_sub_db2,
    },
)
nat = Nat(
    "nat",
    {
        "igwId": vpc.igwId,
        "vpcId": vpc.vpcId,
        "pubSubNat1": vpc.pubSubNat1Id,
        "pubSubNat2": vpc.pubSubNat2Id,
        "privSubWeb1": vpc.privSubWeb1Id,
        "privSubWeb2": vpc.privSubWeb2Id,
        "privSubDb1": vpc.privSubDb1Id,
        "privSubDb2": vpc.privSubDb2Id,
    },
)
sec_group = SecGroup("secGroup", {"vpcId": vpc.vpcId})
alb = Alb(
    "alb",
    {
        "projectName": vpc.projectName,
        "vpcId": vpc.vpcId,
        "albSecGroupId": sec_group.albSecGroupId,
        "pubSubNat1": vpc.pubSubNat1Id,
        "pubSubNat2": vpc.pubSubNat2Id,
    },
)

user_data_file = os.path.join(module_path, "install_snakegame.sh")

web = Web(
    "web",
    {
        "projectName": vpc.projectName,
        "webSecGroupId": sec_group.webSecGroupId,
        "privSubWeb1": vpc.privSubWeb1Id,
        "privSubWeb2": vpc.privSubWeb2Id,
        "targetGroupArn": alb.targetGroupArn,
        "instanceType": web_instance_type,
        "keyName": key_name,
        "userData": base64.b64encode(open(user_data_file, "rb").read()).decode(),
    },
)
db = Db(
    "db",
    {
        "projectName": vpc.projectName,
        "dbUsername": db_username,
        "dbPassword": db_password,
        "dbSecGroupId": sec_group.dbSecGroupId,
        "privSubDb1": vpc.privSubDb1Id,
        "privSubDb2": vpc.privSubDb2Id,
    },
)
pulumi.export("albDns", alb.albDns)

