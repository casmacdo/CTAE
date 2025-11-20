"""Setup script for CTAE package."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ctae",
    version="0.4.3",
    author="Piotr Tompalski, Juha Metsaranta, Vinicius Manvailer Goncalves",
    author_email="piotr.tompalski@NRCan-RNCan.gc.ca",
    description="Canadian Tree Allometric Equations - Python implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/casmacdo/CTAE",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
    ],
    package_data={
        "ctae": ["data/*.csv", "data/*.json"],
    },
    include_package_data=True,
)
