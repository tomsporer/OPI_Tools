# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import re
import sys

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class RigRenameTool(Tool):

  ToolName = 'RigRename'
  ToolLabel = 'Rename Elements'
  ToolCommand = 'rigrename'
  ToolDescription = 'Rig Rename'
  ToolTooltip = 'Rig Rename'

  def __init__(self, host):
    super (RigRenameTool, self).__init__(host)

  def initialize(self, **args):
    self.args.add(name="objects", type="str", value=args.get('objects', None), hidden=True)
    self.args.add(name="side", type="str", value=args.get('side', '[unchanged]'), combo=['[unchanged]', 'L', 'M', 'R'])
    self.args.add(name="name", type="str", value=args.get('name', '[unchanged]'))
    self.args.add(name="replaceWith", label="Replace With", type="str", value=args.get('replaceWith', ''))
    self.args.add(name="keepNameSuffix", label='Keep Name Suffix', type="bool", value=args.get('keepNameSuffix', True))
    self.args.add(name="role", type="str", value=args.get('role', '[unchanged]'), combo=['[unchanged]', 'CTRL', 'JNT', 'SPACE', 'PAR', 'GEO', 'CNS'])

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

    side = self.args.getValue('side')
    name = self.args.getValue('name')
    replaceWith = self.args.getValue('replaceWith')
    keepNameSuffix = self.args.getValue('keepNameSuffix')
    role = self.args.getValue('role')

    defaultSide = side
    if defaultSide.startswith('['):
      defaultSide = 'M'
    defaultRole = role
    if defaultRole.startswith('['):
      defaultRole = 'PAR'

    expr = re.compile('^([a-zA-Z0-9]+)_([a-zA-Z0-9_]+)_([a-zA-Z]+)([0-9]*)$')
    nameSuffixExpr = re.compile('([0-9]+)$')

    objects = reversed(sorted(objects))

    for o in objects:
      n = o.rpartition('|')[2]
      m = expr.search(n)
      if m is None:
        print "Warning: Object '%s' does not follow the naming convention. Adapting..."

        if name != '[unchanged]':
          if keepNameSuffix:
            m2 = nameSuffixExpr.search(n)
            if m2:
              n = "%s%s" % (name, m2.group(1))
            else:
              n = name
        n = "%s_%s_%s" % (defaultSide, n, defaultRole)
      else:

        n1 = m.group(1).upper()
        if side == '[unchanged]':
          if not n1 in self.args.get('side').combo:
            print "Warning: Object '%s' uses an unsupported side:'%s'" % (o, n1)
        else:
          n1 = side

        n2 = m.group(2)
        if name != '[unchanged]' and not replaceWith:
          if keepNameSuffix:
            m2 = nameSuffixExpr.search(n2)
            if m2:
              n2 = "%s%s" % (name, m2.group(1))
            else:
              n2 = name
          else:
            n2 = name
        n2 = n2.replace('_', '')
        n2 = n2[0].upper() + n2[1:]

        n3 = m.group(3).upper()
        if role == '[unchanged]':
          if not n3 in self.args.get('role').combo:
            print "Warning: Object '%s' uses an unsupported role:'%s'" % (o, n3)
        else:
          n3 = role

        n = "%s_%s_%s" % (n1, n2, n3)

      if replaceWith:
        n = n.replace(name, replaceWith)

      print n

      if n == o.rpartition('|')[2]:
        continue

      cmds.rename(o, n)
