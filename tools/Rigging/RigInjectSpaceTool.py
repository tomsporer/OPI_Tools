# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import re
import sys

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class RigInjectSpaceTool(Tool):

  ToolName = 'RigInjectSpace'
  ToolLabel = 'Inject Space'
  ToolCommand = 'riginjectspace'
  ToolDescription = 'Inject Space'
  ToolTooltip = 'Inject Space'

  def __init__(self, host):
    super (RigInjectSpaceTool, self).__init__(host)
    self._noUI = True

  def initialize(self, **args):
    self.args.add(name="objects", type="str", value=args.get('objects', None), hidden=True)

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
    om = maya.api.OpenMaya

    radToDeg = 57.29577951308232

    expr = re.compile('^([a-zA-Z0-9]+)_([a-zA-Z0-9_]+)_([a-zA-Z0-9]+)$')

    objects = self.args.getValue('objects')
    if not objects:
      return
    objects = objects.split(',')
    objects = reversed(sorted(objects))

    for o in objects:
      sel = om.MSelectionList()
      sel.add(o)

      dagPath = sel.getDagPath(0)
      parentDagPath = om.MDagPath(dagPath)
      parentDagPath = parentDagPath.pop()
      parent = None
      if parentDagPath.isValid():
        parent = parentDagPath.fullPathName()

      transformObj = dagPath.transform()
      transform = om.MFnTransform(transformObj)

      m = expr.search(transform.name())
      if not m:
        print 'Warning: Object %s does not follow the naming convention - skipping.' % o
        continue

      side = m.group(1)
      name = m.group(2)
      role = m.group(3)

      if role == 'SPACE':
        newName = '%s_%sSpace_SPACE' % (side, name)
      else:
        newName = '%s_%s_SPACE' % (side, name)

      groupArgs = {'empty': True, 'name': newName}
      if parent:
        groupArgs['parent'] = parent
      group = cmds.group(**groupArgs)

      sel = om.MSelectionList()
      sel.add(group)
      groupDagPath = sel.getDagPath(0)
      groupObj = groupDagPath.transform()
      groupTransform = om.MFnTransform(groupObj)

      groupTransform.setTransformation(transform.transformation())

      cmds.parent(dagPath.fullPathName(), groupDagPath.fullPathName())
