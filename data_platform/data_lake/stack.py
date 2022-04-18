import os

from aws_cdk import core
from aws_cdk import(
    aws_s3 as s3,
)

from data_platform.data_lake.base import (
    BaseDataLakeBucket, DataLakeLayer
)


class DataLakeStack(core.Stack):
    def __init__(self, scope: core.Construct, **kwargs) -> None:
        self.deploy_env = os.environ["ENVIRONMENT"]
        
        super().__init__(
            scope,
            id=f'{self.deploy_env}-datalake-stack', 
            **kwargs
            )
    
        self.raw_bucket = BaseDataLakeBucket(
            self,
            deploy_env=self.deploy_env,
            layer=DataLakeLayer.RAW
            )
        
        self.raw_bucket.add_lifecycle_rule(
            transitions=[
                s3.Transition(
                    storage_class=s3.StorageClass.INTELLIGENT_TIERING,
                    transition_after=core.Duration.days(90)
                ),
                s3.Transition(
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
        