# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import sys

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException

class LayoutRefreshTool(DataBaseTool):

  ToolName = 'LayoutRefresh'
  ToolLabel = 'Layout Refresh'
  ToolCommand = 'layoutrefresh'
  ToolDescription = 'Layout Refresh'
  ToolTooltip = 'Layout Refresh'

  def __init__(self, host):
    super (LayoutRefreshTool, self).__init__(host)

  def initialize(self, **args):

    self.args.add(name="checkbox", type="bool", value=False)

  def execute (self):

    print "hello world"

  def onValueChanged(self, arg):

    if arg.name == "checkbox":
      print "checkbox was checked."
      print "refreshing now..."
      self.args.layout.refresh()



if __name__ == '__main__':

  import os
  import opi
  from opi.client.database import DataBase as OpiDB
  from opi.tools.host import Host as OPIHost
  from opi.tools.workshop import WorkShop as OPIWorkShop
  from opi.ui.Qt import QtWidgets, QtCore

  path = os.path.split(os.path.abspath(__file__))[0]
  path = os.path.split(path)[0]
  path = os.path.split(path)[0]
  path = os.path.split(path)[0]

  print path

  dbRoot = "e:\\PROJECTS"
  
  templateRoot =  os.path.join(path, 'OPI_Tools', 'templates')
  toolRoot =  os.path.join(path, 'OPI_Tools', 'tools')

  db = OpiDB(dbRoot, templateRoot=templateRoot, rootSubFolders=['BEI_Spiel'])

  host = OPIHost('python', {'db': db, 'QtWidgets': QtWidgets, 'QtCore': QtCore})
  workshop = OPIWorkShop(host, toolRoot)

  tool = workshop.instantiate(cmd='layoutrefresh')
  tool.invokeWithUI()


