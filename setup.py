import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="heatwave",
    version="1.2.1",
    description=("A way of visualizing a heat map of a git repo"),
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/james-stoup/heatwave",
    author="James Stoup",
    author_email="james.r.stoup@gmail.com",
    keywords="git visualize heatmap",
    license="GNU General Public License v3.0",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=["Click", "MonthDelta", "GitPython"],
    entry_points={"console_scripts": ["heatwave=src.main:cli"]},
)
