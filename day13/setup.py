# setup.py

from setuptools import setup, find_packages

setup(
    name="booking_system",
    version="1.0.0",
    description="Система управления бронированиями отелей с аудитом",
    author="Student",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.0.0",
    ],
)