# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Tom Sporer. All rights reserved.
#

import os
import sys

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject

class UpdateLocatorTool(DataBaseTool):

  ToolName = 'UpdateLocator'
  ToolLabel = 'Update Locator'
  ToolCommand = 'updatelocator'
  ToolDescription = 'Update Locator'
  ToolTooltip = 'Update Locator'

  def __init__(self, host):
    super (UpdateLocatorTool, self).__init__(host)
    self._noUI = True


  def deleteAlembicNode(self, rootLocator):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    lr = cmds.listRelatives(rootLocator, allDescendents=True, path=True)
    for r in lr:
      if cmds.nodeType(r) == "mesh":
        lc = cmds.listConnections(r, connections=True)
        for c in lc:
          if "AlembicNode" in c:
            cmds.delete(c)
            break
        else:
          continue
      else:
        continue
      break


  def executeMaya(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    sel = cmds.ls(selection=True, long=True)
    for s in sel:
      self.deleteAlembicNode(s)

    #
    # To do:
    # delete assets (only keep pointee)
    #


