#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name="proxycore",
    python_requires=">=3.8",
    version="0.0.1",
    url="https://github.com/florimondmanca/proxycore",
    license="MIT",
    description=(
        "Proof of concept for a lightweight HTTP/1.1 proxy service "
        "built with ASGI and HTTPCore."
    ),
    author="Florimond Manca",
    author_email="florimond.manca@gmail.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["httpcore", "starlette"],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Private :: Do Not Upload",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
