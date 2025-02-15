from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="pyscanr",
    version="0.1.1",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=["scapy>=2.6.1"],
    entry_points={
        "console_scripts": ["pyscanr = pyscanr:run"]
    },
    long_description=description,
    long_description_content_type="text/markdown",
)
