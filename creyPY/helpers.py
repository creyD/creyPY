import secrets
import string


def create_random_password(length: int = 12) -> str:
    all_characters = string.ascii_letters + string.digits + string.punctuation

    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation),
    ]
    password += [secrets.choice(all_characters) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(password)
    return "".join(password)
