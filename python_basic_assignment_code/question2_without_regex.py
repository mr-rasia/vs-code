import random
import string

def generate_password():

    uppercase = random.choice(string.ascii_uppercase)
    lowercase = random.choice(string.ascii_lowercase)
    digits = random.sample(string.digits, 2)
    special = random.choice("!@#$%&*")

    remaining_length = 16 - (1 + 1 + 2 + 1)

    all_chars = string.ascii_letters + string.digits + "!@#$%&*"

    remaining = []

    while len(remaining) < remaining_length:
        char = random.choice(all_chars)
        if char not in remaining and char not in digits and char not in [uppercase, lowercase, special]:
            remaining.append(char)

    password_list = [uppercase, lowercase] + digits + [special] + remaining

    random.shuffle(password_list)

    password = "".join(password_list)

    return password


password = generate_password()

print("Generated Password:", password)