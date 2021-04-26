#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup

pkg = 'Extensions.InternetSpeedTest'
setup(name='enigma2-plugin-extensions-internet-speedtest',
       version='1.0',
       description='Speedtest for enigma2',
       packages=[pkg],
       package_dir={pkg: 'usr'},
       package_data={pkg: ['*.png', '*/*.png']},
      )
