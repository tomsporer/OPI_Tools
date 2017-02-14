# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2017, Helge Mathee. All rights reserved.
#

import os

import opi
from opi.tools.host import Host
from opi.tools.workshop import WorkShop
from opi.ui.Qt import QtWidgets, QtCore

def test_tools_submitRender():

  toolRoot = os.path.split(os.path.abspath(__file__))[0]
  toolRoot = os.path.split(toolRoot)[0]
  toolRoot = os.path.split(toolRoot)[0]
  toolRoot = os.path.join(toolRoot, 'tools')

  host = Host('python', {'QtWidgets': QtWidgets, 'QtCore': QtCore})
  ws = WorkShop(host, toolRoot)
  tool = ws.instantiate(cmd='submitrender')
  tool.invokeWithUI()

if __name__ == '__main__':
  test_tools_submitRender()
