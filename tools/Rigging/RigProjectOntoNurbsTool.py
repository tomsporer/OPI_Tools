# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import re
import sys

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class RigProjectOntoNurbsTool(Tool):

  ToolName = 'RigProjectOntoNurbs'
  ToolLabel = 'Project onto Nurbs'
  ToolCommand = 'rigprojectontonurbs'
  ToolDescription = 'Project onto Nurbs'
  ToolTooltip = 'Project onto Nurbs'

  def __init__(self, host):
    super (RigProjectOntoNurbsTool, self).__init__(host)

  def initialize(self, **args):
    self.args.add(name="geometries", type="str", value=args.get('geometries', None), hidden=True)
    self.args.add(name="nurbsSurface", type="str", value=args.get('nurbsSurface', None), hidden=True)
    self.args.add(name="uvMarginPercent", type="float", value=args.get('uvMargin', 10), range=[0, 100])
    self.results.add(name="deformer", type="str")

  def __getShapeDagNode(self, s):
    maya = self.host.apis['maya']
    om = maya.api.OpenMaya
    sel = om.MSelectionList()
    sel.add(s)
    dagPath = sel.getDagPath(0)
    shapeDagPath = om.MDagPath(dagPath).extendToShape()
    if not shapeDagPath.isValid():
      return None
    return om.MFnDagNode(shapeDagPath.node())

  def preexecute(self, **args):
    maya = self.host.apis['maya']
    cmds = maya.cmds
    om = maya.api.OpenMaya

    selection = cmds.ls(sl=True, l=True)

    geometries = args.get('geometries', None)
    if geometries is None:
      if len(selection) == 0:
        self.logError('Please select the target nurbs surface and the geometries to project.')
        return

      geometries = []
      hitNurbs = False
      for s in selection:
        shapeNode = self.__getShapeDagNode(s)
        if not shapeNode:
          continue

        # skip first nurbs object
        if not hitNurbs:
          if shapeNode.typeName == 'nurbsSurface':
            continue

        if not shapeNode.typeName in ['mesh', 'nurbsCurve', 'nurbsSurface']:
          self.log('Object %s not supported - ignoring.' % s)
          continue
        geometries += [s]

      if len(geometries) == 0:
        self.logError('Please select the target nurbs surface and the geometries to project.')
        return
      self.args.setValue('geometries', ','.join(geometries))

    nurbsSurface = args.get('nurbsSurface', None)
    if nurbsSurface is None:
      if len(selection) == 0:
        self.logError('Please select the target nurbs surface and the geometries to project.')
        return

      for s in selection:
        shapeNode = self.__getShapeDagNode(s)
        if not shapeNode:
          continue
        if shapeNode.typeName != 'nurbsSurface':
          continue
        nurbsSurface = s
        break

      if nurbsSurface is None:
        self.logError('Please select the target nurbs surface and the geometries to project.')
      self.args.setValue('nurbsSurface', nurbsSurface)

  def execute(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds
    om = maya.api.OpenMaya

    geometries = self.args.getValue('geometries')
    if not geometries:
      return
    geometries = geometries.split(',')
    nurbsSurface = self.args.getValue('nurbsSurface')
    if not nurbsSurface:
      return
    uvMarginPercent = self.args.getValue('uvMarginPercent')

    cmds.loadPlugin('HM_WrapDeformer')

    # boundingBox = cmds.exactWorldBoundingBox(geometries)
    # print boundingBox
    bboxMin = []
    bboxMax = []
    for g in geometries:
      shapeNode = self.__getShapeDagNode(g)
      box = cmds.getAttr("%s.boundingBoxMin" % shapeNode.fullPathName())
      box += cmds.getAttr("%s.boundingBoxMax" % shapeNode.fullPathName())
      for j in range(2):
        if len(bboxMin) == 0:
          bboxMin = [box[j][0], box[j][1], box[j][2]]
        else:
          for i in range(3):
            if bboxMin[i] > box[j][i]:
              bboxMin[i] = box[j][i]
        if len(bboxMax) == 0:
          bboxMax = [box[j][0], box[j][1], box[j][2]]
        else:
          for i in range(3):
            if bboxMax[i] < box[j][i]:
              bboxMax[i] = box[j][i]

    for i in range(3):
      c = float(bboxMin[i] + bboxMax[i]) * 0.5
      bboxMin[i] = c + (float(bboxMin[i]) - c) * (1 + uvMarginPercent / 100.0)
      bboxMax[i] = c + (float(bboxMax[i]) - c) * (1 + uvMarginPercent / 100.0)

    deformer = cmds.deformer(geometries, type='HM_WrapDeformer')[0]
    cmds.connectAttr(nurbsSurface+'.local', deformer+'.targetSurface')
    cmds.setAttr(deformer+'.uMin', bboxMin[0])
    cmds.setAttr(deformer+'.uMax', bboxMax[0])
    cmds.setAttr(deformer+'.vMin', bboxMin[1])
    cmds.setAttr(deformer+'.vMax', bboxMax[1])
    self.results.setValue('deformer', deformer)
