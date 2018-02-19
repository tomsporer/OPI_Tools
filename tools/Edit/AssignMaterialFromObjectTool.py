# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#


from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class AssignMaterialFromObjectTool(Tool):

  ToolName = 'AssignMaterialFromObject'
  ToolLabel = 'Assign Material from Object ( A <- B )'
  ToolCommand = 'assignmaterialfromobject'
  ToolDescription = 'Assign Material from last selected Object to selection'
  ToolTooltip = 'Assign Material from last selected Object to selection'

  def __init__(self, host):
    super (AssignMaterialFromObjectTool, self).__init__(host)
    self._noUI = True


  # def initialize(self, **args):


  def executeMaya(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    print "oh, hi"


    def getSGFromObject(obj):
      shape = cmds.listRelatives(obj, children=True, shapes=True, path=True)[0]
      mat = cmds.listConnections(shape, type="shadingEngine")[0]
      return mat


    sel = cmds.ls(selection=True)
    matToCopy = getSGFromObject(sel[-1])
    for s in sel[:-1]:
      cmds.sets(s, forceElement=matToCopy) 