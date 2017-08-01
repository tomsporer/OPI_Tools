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
    self.args.addSpacer(7,1)
    self.args.add(name="bGespannt", type="bool", label="Gespannt", value=True, enabled=False)
    self.args.add(name="bJoy", type="bool", label="Joy", value=True, enabled=False)
    self.args.add(name="bNormal", type="bool", label="Normal", value=True, enabled=False)

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
    cQuery = db.query("pointee_cache", object=cObject, type=cType)
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
      self.args.get("bgespannt").enabled = arg.value
      self.args.get("bjoy").enabled = arg.value
      self.args.get("bnormal").enabled = arg.value

    self.updateNewName()

  def executeMaya(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds
    allRandom = self.args.getValue("allRandom")
    bGespannt = self.args.getValue("bGespannt")
    bJoy = self.args.getValue("bJoy")
    bNormal = self.args.getValue("bNormal")
    
    if allRandom:
      db = self.host.apis['db']
      project = db.queryOne("project", name="Payback_App")
      cObject = self.args.getValue("object")
      cQueryG = db.query("pointee_cache", object=cObject, type="Generic")
      cQueryS = db.query("pointee_cache", object=cObject, type="Special")
      cQuery = cQueryG + cQueryS
      cList = []
      for c in cQuery:
        if bGespannt and "gespannt" in c.name.lower():
          cList.append(c)
        if bJoy and "joy" in c.name.lower():
          cList.append(c)
        if bNormal and "gespannt" not in c.name.lower() and "joy" not in c.name.lower():
          cList.append(c)

    sel = cmds.ls(selection=True)
    for s in sel:
      checkLoc = cmds.listRelatives(s, shapes=True)[0]
      if not cmds.objectType(checkLoc, isType="locator"):
        continue
      if allRandom:
        cQueryRand = cList[randint(0, len(cList)-1)]
        newName = cQueryRand.object + "_" + cQueryRand.type + "_" + cQueryRand.name + "_locator"
      else:
        newName = self.args.getValue("newName") + "_locator"

      cmds.rename(s, newName)
