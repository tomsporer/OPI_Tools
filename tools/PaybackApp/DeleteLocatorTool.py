# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Tom Sporer. All rights reserved.
#

import os
import sys
from random import randint

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject

class DeleteLocatorTool(DataBaseTool):

  ToolName = 'DeleteLocator'
  ToolLabel = 'Delete Locator'
  ToolCommand = 'deletelocator'
  ToolDescription = 'Delete Locator'
  ToolTooltip = 'Delete Locator'

  def __init__(self, host):
    super (DeleteLocatorTool, self).__init__(host)
    self._noUI = True


  def deleteAlembicNode(self, rootLocator):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    lr = cmds.listRelatives(rootLocator, allDescendents=True, path=True)
    for r in lr:
      if cmds.nodeType(r) == "mesh":
        lc = cmds.listConnections(r, connections=True)
        if not lc == None:
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


    sel = cmds.ls(selection=True)

    for loc in sel:
      self.deleteAlembicNode(loc)
      children = cmds.listRelatives(loc, children=True)
      for c in children:
        if cmds.referenceQuery(c, isNodeReferenced=True):
          for nonRef in cmds.listRelatives(c, children=True):
            if not cmds.referenceQuery(nonRef, isNodeReferenced=True):
              cmds.delete(nonRef)
          refFile = cmds.referenceQuery(c, filename=True)
          cmds.file(refFile, removeReference=True, force=True)
        elif not cmds.objectType(c, isType="locator"):
          cmds.delete(c)
      cmds.delete(loc)

