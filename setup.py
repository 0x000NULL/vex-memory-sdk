"""
Setup configuration for vex-memory-sdk
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get long description from README
long_description = (here / "README.md").read_text(encoding="utf-8")

# Get version from __init__.py
version = {}
with open(here / "vex_memory" / "__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)
            break

setup(
    name="vex-memory-sdk",
    version=version.get("__version__", "1.1.0"),
    description="Python client library for vex-memory API with intelligent context building",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0x000NULL/vex-memory-sdk",
    author="Vex Memory Team",
    author_email="",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="memory, ai, llm, context, vector-search, semantic-search",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
            "types-requests>=2.25.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "vex-memory=vex_memory.cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/0x000NULL/vex-memory-sdk/issues",
        "Source": "https://github.com/0x000NULL/vex-memory-sdk",
        "Server": "https://github.com/0x000NULL/vex-memory",
        "Documentation": "https://vexmemory.dev",
    },
)
