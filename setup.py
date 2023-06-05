import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cpquant",
    version="0.0.1",
    author="Charlie Ray",
    author_email="charlie.ray320@gmail.com",
    description="A package containing common functions for CP Quant Club",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Cal-Poly-Quant-Club/cpquant",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)