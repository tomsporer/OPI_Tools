# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Tom Sporer. All rights reserved.
#

import os
import sys
from random import randint

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject

class RenameLocatorTool(DataBaseTool):

  ToolName = 'RenameLocator'
  ToolLabel = 'Rename Locator'
  ToolCommand = 'renamelocator'
  ToolDescription = 'Rename Locator'
  ToolTooltip = 'Rename Locator'

  def __init__(self, host):
    super (RenameLocatorTool, self).__init__(host)

  def initialize(self, **args):

    self.args.addStaticText("\tRename Locator(s) \t \t \t")
    self.args.addSpacer(13)
    self.args.add(name="project", type="instance", template="project", comboSqlQuery="SELECT * FROM project WHERE project.name == 'Payback_App'", enabled=False, hidden=True)
    self.args.add(name="object", type="str", label="", value="Pointee", enabled=False)
    self.args.add(name="type", type="str", label="Pointee Type", combo=["Generic", "Special"], value="Generic", enabled=True)
    self.args.add(name="cache", type="str", label="Cache", combo=[""], value="", enabled=True)
    self.args.beginRow("New Name")
    self.args.add(name="newName", type="str", label="", enabled=False)
    self.args.addStaticText("_locator")
    self.args.endRow()
    self.args.add(name="allRandom", type="bool", label="All Random", value=False)

  def preexecute(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    sel = cmds.ls(selection=True)

    self.fillCacheCombo()
    self.updateNewName()

  def fillCacheCombo(self):
    db = self.host.apis['db']
    project = db.queryOne("project", name="Payback_App")
    cObject = self.args.getValue("object")
    cType = self.args.getValue("type")
    cQuery = db.query("pointee_cache", project=project, object=cObject, type=cType)
    cCombo = []
    if cType == "Generic":
      cCombo += ["Random"]
    for cQ in cQuery:
      cCombo.append(cQ.name)
    self.args.get("cache")._setCombo(cCombo, cCombo[0])

  def updateNewName(self):
    lObject = self.args.getValue("object")
    lType = self.args.getValue("type")
    lCache = self.args.getValue("cache")
    self.args.get("newName").value = lObject + "_" + lType + "_" + lCache

  def onValueChanged(self, arg):
    if arg.name == "type":
      self.fillCacheCombo()
    if arg.name == "allRandom":
      self.args.get("type").enabled = not arg.value
      self.args.get("cache").enabled = not arg.value

    self.updateNewName()

  def executeMaya(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds
    allRandom = self.args.getValue("allRandom")
    
    if allRandom:
      db = self.host.apis['db']
      project = db.queryOne("project", name="Payback_App")
      cObject = self.args.getValue("object")
      cQuery = db.query("pointee_cache", project=project, object=cObject)

    sel = cmds.ls(selection=True)
    for s in sel:
      checkLoc = cmds.listRelatives(s, shapes=True)[0]
      if not cmds.objectType(checkLoc, isType="locator"):
        continue
      if allRandom:
        cQueryRand = cQuery[randint(0, len(cQuery)-1)]
        newName = cQueryRand.object + "_" + cQueryRand.type + "_" + cQueryRand.name + "_locator"
      else:
        newName = self.args.getValue("newName") + "_locator"

      cmds.rename(s, newName)
