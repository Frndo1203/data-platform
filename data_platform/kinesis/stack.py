import os

from aws_cdk import core
from aws_cdk import (
    aws_kinesisfirehose as firehose,
    aws_iam as iam,
)
from data_platform.data_lake.base import BaseDataLakeBucket


class RawFirehoseRole(iam.Role):
    def __init__(
        self, 
        scope: core.Construct,
        data_lake_raw_bucket: BaseDataLakeBucket,
        **kwargs
    ) -> None:
        self.deploy_env = os.environ["ENVIRONMENT"]
        self.data_lake_raw_bucket = data_lake_raw_bucket
        super().__init__(
            scope,
            id=f"{self.deploy_env}-raw-firehose-role",
            assumed_by=iam.ServicePrincipal("firehose.amazonaws.com"),
            description=f"Role for {self.deploy_env} raw firehose",
        )
        self.add_policy()
    
    def add_policy(self):
        policy = iam.Policy(
            self,
            id=f"{self.deploy_env}-raw-firehose-policy",
            policy_name=f"{self.deploy_env}-raw-firehose-policy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "s3:AbortMultipartUpload",
                        "s3:GetBucketLocation",
                        "s3:GetObject",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                        "s3:PutObject",
                    ],
                    resources=[
                        self.data_lake_raw_bucket.bucket_arn,
                        f"{self.data_lake_raw_bucket.bucket_arn}/*",
                    ]
                )
            ]
        )
        self.attach_inline_policy(policy)

        return policy
    

class FirehoseStack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        data_lake_raw_bucket: BaseDataLakeBucket,
        **kwargs,
    ) -> None:
        self.deploy_env = os.environ["ENVIRONMENT"]
        self.data_lake_raw_bucket = data_lake_raw_bucket
        super().__init__(
            scope,
            id=f"{self.deploy_env}-firehose-stack",
            **kwargs
        )

        self.atomic_events = firehose.CfnDeliveryStream(
            self,
            id=f"{self.deploy_env}-raw-firehose-delivery-stream",
            delivery_stream_name=f"{self.deploy_env}-raw-firehose-delivery-stream",
            delivery_stream_type="DirectPut",
            extended_s3_destination_configuration=self.s3_config,
        )

    @property
    def s3_config(self):
        return firehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(
            bucket_arn=self.data_lake_raw_bucket.bucket_arn,
            compression_format="GZIP",
            error_output_prefix="bad_records",
            prefix="atomic_events/landing_date=!{timestamp:yyyy}-!{timestamp:MM}-!{timestamp:dd}/",
            buffering_hints=firehose.CfnDeliveryStream.BufferingHintsProperty(
                interval_in_seconds=60,
                size_in_m_bs=1
                ),
            role_arn=self.firehose_role.role_arn,
        )
        

    @property
    def firehose_role(self):
        return RawFirehoseRole(
            self,
            self.data_lake_raw_bucket,
            deploy_env=self.deploy_env,
        )