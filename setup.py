from setuptools import setup, find_packages
setup(
    name='onager',
    version='0.1.0',
    description='Launching, logging and plotting experiments',
    long_description=open('README.md').read(),
    license=open('LICENSE').read(),
    author='Cameron Allen <csal@cs.brown.edu> , Neev Parikh <neev_parikh@brown.edu>',
    packages=find_packages(include=['onager', 'onager.*']),
    scripts=['bin/onager'],
    install_requires=[
        "tabulate",
    ],
)
