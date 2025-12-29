"""
TaskFlow Setup Configuration
Developed by: visionis
"""

from setuptools import setup, find_packages

setup(
    name="taskflow-async",
    version="1.0.0",
    author="visionis",
    # email field removed for privacy
    description="A high-performance asynchronous task manager with exponential backoff.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/visionis/TaskFlow",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    python_requires='>=3.10',
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Source": "https://github.com/visionis/TaskFlow",
        "Tracker": "https://github.com/visionis/TaskFlow/issues",
    },
)
