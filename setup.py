from setuptools import setup, find_packages
import os
import sys


if sys.version_info < (3, 3):
    sys.exit("Staffeli requires Python >= 3.3.")


def readsybling(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="staffeli",
    description="DIKU support tools for Canvas LMS",
    install_requires=[
        "pyyaml>=3.12",
        "requests>=2.12.5",
        "python-slugify>=1.2.1",
    ],
    keywords=["staffeli", "Canvas", "DIKU"],
    long_description=readsybling('README.md'),
    url="https://github.com/DIKU-EDU/Staffeli",
    version='0.3.1',
    packages=find_packages(),
    maintainer="Oleks",
    maintainer_email="oleks@oleks.info",
    license="EUPLv1.1",
    entry_points={
        'console_scripts': [
            'staffeli = staffeli.cli:main'
        ]
    },
)
