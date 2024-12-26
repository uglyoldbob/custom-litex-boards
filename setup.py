#!/usr/bin/env python3

from setuptools import setup
from setuptools import find_packages


with open("README.md", "r", encoding="utf-8") as fp:
    long_description = fp.read()


setup(
    name                          = "custom-litex-boards",
    version                       = "2024.08",
    description                   = "UOB LiteX supported boards",
    long_description              = long_description,
    long_description_content_type = "text/markdown",
    author                        = "Thomas Epperson",
    author_email                  = "thomas.epperson@gmail.com",
    url                           = "http://uglyoldbob.com",
    download_url                  = "https://github.com/uglyoldbob/custom-litex-boards",
    test_suite                    = "test",
    license                       = "BSD",
    python_requires               = "~=3.7",
    install_requires              = ["litex"],
    include_package_data          = True,
    keywords                      = "HDL ASIC FPGA hardware design",
    classifiers                   = [
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Environment :: Console",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    packages                      = find_packages(exclude=['test*']),
)
