#!/usr/bin/env python3
from aws_cdk import core
from data_platform.data_lake.stack import DataLakeStack
from data_platform.data_platform_stack import DataPlatformStack

app = core.App()
data_lake = DataLakeStack(app)
data_platform = DataPlatformStack(app)
app.synth()
