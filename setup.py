import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="heatwave",
    version="1.0",
    author="James Stoup",
    description=("A way of visualizing a heat map of a git repo"),
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    py_modules=["heatwave"],
    install_requires=["Click", "MonthDelta", "GitPython"],
    entry_points={"console_scripts": ["heatwave=heatwave.heatwave:cli"]},
)
