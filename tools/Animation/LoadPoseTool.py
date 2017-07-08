# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject

class LoadPoseTool(DataBaseTool):

  ToolName = 'LoadPose'
  ToolLabel = 'Load Pose'
  ToolCommand = 'loadpose'
  ToolDescription = 'Load Pose'
  ToolTooltip = 'Load Pose'

  def __init__(self, host):
    super (LoadPoseTool, self).__init__(host)
    self._noUI = True


  def executeMaya(self):

    db = self.host.apis['db']
    maya = self.host.apis['maya'] 
    cmds = maya.cmds

    # sceneFile = cmds.file(q=True, sn=True)
    jsonPath = cmds.fileDialog2(fileFilter="Json (*.json)", fileMode=1, dialogStyle=2)[0]
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

    for each in selList:
      data = jo.get(name=each)
      if not data == None:
        cmds.setAttr(each + ".translate", data.translate[0], data.translate[1], data.translate[2])
        cmds.setAttr(each + ".rotate", data.rotate[0], data.rotate[1], data.rotate[2])
        cmds.setAttr(each + ".scale", data.scale[0], data.scale[1], data.scale[2])
      else:
        print "# WARNING: No transform data found for %s" %(each)

