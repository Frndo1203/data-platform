import os

from aws_cdk import core
from aws_cdk import(
    aws_s3 as s3,
)

from data_platform.data_lake.base import (
    BaseDataLakeBucket, DataLakeLayer
)

from data_platform import active_environment


class DataLakeStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, deploy_env: Environment, **kwargs) -> None:
        self.deploy_env = deploy_env
        
        super().__init__(
            scope,
            id=f'{self.deploy_env.value}-datalake-stack', 
            **kwargs
            )
    
        self.raw_bucket = BaseDataLakeBucket(
            self,
            deploy_env=self.deploy_env,
            layer=DataLakeLayer.RAW
            )
        
        self.raw_bucket.add_lifecycle_rule(
            transitions=[
                s3.transition(
                    storage_class=s3.StorageClass.INTELLIGENT_TIERING,
                    transition_after=core.Duration.days(90)
                ),
                s3.transition(
                    storage_class=s3.StorageClass.GLACIER,
                    transition_after=core.Duration.days(360)
                )
            ]
        )

        #DataLakeLayer.PROCESSED
        self.processed_bucket = BaseDataLakeBucket(
            self,
            deploy_env=self.deploy_env,
            layer=DataLakeLayer.PROCESSED
        )

        #DataLakeLayer.AGGREGATED
        self.aggregated_bucket = BaseDataLakeBucket(
            self,
            deploy_env=self.deploy_env,
            layer=DataLakeLayer.AGGREGATED
        )
        