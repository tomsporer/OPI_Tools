# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class ImportColorCheckerWorldTool(Tool):

  ToolName = 'ImportColorCheckerWorld'
  ToolLabel = 'Color Checker (world)'
  ToolCommand = 'importcolorcheckerworld'
  ToolDescription = 'Import Color Checker lookdev kit into current scene'
  ToolTooltip = 'Import Color Checker lookdev kit into current scene'

  def __init__(self, host):
    super (ImportColorCheckerWorldTool, self).__init__(host)
    self._noUI = True


  def executeMaya(self):

    maya = self.host.apis['maya']
    cmds = maya.cmds

    #Get Colorchecker Images
    opiLauncherDir = os.environ.get("OPI_LAUNCHER_DIR", None)

    #----only for local copy
    opiLauncherDir = "E:\\PIPELINE\\OPI_Tools\\launchers"
    #----
    
    colorCheckerDir = os.path.join(os.path.split(opiLauncherDir)[0], "util", "ColorChecker")
    colorCheckerMA = os.path.join(colorCheckerDir, "colorChecker.ma")
    colorCheckerTex = os.path.join(colorCheckerDir, "sRGB_ColorChecker2014.exr")
    colorCheckerLabelsTex = os.path.join(colorCheckerDir, "sRGB_Labels_ColorChecker2014.exr")

    #Reference Color Checker Scene
    ref = cmds.file(colorCheckerMA, r=True, type="mayaAscii", namespace="colorChecker", returnNewNodes=True)

    #Set File Texture Paths
    for refNode in ref:
      if "colorCheckerFile" in refNode:
        cmds.setAttr(refNode + ".fileTextureName", colorCheckerTex, type="string")
      if "colorCheckerLabelsFile" in refNode:
        cmds.setAttr(refNode + ".fileTextureName", colorCheckerLabelsTex, type="string")
      if refNode.endswith("CTRL"):
        ctrlBox = refNode

    #Select CTRL
    cmds.select(ctrlBox)