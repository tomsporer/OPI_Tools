# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import re
import sys

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class RigCreateControlTool(Tool):

  ToolName = 'RigCreateControl'
  ToolLabel = 'Create Rig Control'
  ToolCommand = 'rigcreatecontrol'
  ToolDescription = 'Create Rig Control'
  ToolTooltip = 'Create Rig Control'

  def __init__(self, host):
    super (RigCreateControlTool, self).__init__(host)
    self.expr = re.compile('^([a-zA-Z0-9]+)_([a-zA-Z0-9_]+)_([a-zA-Z0-9]+)$')

  def initialize(self, **args):
    self.args.add(name="parent", type="str", value=args.get('parent', None), hidden=True)
    self.args.add(name="side", type="str", value=args.get('side', None), combo=['L', 'M', 'R'])
    self.args.add(name="name", type="str", value=args.get('name', 'control'))
    self.args.add(name="type", type="str", value=args.get('type', 'square'), combo=['square', 'circle', 'cube', 'sphere', 'diamond', 'pyramid', 'pin', 'arrow', '2 arrows', '3 arrows', '4 arrows'])
    self.args.add(name="resolution", type="int", value=args.get('resolution', 16))
    self.args.add(name="scale", type="float", value=args.get('scale', 1), range=[0.1, 8])
    self.results.add(name='curve', type='str')

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

    side = args.get('side', None)
    if not side:
      self.args.setValue('side', 'M')
      parent = self.args.getValue('parent')
      if parent:
        name = parent.rpartition('|')[2]
        m = self.expr.search(name)
        if m:
          self.args.setValue('side', m.group(1))

  def execute(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds
    om = maya.api.OpenMaya
    pm = self.host.apis['pymel'].core

    parent = self.args.getValue('parent')
    side = self.args.getValue('side')
    name = self.args.getValue('name')
    controlType = self.args.getValue('type')
    resolution = self.args.getValue('resolution')
    scale = self.args.getValue('scale')

    name = "%s_%s%s_%s" % (side, name[0].upper(), name[1:], "CTRL")

    pi = 3.141592653589793

    points = []
    closed = True

    if controlType == 'square':
      points.append([-1, 0, -1])
      points.append([-1, 0, 1])
      points.append([1, 0, 1])
      points.append([1, 0, -1])

    elif controlType == 'circle':
      if resolution < 5:
        resolution = 5
      for i in range(resolution):
        q = om.MQuaternion(pi * float(i * 2) / float(resolution), om.MVector(0, 1, 0))
        v = om.MVector(1, 0, 0).rotateBy(q)
        points.append([v.x, v.y, v.z])

    elif controlType == 'cube':
      points.append([-1, -1, -1])
      points.append([-1, -1,  1])
      points.append([-1,  1,  1])
      points.append([ 1,  1,  1])
      points.append([ 1, -1,  1])
      points.append([ 1, -1, -1])
      points.append([ 1,  1, -1])
      points.append([-1,  1, -1])
      points.append([-1,  1,  1])
      points.append([-1, -1,  1])
      points.append([ 1, -1,  1])
      points.append([ 1, -1, -1])
      points.append([-1, -1, -1])
      points.append([-1,  1, -1])
      points.append([ 1,  1, -1])
      points.append([ 1,  1,  1])
      closed = False

    elif controlType == 'sphere':
      if resolution < 5:
        resolution = 5
      for i in range(resolution):
        q = om.MQuaternion(pi * float(i * 2) / float(resolution), om.MVector(0, 1, 0))
        v = om.MVector(1, 0, 0).rotateBy(q)
        points.append([v.x, v.y, v.z])
      for i in range(resolution):
        q = om.MQuaternion(pi * float(i * 2) / float(resolution), om.MVector(0, 0, 1))
        v = om.MVector(1, 0, 0).rotateBy(q)
        points.append([v.x, v.y, v.z])

    elif controlType == 'diamond':
      points.append([1, 0, -1])
      points.append([-1, 0, -1])
      points.append([-1, 0, 1])
      points.append([1, 0, 1])
      points.append([1, 0, -1])
      points.append([0, 1, 0])
      points.append([-1, 0, -1])
      points.append([0, -1, 0])
      points.append([-1, 0, 1])
      points.append([0, 1, 0])
      points.append([1, 0, 1])
      points.append([0, -1, 0])
      points.append([1, 0, -1])
      points.append([0, 1, 0])
      closed = False

    elif controlType == 'pyramid':
      points.append([1, 0, 1])
      points.append([-1, 0, -1])
      points.append([0, 1, 0])
      points.append([-1, 0, 1])
      points.append([-1, 0, -1])
      points.append([1, 0, -1])
      points.append([0, 1, 0])
      points.append([1, 0, 1])
      points.append([1, 0, -1])
      points.append([-1, 0, 1])

    elif controlType == 'pin':
      points.append([0, 0, 0])
      points.append([0, 0, -2])
      points.append([-1, 0, -2])
      points.append([-1, 0, -4])
      points.append([1, 0, -4])
      points.append([1, 0, -2])
      points.append([0, 0, -2])
      points.append([0, 0, 0])

    elif controlType == 'arrow':
      points.append([-1, 0, -0.5])
      points.append([-1, 0, 0.5])
      points.append([0, 0, 0.5])
      points.append([0, 0, 1.0])
      points.append([1.0, 0, 0.0])
      points.append([0, 0, -1.0])
      points.append([0, 0, -0.5])

    elif controlType == '2 arrows':
      points.append([-0.5, 0, 0.5])
      points.append([0.5, 0, 0.5])
      points.append([0.5, 0, 1.0])
      points.append([1.5, 0, 0.0])
      points.append([0.5, 0, -1.0])
      points.append([0.5, 0, -0.5])
      points.append([-0.5, 0, -0.5])
      points.append([-0.5, 0, -1.0])
      points.append([-1.5, 0, 0.0])
      points.append([-0.5, 0, 1.0])

    elif controlType == '3 arrows':
      points.append([-1.5, 0, 0.5])
      points.append([-0.5, 0, 0.5])
      points.append([-0.5, 0, 1.5])
      points.append([-1.0, 0, 1.5])
      points.append([0.0, 0, 2.5])
      points.append([1.0, 0, 1.5])
      points.append([0.5, 0, 1.5])
      points.append([0.5, 0, 0.5])
      points.append([1.5, 0, 0.5])
      points.append([1.5, 0, 1.0])
      points.append([2.5, 0, 0.0])
      points.append([1.5, 0, -1.0])
      points.append([1.5, 0, -0.5])
      points.append([0.5, 0, -0.5])
      points.append([-0.5, 0, -0.5])
      points.append([-1.5, 0, -0.5])
      points.append([-1.5, 0, -1.0])
      points.append([-2.5, 0, 0.0])
      points.append([-1.5, 0, 1.0])

    elif controlType == '4 arrows':
      points.append([-1.5, 0, 0.5])
      points.append([-0.5, 0, 0.5])
      points.append([-0.5, 0, 1.5])
      points.append([-1.0, 0, 1.5])
      points.append([0.0, 0, 2.5])
      points.append([1.0, 0, 1.5])
      points.append([0.5, 0, 1.5])
      points.append([0.5, 0, 0.5])
      points.append([1.5, 0, 0.5])
      points.append([1.5, 0, 1.0])
      points.append([2.5, 0, 0.0])
      points.append([1.5, 0, -1.0])
      points.append([1.5, 0, -0.5])
      points.append([0.5, 0, -0.5])
      points.append([0.5, 0, -1.5])
      points.append([1.0, 0, -1.5])
      points.append([0.0, 0, -2.5])
      points.append([-1.0, 0, -1.5])
      points.append([-0.5, 0, -1.5])
      points.append([-0.5, 0, -0.5])
      points.append([-1.5, 0, -0.5])
      points.append([-1.5, 0, -1.0])
      points.append([-2.5, 0, 0.0])
      points.append([-1.5, 0, 1.0])

    if len(points) == 0:
      self.logError('No points for control type %s' % controlType)
      return

    # apply the scaling
    for i in range(len(points)):
      points[i][0] *= scale
      points[i][1] *= scale
      points[i][2] *= scale

    curve = pm.curve(per=False, p=points, degree=1, name=name)
    if closed:
      pm.closeCurve(curve, preserveShape=True, replaceOriginal=True)

    cmds.select(str(curve))

    if parent:
      cmds.parent(str(curve), parent)

      sel = om.MSelectionList()
      sel.add(str(curve))

      dagPath = sel.getDagPath(0)
      transformObj = dagPath.transform()
      transform = om.MFnTransform(transformObj)
      transform.setTransformation(om.MTransformationMatrix(om.MMatrix().setToIdentity()))

    self.results.setValue('curve', str(curve))
