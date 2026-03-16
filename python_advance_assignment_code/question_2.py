import boto3


ACCOUNT_B_ROLE = "arn:aws:iam::763348961039:role/RoleB"
ACCOUNT_C_ROLE = "arn:aws:iam::815023191537:role/RoleC"


def assume_role(role_arn, session_name, credentials=None):
    if credentials:
        sts = boto3.client(
            "sts",
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"]
        )
    else:
        sts = boto3.client("sts")

    response = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName=session_name
    )

    return response["Credentials"]


def main():

    # Step 1: Assume RoleB (Account B)
    role_b_creds = assume_role(ACCOUNT_B_ROLE, "SessionB")

    print("Assumed RoleB")

    # Step 2: Assume RoleC using RoleB credentials
    role_c_creds = assume_role(ACCOUNT_C_ROLE, "SessionC", role_b_creds)

    print("Assumed RoleC")

    # Step 3: Access EC2 in Account C
    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=role_c_creds["AccessKeyId"],
        aws_secret_access_key=role_c_creds["SecretAccessKey"],
        aws_session_token=role_c_creds["SessionToken"],
        region_name="us-east-1"
    )

    response = ec2.describe_instances()

    print("EC2 Instances in Account C:")

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            print(instance["InstanceId"])


if __name__ == "__main__":
    main()