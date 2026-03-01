"""Setup script for vex-memory Python SDK."""

from setuptools import setup, find_packages
import os

# Read README for long description
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "Python SDK for vex-memory - Human-inspired AI memory system"

setup(
    name="vex-memory",
    version="1.0.0",
    author="Ethan Aldrich",
    author_email="e.aldrich@budgetlasvegas.com",
    description="Python SDK for vex-memory - Human-inspired AI memory system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0x000NULL/vex-memory-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/0x000NULL/vex-memory-sdk/issues",
        "Documentation": "https://github.com/0x000NULL/vex-memory-sdk/tree/main/docs",
        "Server": "https://github.com/0x000NULL/vex-memory",
        "Source": "https://github.com/0x000NULL/vex-memory-sdk",
    },
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=2.0.0",
        "tenacity>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "types-requests>=2.28.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
