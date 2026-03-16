import random
import string
import re

def generate_password():

    chars = string.ascii_letters + string.digits + "!@#$%&*"

    while True:

        password = ''.join(random.sample(chars, 16))

        pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=(?:.*\d){2,})(?=.*[!@#$%&*])[A-Za-z\d!@#$%&*]{16}$'

        if re.match(pattern, password):
            return password


password = generate_password()

print("Generated Password:", password)