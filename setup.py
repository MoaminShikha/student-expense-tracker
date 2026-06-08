#!/usr/bin/env python
"""Setup script for Student Expense Tracker."""

from setuptools import setup, find_packages

setup(
    name="student-expense-tracker",
    version="0.2.0",
    description="Personal finance management app for Israeli university students",
    author="Moamin Shikha",
    author_email="moamin.shikha@mail.huji.ac.il",
    url="https://github.com/moamin/student-expense-tracker",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "PyQt6>=6.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-qt>=4.2.0",
            "black>=23.12.0",
            "isort>=5.13.2",
            "ruff>=0.1.8",
            "mypy>=1.7.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "student-expense-tracker=expense_tracker.app.cli:main",
            "mizaan=expense_tracker.app.gui.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
    ],
)
