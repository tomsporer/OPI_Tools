# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Tom Sporer. All rights reserved.
#

import os
import sys

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject

class ImportCacheTool(DataBaseTool):

  ToolName = 'ImportCache'
  ToolLabel = 'Import Cache...'
  ToolCommand = 'importcache'
  ToolDescription = 'Import Cache'
  ToolTooltip = 'Import Cache'

  def __init__(self, host):
    super (ImportCacheTool, self).__init__(host)

  def initialize(self, **args):

    db = self.host.apis['db']
    self.__project = db.queryOne("project", name="Payback_App")
    self.__projectPath = db.getPath(self.__project.location)

    self.args.addStaticText("\tImport Cache \t \t \t")
    self.args.addSpacer(13)
    self.args.add(name="project", type="instance", template="project", comboSqlQuery="SELECT * FROM project WHERE project.name == 'Payback_App'", enabled=False, hidden=True)
    self.args.add(name="object", type="str", label="Pointee/Asset", combo=["Pointee", "Asset"], value=args.get("object", "Pointee"))
    self.args.add(name="type", type="str", label="Pointee Type", combo=["Generic", "Special"], value=args.get("type", "Generic"), enabled=True)
    self.args.add(name="cache", type="instance", label="Cache", template="pointee_cache", comboSqlQuery="SELECT * FROM pointee_cache WHERE project_id == ${project} AND object == '${object}' AND type == '${type}' ORDER BY name", value=args.get("cache", None))
    self.args.add(name="importMode", type="str", label="Import mode", combo=["Merge", "Add under selection", "Add under root"], value=args.get("importMode", "Merge"), enabled=True)

    self.results.add(name="cacheNode", type="str")

  def preexecute(self, **args):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    sel = cmds.ls(selection=True)
    if len(sel) == 0:
      self.args.get("importMode").value = "Add under root"
      self.args.get("importMode").enabled = False


  def onValueChanged(self, arg):
    if arg.name == "object":
      if arg.value == "Pointee":
        self.args.get("type").enabled = True
      else:
        self.args.get("type").enabled = False
        self.args.get("type").value = "Special"


  def executeMaya(self):
    db = self.host.apis['db']
    maya = self.host.apis['maya']
    cmds = maya.cmds
    mel = maya.mel

    importMode = self.args.getValue("importMode")
    cache = self.args.getValue("cache")
    cFilename = cache.filename[:-4]
    cFilepath = db.getPath(cache.location)
    sel = cmds.ls(selection=True)

    abcImportStringStart = "AbcImport -mode import"
    abcImportStringEnd = " \"" + cFilepath.replace("\\", "/") + "\""
    


    if importMode == "Merge":
      abcImportString = abcImportStringStart
      abcImportString += " -connect \""
      abcImportString += str(sel[0])
      if len(sel) > 1:
        for s in sel[1:]:
          abcImportString += " " + str(s)
      abcImportString += "\""
      abcImportString += abcImportStringEnd
      cacheNode = mel.eval(abcImportString)

    if importMode == "Add under selection":
      cacheNode = ""
      for s in sel:
        abcImportString = abcImportStringStart
        abcImportString += " -reparent \""
        abcImportString += str(cmds.ls(s, long=True)[0])
        abcImportString += "\""
        abcImportString += abcImportStringEnd
        cacheNode += mel.eval(abcImportString) + " "
    
    if importMode == "Add under root":
      gr = cmds.group(empty=True, name=cFilename)
      abcImportString = abcImportStringStart
      abcImportString += " -reparent \""
      abcImportString += str(cmds.ls(gr, long=True)[0])
      abcImportString += "\""
      abcImportString += abcImportStringEnd
      cacheNode = mel.eval(abcImportString)
     
    print "# INFO: loaded cache   \"" + str(cFilepath) + "\""
    print "# INFO: cache node:    \"" + cacheNode + "\""
    self.results.setValue("cacheNode", cacheNode)