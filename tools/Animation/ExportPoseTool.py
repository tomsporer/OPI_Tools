# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject

class ExportPoseTool(DataBaseTool):

  ToolName = 'ExportPose'
  ToolLabel = 'Export Pose'
  ToolCommand = 'exportpose'
  ToolDescription = 'Export Pose'
  ToolTooltip = 'Export Pose'

  def __init__(self, host):
    super (ExportPoseTool, self).__init__(host)
    self._noUI = True


  def executeMaya(self):

    db = self.host.apis['db']
    maya = self.host.apis['maya'] 
    cmds = maya.cmds

    # sceneFile = cmds.file(q=True, sn=True)
    jsonPath = cmds.fileDialog2(fileFilter="Json (*.json)", fileMode=0, dialogStyle=2)[0]
    jo = JsonObject(jsonPath)

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

    if os.path.exists(jsonPath):
      jo.clear()

    for each in selList:
      jo.__setattr__(name=each, value=self.getTransforms(each))

    jo.write()


  def getTransforms(self, obj):
    maya = self.host.apis['maya'] 
    cmds = maya.cmds
    transforms = {}
    transforms['translate'] = list(cmds.getAttr(obj + ".translate")[0])
    transforms['rotate'] = list(cmds.getAttr(obj + ".rotate")[0])
    transforms['scale'] = list(cmds.getAttr(obj + ".scale")[0])

    return transforms


