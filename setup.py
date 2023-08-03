import setuptools
from setuptools import setup

# Reading README for full description
with open('README.md', 'r') as f:
    long_description = f.read()

# Getting dependencies list from requirements.txt
with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

setup(
    name='TradingView Auto Commenting Bot',
    version='0.0.1',
    description='Script, that writes predefined comments under a provided list of posts on tradingview.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    install_requires=requirements,
    python_requires=">=3.10",
)