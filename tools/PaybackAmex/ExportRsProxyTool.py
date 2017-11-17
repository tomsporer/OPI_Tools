# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Tom Sporer. All rights reserved.
#

import os
import sys

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject

class ExportRsProxyTool(DataBaseTool):

  ToolName = 'ExportRsProxy'
  ToolLabel = 'Export rsProxy...'
  ToolCommand = 'exportrsproxy'
  ToolDescription = 'Export rsProxy'
  ToolTooltip = 'Export rsProxy'

  def __init__(self, host):
    super (ExportRsProxyTool, self).__init__(host)
    self._noUI = True

  def initialize(self, **args):

    db = self.host.apis['db']
    self.__project = db.queryOne("project", name="Payback_Amex")
    self.__projectPath = db.getPath(self.__project.location)



  def getAlembicNode(self, rootLocator):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    lr = cmds.listRelatives(rootLocator, allDescendents=True, path=True)
    for r in lr:
      lc = cmds.listConnections(r, connections=True)
      if not lc == None:
        for c in lc:
          if "AlembicNode" in c:
            return c
            break


  def executeMaya(self):
    maya = self.host.apis['maya']
    db = self.host.apis['db']
    cmds = maya.cmds
    mel = maya.mel
    
    # Get selection:
    selList = cmds.ls(selection=True)

    for loc in selList:
      cmds.select(loc)
      pName = loc.split("_")[2]
      abcNode = self.getAlembicNode(loc)
      rangeStart = int(cmds.getAttr(abcNode + ".startFrame"))
      rangeEnd = int(cmds.getAttr(abcNode + ".endFrame"))
      speed = cmds.getAttr(abcNode + ".speed")
      rangeEnd = int(round(rangeEnd/speed))
      filename = "Pointee_rsProxy_" + pName + "_####.rs"
      if speed < 1:
        path = os.path.join(self.__projectPath, "Cache", "rsProxy", "slowmo")
      else:
        path = os.path.join(self.__projectPath, "Cache", "rsProxy")

      if not os.path.exists(path):
        os.makedirs(path)

      filepath = os.path.join(path, filename).replace("\\", "/")

      rsProxyExportString = "rsProxy"
      rsProxyExportString += " -fp \"%s\"" %(filepath)
      rsProxyExportString += " -s %s" %(rangeStart)
      rsProxyExportString += " -e %s" %(rangeEnd)
      rsProxyExportString += " -b 1"
      rsProxyExportString += " -sl"
      
      print "# INFO: executing \"" + rsProxyExportString + "\" where selection=" + str(cmds.ls(selection=True))
      mel.eval(rsProxyExportString)
