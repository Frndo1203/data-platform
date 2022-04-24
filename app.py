#!/usr/bin/env python3
from aws_cdk import core
from data_platform.data_lake.stack import DataLakeStack
from data_platform.data_platform_stack import DataPlatformStack
from data_platform.dms.stack import DmsStack

app = core.App()
data_lake = DataLakeStack(app)
data_platform = DataPlatformStack(app)
dms = DmsStack(app, common_stack=DataPlatformStack, 
                raw_bucket=data_lake.raw_bucket)
app.synth()
