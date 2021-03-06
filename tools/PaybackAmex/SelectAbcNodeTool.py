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

    foundAbcNodes = []
    lr = cmds.listRelatives(rootLocator, allDescendents=True, path=True)
    for r in lr:
      lc = cmds.listConnections(r, connections=True)
      if not lc == None:
        for c in lc:
          if "AlembicNode" in c:
            foundAbcNodes.append(c)
            break

    return list(set(foundAbcNodes))

  def executeMaya(self):
    db = self.host.apis['db']
    maya = self.host.apis['maya']
    cmds = maya.cmds

    sel = cmds.ls(selection=True)

    cmds.select(clear=True)

    abcNodes = []
    for s in sel:
      abcNode = self.getAlembicNode(s)
      abcNodes += abcNode

    cmds.select(abcNodes)