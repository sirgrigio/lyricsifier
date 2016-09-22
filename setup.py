#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='lyricsifier',
    version='0.1',
    description='Attempt to classify songs by their lyrics',
    license='GPLv3',
    url='https://bitbucket.org/zmcode/lyricsifier',
    install_requires=['bs4',
                      'cement',
                      'nltk',
                      'sklearn',
                      'unidecode',],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={'console_scripts': ['lyricsifier=lyricsifier.cli.app:main']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 2',
    ]
)
