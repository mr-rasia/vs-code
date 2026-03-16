import re

# -------------------------------
# Function to validate IPv4
# -------------------------------
def validate_ip(ip):

    parts = ip.split(".")

    if len(parts) != 4:
        return "Invalid IP: IPv4 must contain exactly 4 octets."

    for part in parts:

        if not part.isdigit():
            return f"Invalid IP: '{part}' is not a number."

        num = int(part)

        if num < 0 or num > 255:
            return f"Invalid IP: '{part}' must be between 0 and 255."

    return "Valid IPv4 address."


# -------------------------------
# Function to validate Gmail
# -------------------------------
def validate_gmail(email):

    if "@gmail.com" not in email:
        return "Invalid Email: Must contain '@gmail.com'."

    username = email.split("@gmail.com")[0]

    pattern = r'^[a-z0-9._%+-]+$'

    if not re.match(pattern, username):
        return ("Invalid Email: Username can contain only lowercase letters, "
                "numbers, and permitted symbols (._%+-).")

    return "Valid Gmail address."


# -------------------------------
# Main Program
# -------------------------------
ip = input("Enter an IPv4 address: ")
email = input("Enter a Gmail address: ")

print("\nIP Validation Result:")
print(validate_ip(ip))

print("\nEmail Validation Result:")
print(validate_gmail(email))