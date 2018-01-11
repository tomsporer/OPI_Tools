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
    projectPath = cmds.workspace( q=True, rootDirectory=True )

    if renderPrefix[1] != ":":
      renderFolder = os.path.join(projectPath, renderPrefix)
    else:
      renderFolder = renderPrefix

    if renderFolder[-1] != "\\":
      renderFolder = os.path.split(renderFolder)[0]

    openFolder = os.path.exists(renderFolder)

    if openFolder:
      subprocess.Popen('explorer /e,"' + str(renderFolder.replace("/", "\\")) + '"')
    else:
      print "# INFO: Render ouput folder doesn't exist."

