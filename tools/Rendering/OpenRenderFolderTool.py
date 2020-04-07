# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import subprocess

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException



class OpenRenderFolderTool(Tool):

  ToolName = 'OpenRenderFolder'
  ToolLabel = 'Open Render Folder'
  ToolCommand = 'openrenderfolder'
  ToolDescription = 'Open an explorer window with the render output folder of the current scene'
  ToolTooltip = 'Open an explorer window with the render output folder of the current scene'

  def __init__(self, host):
    super (OpenRenderFolderTool, self).__init__(host)
    self._noUI = True


  def executeMaya(self):

    maya = self.host.apis['maya']
    cmds = maya.cmds

    renderPrefix = str(cmds.getAttr("defaultRenderGlobals.imageFilePrefix"))
    renderPrefix = renderPrefix.replace("/", "\\")
    if "<RenderLayer>" in renderPrefix:
      curRenderLayer = cmds.editRenderLayerGlobals( query=True, currentRenderLayer=True )
      if curRenderLayer.startswith("rs_"):
        curRenderLayer = curRenderLayer[3:]
      elif curRenderLayer == "defaultRenderLayer":
        renderPrefix = renderPrefix.replace("\\<RenderLayer>\\", "\\")
      renderPrefix = renderPrefix.replace("<RenderLayer>", curRenderLayer)
    if "<Scene>" in renderPrefix:
      sceneFile = cmds.file(q=True, sceneName=True, shn=True)
      sceneName = os.path.splitext(sceneFile)[0]
      renderPrefix = renderPrefix.replace("<Scene>", sceneName)
    projectPath = cmds.workspace( q=True, rootDirectory=True )

    if renderPrefix == "":
      renderFolder = os.path.join(projectPath, "Render", "")
    elif renderPrefix[1] != ":":
      renderFolder = os.path.join(projectPath, renderPrefix)
    else:
      renderFolder = renderPrefix

    if renderFolder[-1] != "\\":
      renderFolder = os.path.split(renderFolder)[0]

    openFolder = os.path.exists(renderFolder)

    if openFolder:
      subprocess.Popen('explorer /e,"' + str(renderFolder.replace("/", "\\")) + '"')
    else:
      print "# INFO: The Render ouput folder \"%s\" does not exist." %(renderFolder)

