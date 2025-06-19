"""
SelfMastery B2B业务系统安装配置
"""
from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="selfmastery-b2b-system",
    version="1.0.0",
    author="SelfMastery Team",
    author_email="dev@selfmastery.com",
    description="SelfMastery B2B业务管理系统",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/selfmastery/b2b-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "pre-commit>=3.6.0",
        ],
        "docs": [
            "sphinx>=7.1.2",
            "sphinx-rtd-theme>=1.3.0",
            "sphinx-autodoc-typehints>=1.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "selfmastery-backend=backend.main:main",
            "selfmastery-frontend=frontend.main:main",
            "selfmastery-cli=shared.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "frontend": ["resources/*", "ui/*.ui"],
        "config": ["*.yaml", "*.json"],
        "": ["*.md", "*.txt", "*.cfg"],
    },
    zip_safe=False,
    keywords="b2b business management system pyqt6 fastapi",
    project_urls={
        "Bug Reports": "https://github.com/selfmastery/b2b-system/issues",
        "Source": "https://github.com/selfmastery/b2b-system",
        "Documentation": "https://docs.selfmastery.com/b2b-system",
    },
)