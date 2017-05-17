import os
import sys

from setuptools import setup
from typing import List

if sys.version_info < (3, 3):
    sys.exit("Staffeli requires Python >= 3.3.")


def syblingpath(fname: str) -> str:
    return os.path.join(os.path.dirname(__file__), fname)


def read(fname: str) -> str:
    return open(syblingpath(fname)).read()


def readlines(fname: str) -> List[str]:
    with open(syblingpath(fname)) as f:
        return [line for line in f]


setup(
    name="staffeli",
    description="DIKU support tools for Canvas LMS",
    install_requires=[
        "pyyaml>=3.12",
        "requests>=2.12.5",
        "python-slugify>=1.2.1",
        "sphinx>=1.5.2",
        "python-Levenshtein>=0.11.0",
        "beautifulsoup4>=4.5.3",
        "typing>=3.6.1"
    ],
    tests_require=readlines("test-requirements.txt"),
    keywords=["staffeli", "Canvas", "DIKU"],
    long_description=read('README.rst'),
    url="https://github.com/DIKU-EDU/staffeli",
    version='0.4.2',
    packages=["staffeli"],
    maintainer="Oleks",
    maintainer_email="oleks@oleks.info",
    license="EUPLv1.1",
    entry_points={
        'console_scripts': [
            'staffeli = staffeli.cli:main'
        ]
    },
)
