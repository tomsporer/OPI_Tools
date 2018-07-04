# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#


from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class ExtractPolygonsKeepTool(Tool):

  ToolName = 'ExtractPolygonsKeepTool'
  ToolLabel = 'Extract Polygons (keep)'
  ToolCommand = 'extractpolygonskeeptool'
  ToolDescription = 'Extracts selected Polygons and does not modify the source Mesh'
  ToolTooltip = 'Extracts selected Polygons and does not modify the source Mesh'

  def __init__(self, host):
    super (ExtractPolygonsKeepTool, self).__init__(host)
    self._noUI = True


  def executeMaya(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    sel = cmds.ls(selection=True)
    sourceObj = sel[0].split(".")[0]
    polysToExtract = list(sel)
    for s in sel:
      if not sourceObj + "." in s or not ".f" in s:
        polysToExtract.remove(s)

    if polysToExtract:
      extractedObj = cmds.duplicate(sourceObj, name="extracted_Mesh")[0]
      # cmds.delete(polysToExtract)
      extractedSel = []
      for polys in polysToExtract:
        extractedSel += [str(polys).replace(sourceObj, extractedObj)]
      cmds.select(extractedSel)
      # cmds.InvertSelection()
      cmds.select(extractedObj + ".f[*]", toggle=True) # invert selection
      cmds.delete()
      cmds.select(extractedObj)
      exShape = cmds.listRelatives(extractedObj, children=True, shapes=True, path=True)[0]
      exChildren = cmds.listRelatives(extractedObj, children=True, path=True)
      exChildren.remove(exShape)
      if exChildren:
        cmds.delete(exChildren)
      cmds.select(extractedObj)