# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import re
import sys

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class RigFindDuplicateNamesTool(Tool):

  ToolName = 'RigFindDuplicateNames'
  ToolLabel = 'Find Duplicate Names'
  ToolCommand = 'rigfindduplicatenames'
  ToolDescription = 'Find Objects with the same Name'
  ToolTooltip = 'Find Objects with the same Name'

  def __init__(self, host):
    super (RigFindDuplicateNamesTool, self).__init__(host)
    self._noUI = True


  def execute(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    sel = cmds.ls(selection=True)
    if len(sel) == 0:
      sel = cmds.ls(dagObjects=True)
    objs = []
    for s in sel:
      objs.append(s.split("|")[-1])

    duplicates = objs
    uniqueList = list(set(objs))
    for item in uniqueList:
      duplicates.remove(item)
        
    if duplicates != []:
      print "# INFO: Duplicate Names Found:"
      print duplicates
    else:
      print "# INFO: No duplicates found"