# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Tom Sporer. All rights reserved.
#

import os

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException

class updateCachesTool(DataBaseTool):

  ToolName = 'UpdateCaches'
  ToolLabel = 'Update Caches...'
  ToolCommand = 'updatecaches'
  ToolDescription = 'Update Caches'
  ToolTooltip = 'Update Caches'

  def __init__(self, host):
    super (updateCachesTool, self).__init__(host)
    self._noUI = False


  def initialize(self, **args):

    self.args.addStaticText("\tUpdate Caches \t")
    self.args.addSpacer(13)


  def preexecute(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds


    def increment(scenePath):
      sceneFolder, sceneFile = os.path.split(scenePath)
      sceneFileName, sceneFileExt = os.path.splitext(sceneFile)

      if sceneFileName[-1].isdigit() == True: # check if there is already a version number at the end and increment if true
        i = 1
        while sceneFileName[-i].isdigit() == True:
          lastDigit = i
          i = i + 1
        oldFileVersion = sceneFileName[-lastDigit:]
        newFileVersion = str(int(oldFileVersion) + 1).rjust(len(oldFileVersion), "0")
        constantFileName = str(sceneFileName[:-lastDigit])

      savePath = os.path.join(sceneFolder, constantFileName + newFileVersion)
      return savePath + sceneFileExt


    abcDict = {}
    abcNodes = cmds.ls("*AlembicNode*")
    for abcNode in abcNodes:
      nodeIn = cmds.listConnections(abcNode, source=True, destination=False)
      nodeOut = cmds.listConnections(abcNode, source=False, destination=True)
      if len(nodeIn) <= 1 and not nodeOut:
        # delete alembic nodes with no connection
        cmds.delete(abcNode)
      else:
        abcName = abcNode.split("_AlembicNode")[0]
        abcFile = cmds.getAttr(abcNode + ".abc_File")
        abcPlus = increment(abcFile)
        while os.path.exists(abcPlus):
          abcFile = abcPlus
          abcDict[abcName] = [abcNode] + [abcFile] + nodeOut
          abcPlus = increment(abcFile)

    if len(abcDict.keys()) == 0:
      # dialog = cmds.confirmDialog(title="No Updates Found.", message="All Caches are up to date.\n\nNo updates needed.", button=["Ok"], defaultButton="Ok", cancelButton="Ok", dismissString="Ok")
      self.args.addStaticText("No updates needed.")
    else:
      if len(abcDict.keys()) > 0:
        self.args.add(name="updateAll", type="bool", label="All", value=True)
      for abc in sorted(abcDict.keys()):
        lastVersion = os.path.splitext(abcDict[abc][1])[0][-3:]
        self.args.beginRow(abc)
        self.args.add(name=abc, label="", type="bool", value=True)
        self.args.addStaticText("update to v%s" %(lastVersion))
        self.args.endRow()

    self.__abcDict = abcDict

  def onValueChanged(self, arg):

    if arg.name == "updateAll":
      for otherArg in self.args:
        if otherArg.name is not "updateAll":
          self.args.setValue(otherArg.name, arg.value)
    else:
      if arg.value == False:
        self.args.setValue("updateAll", False)
      else:
        for otherArg in self.args:
          if otherArg.name == arg.name or otherArg.name == "updateAll":
            continue
          else:
            if otherArg.value == False:
              break
        else:
          self.args.setValue("updateAll", True)



  def executeMaya(self):
    maya = self.host.apis['maya']
    db = self.host.apis['db']
    cmds = maya.cmds
    mel = maya.mel

    abcDict = self.__abcDict

    for abc in abcDict.keys():
      if self.args.getValue(abc):
        abcNode = abcDict[abc][0]
        abcFile = abcDict[abc][1]
        linkedObjects = abcDict[abc][2:]
        cmds.delete(abcNode)

        abcImportString = "AbcImport -mode import -connect \""
        abcImportString += linkedObjects[0]
        if len(linkedObjects) > 1:
          for obj in linkedObjects[1:]:
            abcImportString += " " + str(obj)
        abcImportString += "\""
        abcImportString += " \"%s\"" %(abcFile.replace("\\", "/"))
        cacheNode = mel.eval(abcImportString)
