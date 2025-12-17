"""
Setup script for Eye Mouse Control
"""

from setuptools import setup, find_packages
import os

# Read requirements
def read_requirements():
    with open("requirements.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read README
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

setup(
    name="eye-mouse-control",
    version="1.0.0",
    description="Hands-free mouse control using face tracking and blink detection",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Eye Mouse Control Team",
    author_email="contact@example.com",
    url="https://github.com/example/eye-mouse-control",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video :: Capture",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Utilities",
    ],
    keywords="mouse control accessibility face tracking blink detection computer vision",
    entry_points={
        "console_scripts": [
            "eye-mouse=eye_mouse_control:main",
            "eye-mouse-config=config_gui:main",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
        "gpu": [
            "mediapipe-gpu",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/example/eye-mouse-control/issues",
        "Source": "https://github.com/example/eye-mouse-control",
        "Documentation": "https://github.com/example/eye-mouse-control/wiki",
    },
)
