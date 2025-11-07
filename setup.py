from setuptools import setup, find_packages

setup(
    name="notion-to-md-py",  # Replace with your package name
    version="0.1.4",
    packages=find_packages(),  # Automatically include the submodules
    install_requires=[
        "httpx",  # Required based on `md.py`
        "pytablewriter", # Required based on `md.py`
        "notion-client",  # Required based on references to `notion_client`
    ],
    extras_require={
        "async": [
            "asyncio",  # Used in async functionality
        ]
    },
    description="A package to convert Notion content into Markdown format",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SwordAndTea/notion-to-md-py",
    author="Wei Xiang",
    author_email="xiangweiqaz@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3.7",
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