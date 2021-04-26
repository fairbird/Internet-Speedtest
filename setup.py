#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup

pkg = 'Extensions.InternetSpeedTest'
setup(name='enigma2-plugin-extensions-internetspeedtest',
       version='1.0',
       description='Internet speed test for enigma2',
       packages=[pkg],
       package_dir={pkg: 'usr'},
       package_data={pkg: ['*.png', '*/*.png', '*/locale/*/LC_MESSAGES/*.mo']},
      )
