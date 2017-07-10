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
      if ":" in each:
        name = each.split(":")[1]
      else:
        name = each
      data = jo.get(name=name)
      if not data == None:
        axis = ["X", "Y", "Z"]
        for i in range(3):
          try:
            cmds.setAttr(each + ".translate" + axis[i], data.translate[i])
          except:
            print "# WARNING: could not set translate%s for %s." %(axis[i], each)
          try:
            cmds.setAttr(each + ".rotate" + axis[i], data.rotate[i])
          except:
            print "# WARNING: could not set rotate%s for %s." %(axis[i], each)
          try:
            cmds.setAttr(each + ".scale" + axis[i], data.scale[i])
          except:
            print "# WARNING: could not set scale%s for %s." %(axis[i], each)
      else:
        print "# WARNING: No transform data found for %s." %(each)

