import boto3
from datetime import datetime, timedelta

ec2 = boto3.client('ec2')
rds = boto3.client('rds')
lambda_client = boto3.client('lambda')
cloudwatch = boto3.client('cloudwatch')
s3 = boto3.client('s3')

print("===== AWS COST OPTIMIZATION REPORT =====\n")

# -----------------------------------------
# 1. EC2 Instances with Low CPU Utilization
# -----------------------------------------

print("Low CPU EC2 Instances (<10% CPU last 30 days):")

instances = ec2.describe_instances()

end = datetime.utcnow()
start = end - timedelta(days=30)

for reservation in instances['Reservations']:
    for instance in reservation['Instances']:

        instance_id = instance['InstanceId']

        metrics = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {'Name': 'InstanceId', 'Value': instance_id}
            ],
            StartTime=start,
            EndTime=end,
            Period=86400,
            Statistics=['Average']
        )

        datapoints = metrics['Datapoints']

        if datapoints:
            avg_cpu = sum(d['Average'] for d in datapoints) / len(datapoints)

            if avg_cpu < 10:
                print(f"Instance: {instance_id} | Avg CPU: {avg_cpu:.2f}%")

print("\n")


# -----------------------------------------
# 2. RDS Idle Databases
# -----------------------------------------

print("Idle RDS Instances (Low Connections):")

dbs = rds.describe_db_instances()

for db in dbs['DBInstances']:

    db_id = db['DBInstanceIdentifier']

    metrics = cloudwatch.get_metric_statistics(
        Namespace='AWS/RDS',
        MetricName='DatabaseConnections',
        Dimensions=[
            {'Name': 'DBInstanceIdentifier', 'Value': db_id}
        ],
        StartTime=datetime.utcnow() - timedelta(days=7),
        EndTime=datetime.utcnow(),
        Period=86400,
        Statistics=['Average']
    )

    datapoints = metrics['Datapoints']

    if datapoints:
        avg_conn = sum(d['Average'] for d in datapoints) / len(datapoints)

        if avg_conn < 1:
            print(f"Idle RDS Instance: {db_id}")

print("\n")


# -----------------------------------------
# 3. Lambda Functions Not Used in 30 Days
# -----------------------------------------

print("Unused Lambda Functions (No Invocations in 30 days):")

functions = lambda_client.list_functions()

for function in functions['Functions']:

    fname = function['FunctionName']

    metrics = cloudwatch.get_metric_statistics(
        Namespace='AWS/Lambda',
        MetricName='Invocations',
        Dimensions=[
            {'Name': 'FunctionName', 'Value': fname}
        ],
        StartTime=datetime.utcnow() - timedelta(days=30),
        EndTime=datetime.utcnow(),
        Period=86400,
        Statistics=['Sum']
    )

    datapoints = metrics['Datapoints']

    total_invocations = sum(d['Sum'] for d in datapoints)

    if total_invocations == 0:
        print(f"Unused Lambda: {fname}")

print("\n")


# -----------------------------------------
# 4. Unused / Empty S3 Buckets
# -----------------------------------------

print("Unused or Empty S3 Buckets:")

buckets = s3.list_buckets()

for bucket in buckets['Buckets']:

    bucket_name = bucket['Name']

    objects = s3.list_objects_v2(Bucket=bucket_name)

    if 'Contents' not in objects:
        print(f"Empty Bucket: {bucket_name}")

print("\n")

print("===== END OF REPORT =====")