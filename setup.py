import subprocess

from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("requirements.build.txt") as f:
    build_requirements = f.read().splitlines()

with open("requirements.pg.txt") as f:
    pg_requirements = f.read().splitlines()

with open("requirements.auth0.txt") as f:
    auth0_requirements = f.read().splitlines()

with open("requirements.stripe.txt") as f:
    stripe_requirements = f.read().splitlines()


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
    long_description_content_type="text/markdown",
    author="Conrad Großer",
    author_email="code@grosser.group",
    packages=find_packages(),
    url="https://github.com/creyD/creyPY",
    license="MIT",
    python_requires=">=3.12",
    install_requires=requirements,
    extras_require={
        "build": build_requirements,
        "postgres": pg_requirements,
        "auth0": auth0_requirements,
        "stripe": stripe_requirements,
        "all": build_requirements + pg_requirements + auth0_requirements + stripe_requirements,
    },
    keywords=[
        "creyPY",
        "Python",
        "FastAPI",
        "shortcuts",
        "snippets",
        "utils",
    ],
    platforms="any",
)
