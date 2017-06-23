# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Tom Sporer. All rights reserved.
#

import os
import sys

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject

class SoloLocatorTool(DataBaseTool):

  ToolName = 'SoloLocators'
  ToolLabel = 'Solo Locators'
  ToolCommand = 'sololocators'
  ToolDescription = 'Solo Locators'
  ToolTooltip = 'Solo Locators'

  def __init__(self, host):
    super (SoloLocatorTool, self).__init__(host)
    self._noUI = True


  def executeMaya(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    sel = cmds.ls(selection=True)
    references = cmds.file(q=True, reference=True )
    refNodes = []
    for ref in references:
      refNodes.append(cmds.referenceQuery(ref, referenceNode=True))

    if len(sel) == 0:
      refsToKeep = refNodes
    else:
      refsToKeep = []
      for s in sel:
        for child in cmds.listRelatives(s, children=True):
          if cmds.referenceQuery(child, isNodeReferenced=True):
            refNode = cmds.referenceQuery(child, referenceNode=True)
            refsToKeep.append(refNode)

    for refNode in refNodes:
      isLoaded = cmds.referenceQuery(refNode, isLoaded=True)
      if refNode in refsToKeep:
        if not isLoaded:
          cmds.file(loadReference=refNode)
      else:
        if isLoaded:
          cmds.file(unloadReference=refNode)

    cmds.select(sel)