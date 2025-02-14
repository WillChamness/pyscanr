from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="pyscanr",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=["scapy>=2.6.1"],
    entry_points={
        "console_scripts": ["pyscanr = pyscanr._init"]
    },
    long_description=description,
    long_description_content_type="text/markdown",
)
