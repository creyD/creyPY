from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="creyPY",
    version="0.0.9",
    description="My collection of Python and FastAPI shortcuts etc.",
    author="Conrad Großer",
    author_email="conrad@noah.tech",
    packages=find_packages(),
    url="https://github.com/creyD/creyPY",
    license="MIT",
    python_requires=">=3.12",
    install_requires=requirements,
)
