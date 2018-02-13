# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException

class IncrementAndSaveTool(DataBaseTool):

  ToolName = 'IncrementAndSave'
  ToolLabel = 'Increment and save'
  ToolCommand = 'incrementandsave'
  ToolDescription = 'Increments current scene file and saves a new file'
  ToolTooltip = 'Increments current scene file and saves a new file'

  def __init__(self, host):
    super (IncrementAndSaveTool, self).__init__(host)
    self._noUI = True

  # def initialize(self, **args):


  def increment(self, scenePath):

    sceneFolder = os.path.split(scenePath)[0]
    sceneFile = os.path.split(scenePath)[1]
    sceneFileName, sceneFileExt = os.path.splitext(sceneFile)

    if sceneFileName[-1].isdigit() == True: # check if there is already a version number at the end and increment if true
      i = 1
      while sceneFileName[-i].isdigit() == True:
        lastDigit = i
        i = i + 1
      oldFileVersion = sceneFileName[-lastDigit:]
      newFileVersion = str(int(oldFileVersion) + 1).rjust(len(oldFileVersion), "0")
      constantFileName = str(sceneFileName[:-lastDigit])
    else:
      constantFileName = str(sceneFileName)
      oldFileVersion = ""
      newFileVersion = "_01"

    savePath = os.path.join(sceneFolder, constantFileName + newFileVersion)
    return savePath + sceneFileExt

  def executeMaya(self):

    maya = self.host.apis['maya']
    scenePath = maya.cmds.file(q = True, sceneName = True)
    savePath = self.increment(scenePath)

    if os.path.exists(savePath) == True:
      QtWidgets = self.host.apis["QtWidgets"]
      msgBox = QtWidgets.QMessageBox
      q = msgBox.question(None, "Override...", "New Filename already exists.\nOverride?", msgBox.StandardButton.Yes | msgBox.StandardButton.Cancel)
      if q == msgBox.Yes:
        maya.cmds.file(rename = savePath)
        maya.cmds.file(save = True)
      else:
        print "User Aborted. Scene NOT saved."
    else:
      maya.cmds.file(rename = savePath)
      print savePath
      maya.cmds.file(save = True)
      maya.mel.eval("addRecentFile(\"%s\", \"mayaAscii\");" %(savePath.replace("\\", "/")))
