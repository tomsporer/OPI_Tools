# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class ImportColorCheckerCameraTool(Tool):

  ToolName = 'ImportColorCheckerCamera'
  ToolLabel = 'Color Checker (camera)'
  ToolCommand = 'importcolorcheckercamera'
  ToolDescription = 'Import Color Checker lookdev kit under current camera'
  ToolTooltip = 'Import Color Checker lookdev kit under current camera'

  def __init__(self, host):
    super (ImportColorCheckerCameraTool, self).__init__(host)
    self._noUI = True


  def executeMaya(self):

    maya = self.host.apis['maya']
    cmds = maya.cmds

    #Get Current Camera
    curPanel = cmds.getPanel(withFocus=True)
    panelType = cmds.getPanel(typeOf=curPanel)
    if panelType != "modelPanel":
      cmds.warning("No active Camera detected. Please click in the viewport once and try again.")
    else:
      curCam = cmds.modelPanel(curPanel, q=True, camera=True)
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

      #Parent under Camera
      cmds.setAttr(curCam + ".visibility", 1)
      ctrlBox = cmds.parent(ctrlBox, curCam)[0]
      cmds.xform(ctrlBox, t=[-0.6, -0.15, -2], ro=[0, 0, 0], s=[0.05, 0.05, 0.05])

      #Select CTRL
      cmds.select(ctrlBox)