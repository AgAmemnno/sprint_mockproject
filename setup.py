import os
from setuptools import setup, find_packages

def read_requirements():
    """Parse requirements from requirements.txt."""
    reqs_path = os.path.join('.', 'requirements.txt')
    with open(reqs_path, 'r') as f:
        requirements = [line.rstrip() for line in f]
    return requirements

setup(
    name='p2popt',
    version='0.0.1',
    description='MockProject for Python Sprint',
    author='AgAmemnno',
    author_email='kaz380@hotmail.co.jp',
    url     ='https://github.com/AgAmemnno/sprint_mockproject',
    license ='MIT',
    install_requires=read_requirements(),
    packages = find_packages()
)
