""" A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ansible-check-insights',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.6',

    description='Conformance as an Ansible Playbook',
    long_description=long_description,

    url='https://github.com/gavin-romig-koch/probable-giggle',

    author='Gavin Romig-Koch',
    author_email='gavin@redhat.com',

    license='GPLv3+',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Systems Administration',
    ],

    install_requires=['ansible', 'requests'],

    data_files=[
	('bin', ['bin/ansible-check-insights']),
	('share/ansible-check-insights/plugins/action_plugins', ['share/ansible-check-insights/plugins/action_plugins/check.py']),
	('share/ansible-check-insights/plugins/callback_plugins', ['share/ansible-check-insights/plugins/callback_plugins/notify_insights.py']),
	('share/ansible-check-insights/plugins/library', ['share/ansible-check-insights/plugins/library/check.py']),
    ],

    scripts=[
        'bin/ansible-check-insights',
    ],
)
