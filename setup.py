#!/usr/bin/env python3

import os
import sys
from setuptools import setup, find_packages

# Read README file
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []

# Ensure we're using Python 3.8+
if sys.version_info < (3, 8):
    sys.exit('Sorry, Python < 3.8 is not supported')

# Package metadata
NAME = 'dominus-mongo'
VERSION = '1.0.0'
DESCRIPTION = 'Service for monitoring and managing server statuses in MongoDB clusters'
LONG_DESCRIPTION = read_file('README.md')
AUTHOR = 'Your Name'
AUTHOR_EMAIL = 'your.email@example.com'
URL = 'https://github.com/Basyuk/dominus-mongo'
LICENSE = 'MIT'

# Requirements
INSTALL_REQUIRES = read_requirements('requirements.txt')

# Development requirements
EXTRAS_REQUIRE = {
    'dev': [
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'pytest-asyncio>=0.21.0',
        'black>=23.0.0',
        'isort>=5.12.0',
        'flake8>=6.0.0',
        'mypy>=1.0.0',
        'bandit>=1.7.0',
        'safety>=2.0.0',
    ],
    'docs': [
        'mkdocs>=1.4.0',
        'mkdocs-material>=9.0.0',
        'mkdocs-mermaid2-plugin>=0.6.0',
    ],
    'testing': [
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'pytest-asyncio>=0.21.0',
        'requests-mock>=1.10.0',
        'mongomock>=4.1.0',
    ]
}

# Classifiers
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Topic :: Database',
    'Topic :: System :: Clustering',
    'Topic :: System :: Monitoring',
    'Topic :: System :: Systems Administration',
    'Framework :: FastAPI',
    'Environment :: Web Environment',
    'Environment :: Console',
]

# Keywords
KEYWORDS = [
    'mongodb',
    'replica-set',
    'clustering',
    'monitoring',
    'fastapi',
    'status',
    'management',
    'database',
    'devops',
    'infrastructure'
]

# Entry points
ENTRY_POINTS = {
    'console_scripts': [
        'dominus-mongo=dominus.main:main',
    ],
}

# Package data
PACKAGE_DATA = {
    'dominus': [
        'py.typed',
    ],
}

# Setup configuration
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_data=PACKAGE_DATA,
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    entry_points=ENTRY_POINTS,
    classifiers=CLASSIFIERS,
    keywords=' '.join(KEYWORDS),
    python_requires='>=3.8',
    zip_safe=False,
    project_urls={
        'Bug Reports': f'{URL}/issues',
        'Source': URL,
        'Documentation': f'{URL}#readme',
        'Funding': f'{URL}#support-the-project',
        'Say Thanks!': f'{URL}#contributors',
        'Security': f'{URL}/security',
        'CI/CD': f'{URL}/actions',
        'Docker Hub': 'https://hub.docker.com/r/Basyuk/dominus-mongo',
    },
)
