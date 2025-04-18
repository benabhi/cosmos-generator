from setuptools import setup, find_packages

setup(
    name="cosmos_generator",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Pillow",
        "numpy",
        "pyfastnoiselite",
    ],
    entry_points={
        "console_scripts": [
            "cosmos-generator=cosmos_generator.cli:main",
        ],
    },
    author="Cosmos Generator Team",
    author_email="info@cosmosgenerator.com",
    description="A Python library for procedurally generating celestial bodies",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cosmos-generator/cosmos-generator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
