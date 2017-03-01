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
    sceneFileName = os.path.splitext(sceneFile)[0]

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
    return savePath


  def execute(self):

    if self.host.apis.has_key("maya"):
      maya = self.host.apis['maya']
      scenePath = maya.cmds.file(q = True, sceneName = True)
      savePath = self.increment(scenePath)
      maya.cmds.file(rename = savePath)
      maya.cmds.file(save = True)
    elif self.host.apis.has_key("xsi"):
      xsi = self.host.apis['xsi']
      scenePath = xsi.ActiveProject.ActiveScene.filename.value
      savePath = self.increment(scenePath)
      xsi.SaveSceneAs(savePath + ".scn", "")


    #
    # QtWidgets.QMessageBox
    #
    
    # if os.path.exists(savePath) == True:
    #   askForOverride = XSIUIToolkit.MsgBox( "New Filename already exists. Override?" , 32 | 1, "Override...")
    #   if askForOverride == 1:
    #     saveAs()
    #   else:
    #     log("User Aborted. Scene NOT saved.", 4)
    # else:
    #   saveAs()

