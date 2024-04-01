import subprocess

from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


def get_latest_git_tag() -> str:
    try:
        tag = (
            subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
            .strip()
            .decode("utf-8")
        )
        if tag.startswith("v"):
            tag = tag[1:]
    except subprocess.CalledProcessError:
        raise RuntimeError("Unable to get latest git tag")
    return str(tag)


setup(
    name="creyPY",
    version=get_latest_git_tag(),
    description="My collection of Python and FastAPI shortcuts etc.",
    author="Conrad Großer",
    author_email="conrad@noah.tech",
    packages=find_packages(),
    url="https://github.com/creyD/creyPY",
    license="MIT",
    python_requires=">=3.12",
    install_requires=requirements,
)
