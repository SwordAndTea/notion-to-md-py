from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="notion-to-md-py",
    version="0.1.5",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "httpx",  # Required based on `md.py`
        "pytablewriter", # Required based on `md.py`
        "notion-client",  # Required based on references to `notion_client`
    ],
    description="A package to convert Notion content into Markdown format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SwordAndTea/notion-to-md-py",
    author="Wei Xiang",
    author_email="xiangweiqaz@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    keywords="notion markdown converter python",
    project_urls={
        "Bug Tracker": "https://github.com/SwordAndTea/notion-to-md-py/issues",
        "Source Code": "https://github.com/SwordAndTea/notion-to-md-py",
    },
)