#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="pandalog",
    description="simple graylog python wrapper",
    version="0.5.0",
    author="Yuri Neves",
    author_email="<yuri.neves@bitpanda.com>",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
         "click==7.1.2",
         "requests==2.25.1",
    ],
    entry_points={
        "console_scripts": [
            "pandalog = pandalog.cmd:entrypoint",
            "pandalog-auth = pandalog.cmd:auth_entrypoint"
        ]
    }
)
