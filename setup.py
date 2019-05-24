from setuptools import find_packages, setup

with open('requirements.txt') as f:
    REQUIRED = f.read().splitlines()

setup(name='pyopteryx',
      version='0.1',
      description='The funniest joke in the world',
      license='EPL',
      packages=find_packages(),
      install_requires=REQUIRED
      )
