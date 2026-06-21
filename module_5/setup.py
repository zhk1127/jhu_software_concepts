"""Setup file for the Module 5 GradCafe analytics project."""

from setuptools import find_packages, setup

setup(
    name="gradcafe-analytics-module5",
    version="1.0.0",
    description="Flask and PostgreSQL analytics dashboard for GradCafe data.",
    author="Hongkang Zhang",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "psycopg[binary]",
        "python-dotenv",
        "beautifulsoup4",
    ],
)