from setuptools import setup
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='squirrels',
    packages=['squirrels'],
    description='Python Package for Configuring SQL Generating APIs',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Tim Huang',
    license='MIT',
    install_requires=['pandasql', 'pandas', 'sqlalchemy<2', 'Jinja2'],
    setup_requires=['pytest-runner==6.0.0', 'setuptools_scm'],
    version='0.1',
    use_scm_version=False,
    tests_require=['pytest==7.2.0'],
    test_suite='tests',
    entry_points= {
        'console_scripts': ['squirrels=squirrels.command_line:main']
    }
)
