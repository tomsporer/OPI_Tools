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
    self.__project = db.queryOne("project", name="Payback_App")
    self.__projectPath = db.getPath(self.__project.location)

    # self.args.addStaticText("\tExport rsProxy \t \t \t")
    # self.args.addSpacer(13)
    # self.args.add(name="project", type="instance", template="project", comboSqlQuery="SELECT * FROM project WHERE project.name == 'Payback_App'", enabled=False, hidden=True)
    # self.args.add(name="name", type="str", label="Name", expression="[A-Za-z]+[A-Za-z0-9]*", value=None, enabled=False)
    # # self.args.addSpacer(10,0)
    # self.args.beginRow("Frame Range")
    # self.args.add(name="rangeStart", type="int", label="start", value=1)
    # self.args.add(name="rangeEnd", type="int", label="end", value=2)
    # self.args.endRow()


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


  # def preexecute(self, **args):
  #   maya = self.host.apis['maya']
  #   cmds = maya.cmds

  #   # get name from selected locator
  #   loc = cmds.ls(selection=True)[0]
  #   pName = loc.split("_")[2]
  #   self.args.get("name").value = pName
    
  #   db = self.host.apis['db']
  #   QtWidgets = self.host.apis["QtWidgets"]
  #   pName = self.args.getValue("name")

  #   # fileExists = db.query("pointee_rsproxy", name=pName)
  #   # if fileExists != []:
  #   #   msgBox = QtWidgets.QMessageBox
  #   #   msgBox.warning(None, "File already exists", "A Proxy with that name already exists.\n! Overriding will cause problems !\nPlease choose a different name (or manually delete the old files before continuing).")
    
  #   # # Get framerange from playback range
  #   # self.args.get("rangeStart").value = cmds.playbackOptions( q=True, minTime=True )
  #   # self.args.get("rangeEnd").value = cmds.playbackOptions( q=True, maxTime=True )

  #   # Get framerange from alembic node
  #   abcNode = self.getAlembicNode(loc)
  #   self.args.get("rangeStart").value = cmds.getAttr(abcNode + ".startFrame")
  #   self.args.get("rangeEnd").value = cmds.getAttr(abcNode + ".endFrame")

  #   if len(cmds.ls(selection=True)) == 0:
  #     raise OPIException("Nothing selected. Please select objects/sets and retry")



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
      filename = "Pointee_rsProxy_" + pName + "_####.rs"
      filepath = os.path.join(self.__projectPath, "Cache", "rsProxy", filename).replace("\\", "/")

      rsProxyExportString = "rsProxy"
      rsProxyExportString += " -fp \"%s\"" %(filepath)
      rsProxyExportString += " -s %s" %(rangeStart)
      rsProxyExportString += " -e %s" %(rangeEnd)
      rsProxyExportString += " -b 1"
      rsProxyExportString += " -sl"
      
      print "# INFO: executing \"" + rsProxyExportString + "\" where selection=" + str(cmds.ls(selection=True))
      mel.eval(rsProxyExportString)
    # db.getOrCreateNew("pointee_rsproxy", project=self.__project, name=pName, createEmptyFile=False)

