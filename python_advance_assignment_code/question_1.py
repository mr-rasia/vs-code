import boto3
import csv

# Get EC2 client
ec2 = boto3.client('ec2')

# Get list of all regions
regions_response = ec2.describe_regions()
regions = [region['RegionName'] for region in regions_response['Regions']]

data = []

# Loop through each region
for region in regions:

    print("Scanning region:", region)

    regional_ec2 = boto3.client('ec2', region_name=region)

    instance_types = set()

    paginator = regional_ec2.get_paginator('describe_instance_types')

    for page in paginator.paginate():
        for instance in page['InstanceTypes']:
            instance_types.add(instance['InstanceType'])

    for itype in sorted(instance_types):
        data.append([region, itype])

# Write to CSV
with open('ec2_instance_types.csv', 'w', newline='') as file:

    writer = csv.writer(file)

    writer.writerow(['region', 'instance_type'])

    writer.writerows(data)

print("CSV file created: ec2_instance_types.csv")