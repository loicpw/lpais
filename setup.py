#! /usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

setuptools.setup(
    name="lpais",
    version="0.0.2",
    url="https://github.com/loicpw/lpais",
    download_url = "https://github.com/loicpw/lpais.git",

    author="Loïc Peron",
    author_email="peronloic.us@gmail.com",

    description="use libais to decode ais, replacing ais.stream",
    long_description='\n\n'.join(
        open(f, 'rb').read().decode('utf-8')
        for f in ['README.rst', 'HISTORY.rst']),

    packages=setuptools.find_packages(),

    install_requires=[
        'libais',
    ],

    license='MIT License',
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
