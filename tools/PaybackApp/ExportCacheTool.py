# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Tom Sporer. All rights reserved.
#

import os
import sys

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject

class ExportCacheTool(DataBaseTool):

  ToolName = 'ExportCache'
  ToolLabel = 'Export Cache...'
  ToolCommand = 'exportcache'
  ToolDescription = 'Export Cache'
  ToolTooltip = 'Export Cache'

  def __init__(self, host):
    super (ExportCacheTool, self).__init__(host)

  def initialize(self, **args):

    db = self.host.apis['db']
    self.__project = db.queryOne("project", name="Payback_App")
    self.__projectPath = db.getPath(self.__project.location)

    self.args.addStaticText("\tExport Cache \t \t \t")
    self.args.addSpacer(13)
    self.args.add(name="project", type="instance", template="project", comboSqlQuery="SELECT * FROM project WHERE project.name == 'Payback_App'", enabled=False, hidden=True)
    self.args.add(name="object", type="str", label="Pointee/Asset", combo=["Pointee", "Asset"], value="Pointee")
    self.args.add(name="type", type="str", label="Pointee Type", combo=["Generic", "Special"], value="Generic", enabled=True)
    self.args.add(name="matchWithPointee", type="instance", template="pointee_cache", comboSqlQuery="SELECT * FROM pointee_cache WHERE project_id == ${project} AND object == 'Pointee' AND type == 'Special' ORDER BY name", enabled=False, optional=True)
    self.args.add(name="name", type="str", label="Name", expression="[A-Za-z]+[A-Za-z0-9]*", value=None, enabled=True)
    self.args.addSpacer(10,0)
    self.args.beginRow("Frame Range")
    self.args.add(name="rangeStart", type="int", label="start", value=0)
    self.args.add(name="rangeEnd", type="int", label="end", value=1)
    self.args.endRow()


  def preexecute(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    # Get framerange from playback range
    self.args.get("rangeStart").value = cmds.playbackOptions( q=True, minTime=True )
    self.args.get("rangeEnd").value = cmds.playbackOptions( q=True, maxTime=True )
    # Get framerange from animation range
    # self.args.get("rangeStart").value = cmds.playbackOptions( q=True, animationStartTime=True )
    # self.args.get("rangeEnd").value = cmds.playbackOptions( q=True, animationEndTime=True )

    if len(cmds.ls(selection=True)) == 0:
      raise OPIException("Nothing selected. Please select objects/sets and retry")


  def onValueChanged(self, arg):
    if arg.name == "object":
      if arg.value == "Pointee":
        self.args.get("type").enabled = True
        self.args.get("name").enabled = True
        self.args.get("matchWithPointee").enabled = False
      else:
        self.args.get("type").enabled = False
        self.args.get("type").value = "Special"
        self.args.get("name").enabled = False
        self.args.get("matchWithPointee").enabled = True
        self.args.get("name").value = self.args.getValue("matchWithPointee").name

    if arg.name == "name":
      QtWidgets = self.host.apis["QtWidgets"]
      cObject = self.args.getValue("object")
      cType = self.args.getValue("type")
      cName = self.args.getValue("name")

      filename = cObject + "_" + cType + "_" + cName + ".abc"
      filepath = os.path.join(self.__projectPath, "Cache", "alembic", filename)

      if os.path.exists(filepath):
        msgBox = QtWidgets.QMessageBox
        msgBox.warning(None, "File already exists", "A Cache with that name already exists.\nIt will be overridden if you continue")

    if arg.name == "matchWithPointee":
      self.args.get("name").value = arg.value.name



  def executeMaya(self):
    maya = self.host.apis['maya']
    db = self.host.apis['db']
    cmds = maya.cmds
    rangeStart = self.args.getValue("rangeStart")
    rangeEnd = self.args.getValue("rangeEnd")
    
    # Get selection:
    sel = cmds.ls(selection=True)
    selList = []
    for s in sel:
      sType = cmds.ls(s, showType=True)[1]
      if sType == "objectSet":
        selList += cmds.sets(s, q=True)
      else:
        selList.append(s)
    selList = list(set(selList))

    cObject = self.args.getValue("object")
    cType = self.args.getValue("type")
    if cObject == "Pointee":
      cName = self.args.getValue("name")
    if cObject == "Asset":
      cPointeeMatch = self.args.getValue("matchWithPointee")
      cName = cPointeeMatch.name
    filename = cObject + "_" + cType + "_" + cName + ".abc"
    filepath = os.path.join(self.__projectPath, "Cache", "alembic", filename).replace("\\\\", "/")

    abcExportString = ""
    abcExportString += "-frameRange %s %s" %(rangeStart, rangeEnd)
    abcExportString += " -writeUVSets"
    abcExportString += " -uvWrite"
    abcExportString += " -stripNamespaces"
    abcExportString += " -dataFormat ogawa"
    for selObj in selList:
      abcExportString += " -root " + cmds.ls(selObj, long=True)[0]
    abcExportString += " -file "
    abcExportString += filepath

    print abcExportString

    cmds.AbcExport( j= abcExportString )
    if cObject == "Pointee":
      db.getOrCreateNew("pointee_cache", project=self.__project, object=cObject, type=cType, name=cName, createEmptyFile=False)
    elif cObject == "Special":
      db.getOrCreateNew("asset_cache", project=self.__project, object=cObject, type=cType, name=cName, createEmptyFile=False)
