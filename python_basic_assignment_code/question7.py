# EC2 Recommendation Script

# Instance size hierarchy
sizes = [
    "nano","micro","small","medium","large",
    "xlarge","2xlarge","4xlarge","8xlarge",
    "16xlarge","32xlarge"
]

# Latest generation mapping
latest_generation = {
    "t2": "t3",
    "t3": "t3"
}

# Function to recommend instance
def recommend_instance(instance, cpu):

    instance_type, instance_size = instance.split(".")
    index = sizes.index(instance_size)

    if cpu < 20:
        status = "Underutilized"
        if index == 0:
            recommended = instance
        else:
            recommended = instance_type + "." + sizes[index-1]

    elif cpu <= 80:
        status = "Optimized"
        new_type = latest_generation.get(instance_type, instance_type)
        recommended = new_type + "." + instance_size

    else:
        status = "Overutilized"
        if index == len(sizes)-1:
            recommended = instance
        else:
            recommended = instance_type + "." + sizes[index+1]

    return status, recommended


# Function to print table
def print_table(data):

    headers = ["Serial No.", "Current EC2", "Current CPU", "Status", "Recommended EC2"]

    table = [headers] + data
    col_widths = [max(len(str(row[i])) for row in table) for i in range(len(headers))]

    def border():
        print("+", end="")
        for w in col_widths:
            print("-"*(w+2)+"+", end="")
        print()

    def print_row(row):
        print("|", end="")
        for i,val in enumerate(row):
            print(" "+str(val).ljust(col_widths[i])+" |", end="")
        print()

    border()
    print_row(headers)
    border()

    for row in data:
        print_row(row)

    border()


# ---- Input ----
current_ec2 = "t2.large"
cpu = 80

status, recommended = recommend_instance(current_ec2, cpu)

data = [
    [1, current_ec2, str(cpu)+"%", status, recommended]
]

print_table(data)