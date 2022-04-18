import os

from aws_cdk import (
    core,
    aws_rds as rds,
    aws_ec2 as ec2
)


class DataPlatformStack(core.Stack):
    """
        docstring for DataPlatformStack
    """
    def __init__(self, scope: core.Construct, **kwargs) -> None:
        self.deploy_env = os.environ["ENVIRONMENT"]
        super().__init__(
            scope,
            id=f'{self.deploy_env}-data-platform-stack',
            **kwargs)

        self.custom_vpc = ec2.Vpc(self, f"vpc-{self.deploy_env}")

        self.orders_rds_sg = ec2.SecurityGroup(
            self,
            f"orders-rds-sg-{self.deploy_env}",
            vpc=self.custom_vpc,
            allow_all_outbound=True,
            security_group_name=f"orders-rds-sg-{self.deploy_env}"
        )

        self.orders_rds_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4("0.0.0.0/0"),
            connection=ec2.Port.tcp(5432)
        )

        for subnet in self.custom_vpc.public_subnets:
            self.orders_rds_sg.add_ingress_rule(
                peer=ec2.Peer.ipv4(subnet.ipv4_cidr_block),
                connection=ec2.Port.tcp(5432)
            )

        self.orders_rds_parameter_group= rds.ParameterGroup(
            self,
            f"orders-rds-pg-{self.deploy_env}",
            description="Orders RDS Parameter Group to allow CDC from RDS using DMG",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_12_4
            ),
            parameters={"rds.logical_replication": "1",
                        "wal_sender_timeout": "0"}
        )

        self.orders_rds = rds.DatabaseInstance(
            self,
            f"orders-rds-{self.deploy_env}",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_12_4
            ),
            database_name="orders",
            instance_type=ec2.InstanceType("t3.micro"),
            vpc=self.custom_vpc,
            instance_identifier=f"orders-rds-{self.deploy_env}-db",
            port=5432,
            vpc_placement=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            subnet_group=rds.SubnetGroup(
                self,
                f"rds-{self.deploy_env}-subnet",
                description="place RDS on public subnet",
                vpc=self.custom_vpc,
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            ),
            parameter_group=self.orders_rds_parameter_group,
            security_groups=[self.orders_rds_sg],
            removal_policy=core.RemovalPolicy.DESTROY,
            **kwargs
        )

