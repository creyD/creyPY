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
    description="Collection of my Python and FastAPI shortcuts, snippets etc.",
    long_description=open("README.md").read(),
    author="Conrad Großer",
    author_email="conrad@noah.tech",
    packages=find_packages(),
    url="https://github.com/creyD/creyPY",
    license="MIT",
    python_requires=">=3.12",
    install_requires=requirements,
)
