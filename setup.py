"""
Setup script for the AI Web Research Agent.
"""
from setuptools import setup, find_packages

setup(
    name="ai-web-research-agent",
    version="0.1.0",
    author="Your Name",
    author_email="shuvankarnaskar75@gmail.com",
    description="An AI-powered web research agent using Groq LLM",
    # Fix the encoding issue with README.md
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/shuvankar7/ai-web-research-agent",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.3",
        "trafilatura>=1.2.0",
        "nltk>=3.6.0",
        "python-dotenv>=0.19.0",
        "langchain>=0.1.0",
        "langchain-groq>=0.0.1",
        "langchain-community>=0.0.13",
        "langchain-core>=0.1.17",
        "duckduckgo-search>=4.1.1",
        "pydantic>=2.5.2",
    ],
    entry_points={
        "console_scripts": [
            "research=src.main:main",
        ],
    },
)