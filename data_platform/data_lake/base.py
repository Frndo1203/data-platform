from enum import Enum #get env
from aws_cdk import core
from aws_cdk import (
    aws_s3 as s3,
)

class DataLakeLayer(Enum):
    """
    Enum for the different data lake layers
    """

    RAW = 'raw'
    PROCESSED = 'processed'
    AGGREGATED = 'aggregated'


class BaseDataLakeBucket(s3.Bucket):
    """
    Base class for all data lake buckets
    """

    def __init__(self, scope: core.Construct, deploy_env: str, layer: DataLakeLayer, **kwargs) -> None:
        self.layer = layer
        self.deploy_env = deploy_env
        self.obj_name = f's3-fernando-{deploy_env}-datalake-{layer.value}'
    
        super().__init__( 
            scope, 
            id = self.obj_name,
            bucket_name = self.obj_name,
            block_public_access=self.default_block_public_access,
            encryption=self.default_encryption,
            versioned=True,
            **kwargs
            )
        
        self.set_default_lifecycle_rules()
  
    @property
    def default_block_public_access(self):
        """
        Default block public access
        """
        return s3.BlockPublicAccess.BLOCK_ALL
    
    @property
    def default_encryption(self):
        """
        Default encryption
        """
        return s3.BucketEncryption.S3_MANAGED
    
    def set_default_lifecycle_rules(self):
        """
        Set default lifecycle rules
        """
        self.add_lifecycle_rule(
            abort_incomplete_multipart_upload_after=core.Duration.days(7),
            enabled=True
            )
        
        self.add_lifecycle_rule(
            noncurrent_version_transitions=[
                s3.NoncurrentVersionTransition(
                    storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                    transition_after=core.Duration.days(30)
                ),
                s3.NoncurrentVersionTransition(
                    storage_class=s3.StorageClass.GLACIER,
                    transition_after=core.Duration.days(60)
                )
            ]
        )

        self.add_lifecycle_rule(
            noncurrent_version_expiration=core.Duration.days(360)
        )
        