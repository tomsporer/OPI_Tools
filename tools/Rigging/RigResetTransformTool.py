# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import re
import sys

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class RigResetTransformTool(Tool):

  ToolName = 'RigResetTransform'
  ToolLabel = 'Reset Transform'
  ToolCommand = 'rigresettransform'
  ToolDescription = 'Reset Transform'
  ToolTooltip = 'Reset Transform'

  def __init__(self, host):
    super (RigResetTransformTool, self).__init__(host)
    self._noUI = True

  def initialize(self, **args):
    self.args.add(name="objects", type="str", value=args.get('objects', None), hidden=True)
    self.args.add(name="translation", type="bool", value=args.get('translation', True))
    self.args.add(name="rotation", type="bool", value=args.get('rotation', True))
    self.args.add(name="scaling", type="bool", value=args.get('scaling', True))

  def preexecute(self, **args):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    objects = args.get('objects', None)
    if objects is None:
      objects = ','.join(cmds.ls(sl=True, l=True))
      self.args.setValue('objects', objects)

  def execute(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    objects = self.args.getValue('objects')
    if not objects:
      return
    objects = objects.split(',')

    translation = self.args.getValue('translation')
    rotation = self.args.getValue('rotation')
    scaling = self.args.getValue('scaling')

    objects = reversed(sorted(objects))

    for o in objects:
      axes = ['X', 'Y', 'Z']
      if translation:
        for axis in axes:
          cmds.setAttr("%s.translate%s" % (o, axis), 0.0)
      if rotation:
        for axis in axes:
          cmds.setAttr("%s.rotate%s" % (o, axis), 0.0)
      if scaling:
        for axis in axes:
          cmds.setAttr("%s.scale%s" % (o, axis), 1.0)
