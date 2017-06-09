# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import re
import sys

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class RigMirrorTransformComponentTool(Tool):

  ToolName = 'RigMirrorTransformComponent'
  ToolLabel = 'Mirror Transform Component'
  ToolCommand = 'RigMirrorTransformComponent'
  ToolDescription = 'Mirror Transform Component'
  ToolTooltip = 'Mirror Transform Component'

  def __init__(self, host):
    super (RigMirrorTransformComponentTool, self).__init__(host)

  def initialize(self, **args):
    self.args.add(name="objects", type="str", value=args.get('objects', None), hidden=True)
    self.args.add(name="translateX", type="bool", value=args.get('translateX', True))
    self.args.add(name="translateY", type="bool", value=args.get('translateY', False))
    self.args.add(name="translateZ", type="bool", value=args.get('translateZ', False))
    self.args.add(name="rotateX", type="bool", value=args.get('rotateX', False))
    self.args.add(name="rotateY", type="bool", value=args.get('rotateY', False))
    self.args.add(name="rotateZ", type="bool", value=args.get('rotateZ', False))
    self.args.add(name="scaleX", type="bool", value=args.get('scaleX', False))
    self.args.add(name="scaleY", type="bool", value=args.get('scaleY', False))
    self.args.add(name="scaleZ", type="bool", value=args.get('scaleZ', False))

  def preexecute(self, **args):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    objects = args.get('objects', None)
    if objects is None:
      objects = ','.join(cmds.ls(sl=True))
      self.args.setValue('objects', objects)

  def execute(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    objects = self.args.getValue('objects').split(',')

    options = {
      'translateX': self.args.getValue('translateX'),
      'translateY': self.args.getValue('translateY'),
      'translateZ': self.args.getValue('translateZ'),
      'rotateX': self.args.getValue('rotateX'),
      'rotateY': self.args.getValue('rotateY'),
      'rotateZ': self.args.getValue('rotateZ'),
      'scaleX': self.args.getValue('scaleX'),
      'scaleY': self.args.getValue('scaleY'),
      'scaleZ': self.args.getValue('scaleZ'),
    }

    objects = reversed(sorted(objects))

    for o in objects:
      for attr in options:
        if not options[attr]:
          continue
        value = cmds.getAttr('%s.%s' % (o, attr))
        value = -value
        cmds.setAttr('%s.%s' % (o, attr), value)
