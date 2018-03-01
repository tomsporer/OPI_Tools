# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

import os

class SmartSaveAsTool(Tool):

  ToolName = 'SmartSaveAs'
  ToolLabel = 'Smart Save As...'
  ToolCommand = 'smartsaveas'
  ToolDescription = 'Smart Save As'
  ToolTooltip = 'Smart Save As'

  def __init__(self, host):
    super (SmartSaveAsTool, self).__init__(host)
    self._noUI = False

  def initialize(self, **args):
    
    self.args.addStaticText("\tSmart Save As \t \t \t")
    self.args.addSpacer(13)
    self.args.add(name="currentScene", type="str", label="Current Scene Name", value="", enabled=False)
    self.args.beginRow("Current Folder")
    self.args.add(name="currentFolder", type="str", label="", value="", enabled=False)
    self.args.addButton("pickFolder", "...")
    self.args.endRow()
    self.args.beginRow("New Scene Name")
    self.args.add(name="newScene", type="str", label="", value="", enabled=True)
    self.args.addButton("plusOne", "+1")
    self.args.endRow()


  def preexecute(self):

    maya = self.host.apis['maya'] 
    cmds = maya.cmds

    scenePath = cmds.file(q = True, sceneName = True)

    if scenePath:
      sceneFolder, sceneFile = os.path.split(scenePath)
    else:
      sceneFile = "untitled"
      mostRecentFile = cmds.optionVar(q="RecentFilesList")[-1]
      mostRecentFolder = os.path.split(mostRecentFile)[0]
      sceneFolder = mostRecentFolder

    self.__scenePath = scenePath
    self.__sceneFolder = sceneFolder
    self.__sceneFile = sceneFile

    self.args.get("currentScene").value = sceneFile
    self.args.get("currentFolder").value = sceneFolder
    self.args.get("newScene").value = sceneFile


  def onButtonPressed(self, button):

    QtWidgets = self.host.apis["QtWidgets"]
    maya = self.host.apis['maya'] 
    cmds = maya.cmds
    sceneFolder = self.args.getValue("currentFolder")

    if button == "plusOne":
      sceneFile = self.args.getValue("newScene")
      incrementSceneFile = self.increment(sceneFile)
      self.args.setValue("newScene", incrementSceneFile)
    if button == "pickFolder":
      QFileDialog = QtWidgets.QFileDialog
      newFolder = QFileDialog.getExistingDirectory(None, "Tittle", sceneFolder)
      # newFolder = QFileDialog.getSaveFileName(None, "Tittle", dir=sceneFolder, filter="Maya Files (*.ma *.mb)")[0]
      if newFolder:
        self.args.setValue("currentFolder", newFolder)


  def increment(self, sceneFile):

    sceneFileName, sceneFileExt = os.path.splitext(sceneFile)

    for i in list(reversed(range(0, len(sceneFileName)))):
      if sceneFileName[i].isdigit():
        suffix = sceneFileName[i+1:]
        sansSuffix = sceneFileName[:i+1]
        i = 1
        while sansSuffix[-i].isdigit() == True:
          lastDigit = i
          i = i + 1
        oldFileVersion = sansSuffix[-lastDigit:]
        newFileVersion = str(int(oldFileVersion) + 1).rjust(len(oldFileVersion), "0")
        constantFileName = str(sansSuffix[:-lastDigit])
        break
    else:
      constantFileName = str(sceneFileName)
      oldFileVersion = ""
      newFileVersion = "_01"
      suffix = ""

    newSceneFile = constantFileName + newFileVersion + suffix + sceneFileExt
    return newSceneFile


  def executeMaya(self):

    maya = self.host.apis['maya'] 
    cmds = maya.cmds

    saveFolder = self.args.getValue("currentFolder")
    saveScene = self.args.getValue("newScene")

    fileTypeDict = {
      "mb" : "mayaBinary",
      "ma" : "mayaAscii"
    }

    saveSceneName, saveSceneExt = os.path.splitext(saveScene)
    if not saveSceneExt:
      saveSceneExt = ".ma"
      fileType = "mayaAscii"
    else:
      fileType = fileTypeDict[saveSceneExt[1:]]

    savePath = os.path.join(saveFolder, saveSceneName + saveSceneExt)

    if os.path.isfile(savePath):
      confirmDialog = cmds.confirmDialog( title='Save As', message=savePath + " already exists.\nDo you want to replace it?", button=['Yes', "No"], defaultButton='No', cancelButton='No', dismissString='No' )
      if confirmDialog != 'Yes':
        self.invokeWithUI()

    cmds.file(rename = savePath)
    cmds.file(type = fileType)
    cmds.file(save = True)
    maya.mel.eval("addRecentFile(\"%s\", \"%s\");" %(savePath.replace("\\", "/"), fileType))
