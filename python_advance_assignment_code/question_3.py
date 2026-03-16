import boto3

# Create EC2 client
ec2 = boto3.client('ec2')

# Get all AWS regions
regions_response = ec2.describe_regions()
regions = [region['RegionName'] for region in regions_response['Regions']]

active_regions = []

# Check resources in each region
for region in regions:

    print("Checking region:", region)

    regional_ec2 = boto3.client('ec2', region_name=region)

    response = regional_ec2.describe_instances()

    instances = []

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])

    if len(instances) > 0:
        active_regions.append(region)

# Print regions with resources
print("\nRegions where customer has resources:\n")

for r in active_regions:
    print(r)