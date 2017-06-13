# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import re
import sys

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class RigCreateConstraintTargetTool(Tool):

  ToolName = 'RigCreateConstraintTarget'
  ToolLabel = 'Create Constraint Target'
  ToolCommand = 'rigcreateconstrainttarget'
  ToolDescription = 'Create Constraint Target'
  ToolTooltip = 'Create Constraint Target'

  def __init__(self, host):
    super (RigCreateConstraintTargetTool, self).__init__(host)
    self._noUI = True

  def initialize(self, **args):
    self.args.add(name="parent", type="str", value=args.get('parent', None), hidden=True)

  def preexecute(self, **args):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    parent = args.get('parent', None)
    if parent is None:
      parents = cmds.ls(sl=True)
      if len(parents) > 0:
        self.args.setValue('parent', parents[0])
      else:
        self.args.setValue('parent', '')

  def execute(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds
    om = maya.api.OpenMaya
    pm = self.host.apis['pymel'].core

    parent = self.args.getValue('parent')

    name = parent.rpartition('|')[2].rpartition('_')[0] + '_CNS'
    cmds.group(empty=True, name=name, parent=parent)

