# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#


from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class MakeMaterialLocalTool(Tool):

  ToolName = 'MakeMaterialLocal'
  ToolLabel = 'Make Material local'
  ToolCommand = 'makemateriallocal'
  ToolDescription = 'Make shared Material unique and connect to Object'
  ToolTooltip = 'Make shared Material unique and connect to Object'

  def __init__(self, host):
    super (MakeMaterialLocalTool, self).__init__(host)
    self._noUI = True


  # def initialize(self, **args):


  def executeMaya(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    def getSGFromShape(obj):
      mat = cmds.listConnections(shape, type="shadingEngine")[0]
      return mat

    sel = cmds.ls(selection=True)
    for s in sel:
      shape = cmds.listRelatives(s, children=True, shapes=True, path=True)[0]
      sharedSG = getSGFromShape(shape)
      localSG = cmds.duplicate(sharedSG, upstreamNodes=True)[0]
      print localSG
      cmds.sets(shape, forceElement=localSG)