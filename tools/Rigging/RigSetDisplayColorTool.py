# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import re
import sys

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class RigSetDisplayColorTool(Tool):

  ToolName = 'RigSetDisplayColor'
  ToolLabel = 'Set Display Color'
  ToolCommand = 'rigsetdisplaycolor'
  ToolDescription = 'Set Display Color'
  ToolTooltip = 'Set Display Color'

  def __init__(self, host):
    super (RigSetDisplayColorTool, self).__init__(host)

  def initialize(self, **args):
    self.args.add(name="objects", type="str", value=args.get('objects', None), hidden=True)
    self.args.add(name="r", type="float", value=args.get('r', 1.0), range=[0, 1])
    self.args.add(name="g", type="float", value=args.get('g', 1.0), range=[0, 1])
    self.args.add(name="b", type="float", value=args.get('b', 1.0), range=[0, 1])

  def preexecute(self, **args):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    objects = args.get('objects', None)
    if objects is None:
      objects = ','.join(cmds.ls(sl=True, l=True))
      self.args.setValue('objects', objects)

  def execute(self):
    pm = self.host.apis['pymel'].core

    objects = self.args.getValue('objects')
    if not objects:
      return
    objects = objects.split(',')

    r = self.args.getValue('r')
    g = self.args.getValue('g')
    b = self.args.getValue('b')

    for o in objects:
      node = pm.ls(o)[0]
      node.overrideEnabled.set(True)
      node.overrideRGBColors.set(True)
      node.overrideColorRGB.set(r, g, b)
