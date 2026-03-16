import boto3
import csv

iam = boto3.client('iam')
ec2 = boto3.client('ec2')

# -----------------------------
# 1. Check IAM Roles with AdministratorAccess
# -----------------------------

roles = iam.list_roles()['Roles']

with open('iam_roles_admin_access.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['IAMRoleName', 'PolicyName'])

    for role in roles:
        role_name = role['RoleName']

        policies = iam.list_attached_role_policies(RoleName=role_name)

        for policy in policies['AttachedPolicies']:
            if policy['PolicyName'] == 'AdministratorAccess':
                writer.writerow([role_name, policy['PolicyName']])


# -----------------------------
# 2. Check MFA enabled for IAM Users
# -----------------------------

users = iam.list_users()['Users']

with open('iam_users_mfa_status.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['IAMUserName', 'MFAEnabled'])

    for user in users:
        username = user['UserName']

        mfa_devices = iam.list_mfa_devices(UserName=username)

        if len(mfa_devices['MFADevices']) > 0:
            mfa_status = True
        else:
            mfa_status = False

        writer.writerow([username, mfa_status])


# -----------------------------
# 3. Check Security Groups open to public
# -----------------------------

security_groups = ec2.describe_security_groups()['SecurityGroups']

with open('security_groups_public_access.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['SGName', 'Port', 'AllowedIP'])

    for sg in security_groups:
        sg_name = sg['GroupName']

        for permission in sg['IpPermissions']:

            from_port = permission.get('FromPort')
            to_port = permission.get('ToPort')

            if from_port in [22, 80, 443] or to_port in [22, 80, 443]:

                for ip_range in permission.get('IpRanges', []):
                    if ip_range['CidrIp'] == '0.0.0.0/0':
                        writer.writerow([sg_name, from_port, '0.0.0.0/0'])


# -----------------------------
# 4. Find Unused EC2 Key Pairs
# -----------------------------

key_pairs = ec2.describe_key_pairs()['KeyPairs']
instances = ec2.describe_instances()

used_keys = set()

for reservation in instances['Reservations']:
    for instance in reservation['Instances']:
        if 'KeyName' in instance:
            used_keys.add(instance['KeyName'])

with open('unused_ec2_keypairs.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['KeyPairName', 'Status'])

    for key in key_pairs:
        key_name = key['KeyName']

        if key_name not in used_keys:
            writer.writerow([key_name, 'Unused'])


print("Security audit completed. CSV reports generated.")