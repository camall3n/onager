from setuptools import setup, find_packages
setup(
    name='onager',
    version='0.1.0',
    description='Lightweight python library for launching experiments and tuning hyperparameters, either locally or on a cluster',
    long_description=open('README.md').read(),
    license=open('LICENSE').read(),
    author='Cameron Allen, Neev Parikh',
    author_email=('csal@brown.edu, neev_parikh@brown.edu'),
    packages=find_packages(include=['onager', 'onager.*']),
    scripts=['bin/onager'],
    url='http://pypi.python.org/pypi/onager/',
    install_requires=[
        "tabulate",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
