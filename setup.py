from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='onager',
    version='0.1.2',
    description='Lightweight python library for launching experiments and tuning hyperparameters, either locally or on a cluster',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Cameron Allen, Neev Parikh',
    author_email=('csal@brown.edu,neev_parikh@brown.edu'),
    packages=find_packages(include=['onager', 'onager.*']),
    scripts=['bin/onager'],
    url='https://github.com/camall3n/onager/',
    install_requires=[
        "tabulate",
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)
