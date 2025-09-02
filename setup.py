#!/usr/bin/env python3
"""
Setup script for UMCP (Universal Measurement and Control Protocol).
"""

from setuptools import setup, find_packages
import os

# Read the README file
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "UMCP: Universal Measurement and Control Protocol for collapse calculus and time series analysis."

# Read requirements
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8") as f:
        install_requires = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    install_requires = ["matplotlib", "python-docx", "pandas"]

setup(
    name="umcp",
    version="2.0.0",
    author="UMCP Development Team",
    author_email="",
    description="Universal Measurement and Control Protocol for collapse calculus and time series analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/calebpruett927/UMCP",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require={
        "dev": ["pytest", "black", "flake8", "mypy"],
        "docs": ["sphinx", "sphinx-rtd-theme"],
        "full": ["numpy", "scipy"],
    },
    entry_points={
        "console_scripts": [
            "umcp-validate=umcp.scripts.validate:main",
            "umcp-playground=umcp.scripts.playground:main",
            "umcp-turbo=umcp.scripts.turbo:main",
        ],
    },
    include_package_data=True,
    package_data={
        "umcp": ["configs/*.json", "data/*.csv"],
    },
    zip_safe=False,
)