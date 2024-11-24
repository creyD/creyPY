import random
import string


def create_random_password(length: int = 12) -> str:
    all_characters = string.ascii_letters + string.digits + string.punctuation

    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice(string.punctuation),
    ]
    password += random.choices(all_characters, k=length - 4)
    random.shuffle(password)
    return "".join(password)
