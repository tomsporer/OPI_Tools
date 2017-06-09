# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import re
import sys

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class RigResetPivotTool(Tool):

  ToolName = 'RigResetPivot'
  ToolLabel = 'Reset Pivot'
  ToolCommand = 'RigResetPivot'
  ToolDescription = 'Reset Pivot'
  ToolTooltip = 'Reset Pivot'

  def __init__(self, host):
    super (RigResetPivotTool, self).__init__(host)
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

    objects = self.args.getValue('objects').split(',')
    objects = reversed(sorted(objects))

    for o in objects:
      sel = om.MSelectionList()
      sel.add(o)

      dagPath = sel.getDagPath(0)
      parentDagPath = om.MDagPath(dagPath)
      parentDagPath = parentDagPath.pop()

      transformObj = dagPath.transform()
      transform = om.MFnTransform(transformObj)

      # pull the transform off the MfnTransform - to include the pivot
      m = transform.transformation()
      p = transform.rotatePivot(om.MSpace.kTransform)
      p = om.MVector(p.x, p.y, p.z)
      pivot = om.MTransformationMatrix()
      pivot.setTranslation(p, om.MSpace.kTransform)
      m = om.MTransformationMatrix(m.asMatrix() * pivot.asMatrix())

      if parentDagPath.isValid():
        parentM = parentDagPath.inclusiveMatrixInverse()
        m = om.MTransformationMatrix(m.asMatrix() * parentM)

      transform.setRotatePivot(om.MPoint(0, 0, 0, 1), om.MSpace.kTransform, True)
      transform.setScalePivot(om.MPoint(0, 0, 0, 1), om.MSpace.kTransform, True)

      cmds.setAttr("%s.translateX" % o, m.translation(om.MSpace.kTransform).x)
      cmds.setAttr("%s.translateY" % o, m.translation(om.MSpace.kTransform).y)
      cmds.setAttr("%s.translateZ" % o, m.translation(om.MSpace.kTransform).z)
      cmds.setAttr("%s.rotateX" % o, m.rotation(asQuaternion=False).x * radToDeg)
      cmds.setAttr("%s.rotateY" % o, m.rotation(asQuaternion=False).y * radToDeg)
      cmds.setAttr("%s.rotateZ" % o, m.rotation(asQuaternion=False).z * radToDeg)
      cmds.setAttr("%s.scaleX" % o, m.scale(om.MSpace.kTransform)[0])
      cmds.setAttr("%s.scaleY" % o, m.scale(om.MSpace.kTransform)[1])
      cmds.setAttr("%s.scaleZ" % o, m.scale(om.MSpace.kTransform)[2])
