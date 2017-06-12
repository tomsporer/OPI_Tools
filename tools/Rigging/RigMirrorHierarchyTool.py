# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import re
import sys

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class RigMirrorHierarchyTool(Tool):

  ToolName = 'RigMirrorHierarchy'
  ToolLabel = 'Mirror Hierarchy'
  ToolCommand = 'rigmirrorhierarchy'
  ToolDescription = 'Mirror Hierarchy'
  ToolTooltip = 'Mirror Hierarchy'

  def __init__(self, host):
    super (RigMirrorHierarchyTool, self).__init__(host)

  def initialize(self, **args):
    self.args.add(name="objects", type="str", value=args.get('objects', None), hidden=True)
    self.args.add(name="roles", type="str", value=args.get('roles', 'CNS,PAR,SPACE'))
    self.args.add(name="rotation", type="bool", value=args.get('rotation', True))

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
    om = maya.api.OpenMaya

    radToDeg = 57.29577951308232

    expr = re.compile('^([a-zA-Z0-9]+)_([a-zA-Z0-9_]+)_([a-zA-Z0-9]+)$')

    objects = self.args.getValue('objects')
    if not objects:
      return
    objects = objects.split(',')
    objects = sorted(objects)

    roles = self.args.getValue('roles').split(',')
    rotation = self.args.getValue('rotation')

    matrices = {}
    for o in objects:
      sel = om.MSelectionList()
      sel.add(o)

      dagPath = sel.getDagPath(0)
      parentDagPath = om.MDagPath(dagPath)
      parentDagPath = parentDagPath.pop()

      transformObj = dagPath.transform()
      transform = om.MFnTransform(transformObj)

      m = om.MTransformationMatrix(dagPath.inclusiveMatrix())
      matrices[o] = m

    for o in objects:
      sel = om.MSelectionList()
      sel.add(o)

      dagPath = sel.getDagPath(0)
      parentDagPath = om.MDagPath(dagPath)
      parentDagPath = parentDagPath.pop()

      transformObj = dagPath.transform()
      transform = om.MFnTransform(transformObj)

      m = expr.search(transform.name())
      if not m:
        print 'Warning: Object %s does not follow the naming convention - skipping.' % o
        continue

      side = m.group(1)
      role = m.group(3)

      if not role in roles:
        continue

      print 'Mirroring %s' % o

      m = om.MTransformationMatrix(matrices[o])
      tr = m.translation(om.MSpace.kTransform)
      sc = m.scale(om.MSpace.kTransform)

      ori = m.rotation(asQuaternion=True)
      oriX = om.MVector(1, 0, 0).rotateBy(ori)
      oriY = om.MVector(0, 1, 0).rotateBy(ori)
      oriZ = om.MVector(0, 0, 1).rotateBy(ori)

      tr.x = -tr.x
      oriX.x = -oriX.x
      oriY.x = -oriY.x
      oriZ = oriX ^ oriY # cross product

      oriM = om.MMatrix().setToIdentity()
      oriM.setElement(0, 0, oriX.x)
      oriM.setElement(0, 1, oriX.y)
      oriM.setElement(0, 2, oriX.z)
      oriM.setElement(1, 0, oriY.x)
      oriM.setElement(1, 1, oriY.y)
      oriM.setElement(1, 2, oriY.z)
      oriM.setElement(2, 0, oriZ.x)
      oriM.setElement(2, 1, oriZ.y)
      oriM.setElement(2, 2, oriZ.z)

      if rotation:
        m = om.MTransformationMatrix(oriM)
      else:
        m = om.MTransformationMatrix(m)
        
      m.setTranslation(tr, om.MSpace.kTransform)
      m.setScale(sc, om.MSpace.kTransform)

      matrices[o] = om.MTransformationMatrix(m)

      if parentDagPath.isValid():
        parentM = parentDagPath.inclusiveMatrix().inverse()
        m = om.MTransformationMatrix(m.asMatrix() * parentM)

      # transform.setTransformation(m)
      try:
        cmds.setAttr("%s.translateX" % o, m.translation(om.MSpace.kTransform).x)
        cmds.setAttr("%s.translateY" % o, m.translation(om.MSpace.kTransform).y)
        cmds.setAttr("%s.translateZ" % o, m.translation(om.MSpace.kTransform).z)
        cmds.setAttr("%s.rotateX" % o, m.rotation(asQuaternion=False).x * radToDeg)
        cmds.setAttr("%s.rotateY" % o, m.rotation(asQuaternion=False).y * radToDeg)
        cmds.setAttr("%s.rotateZ" % o, m.rotation(asQuaternion=False).z * radToDeg)
        cmds.setAttr("%s.scaleX" % o, m.scale(om.MSpace.kTransform)[0])
        cmds.setAttr("%s.scaleY" % o, m.scale(om.MSpace.kTransform)[1])
        cmds.setAttr("%s.scaleZ" % o, m.scale(om.MSpace.kTransform)[2])
      except:
        pass
