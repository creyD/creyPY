import secrets
import string
import csv
from pathlib import Path


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


def data_to_csv(file: Path, data: list) -> None:

    with file.open(mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=";")
        writer.writeheader()
        writer.writerows(data)
