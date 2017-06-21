# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Tom Sporer. All rights reserved.
#

import os
import sys

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject

class SelectAbcNodeTool(DataBaseTool):

  ToolName = 'SelectAbcNode'
  ToolLabel = 'Select Alembic Node'
  ToolCommand = 'selectabcnode'
  ToolDescription = 'Select Alembic Node'
  ToolTooltip = 'Select Alembic Node'

  def __init__(self, host):
    super (SelectAbcNodeTool, self).__init__(host)
    self._noUI = True


  def getAlembicNode(self, rootLocator):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    lr = cmds.listRelatives(rootLocator, allDescendents=True, path=True)
    for r in lr:
      if cmds.nodeType(r) == "mesh":
        lc = cmds.listConnections(r, connections=True)
        for c in lc:
          if "AlembicNode" in c:
            return c
            break
        else:
          continue
      else:
        continue
      break
    else:
      return None

  def executeMaya(self):
    db = self.host.apis['db']
    maya = self.host.apis['maya']
    cmds = maya.cmds

    sel = cmds.ls(selection=True)

    cmds.select(clear=True)

    abcNodes = []
    for s in sel:
      abcNode = self.getAlembicNode(s)
      if abcNode != None:
        abcNodes += [abcNode]

    cmds.select(abcNodes)