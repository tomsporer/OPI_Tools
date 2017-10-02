# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import sys
import subprocess

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject



class QuickRenderBatFromSceneTool(DataBaseTool):

  ToolName = 'QuickRenderBatFromScene'
  ToolLabel = 'Quick Render Bat File From Scene'
  ToolCommand = 'quickrenderbatfromscene'
  ToolDescription = 'Creates a bat file to render the currently open scene'
  ToolTooltip = 'Quick Render Bat From Scene'

  def __init__(self, host):
    super (QuickRenderBatFromSceneTool, self).__init__(host)
    self._noUI = True


  def writeBatFile(self, output, sceneName, scenePath):


    batHead = "\
@echo off\n\
@echo.\n\
@echo starting render for " + sceneName + "\n\
@echo.\n\
\n\
"

    batEnvVariables = "\
SET ADSKFLEX_LICENSE_FILE=@192.168.1.14;@192.168.1.21;@192.168.1.22\n\
SET MAYA_VERSION=" + os.environ.get("MAYA_VERSION") + "\n\
SET REDSHIFT_VERSION=" + os.environ.get("REDSHIFT_VERSION") + "\n\
SET REDSHIFT_INSTALLATION_ROOT=" + os.environ.get("REDSHIFT_INSTALLATION_ROOT") + "\n\
SET REDSHIFT_ROOT=%REDSHIFT_INSTALLATION_ROOT%\\RedShift\n\
SET REDSHIFT_CORE_PATH=%REDSHIFT_ROOT%\\%REDSHIFT_VERSION%\\Redshift\n\
SET REDSHIFT_COREDATAPATH=%REDSHIFT_CORE_PATH%\n\
SET REDSHIFT_COMMON_ROOT=%REDSHIFT_CORE_PATH%\\Plugins\\Maya\\Common\n\
SET REDSHIFT_PLUG_IN_PATH=%REDSHIFT_CORE_PATH%\\Plugins\\Maya\\%MAYA_VERSION%\\nt-x86-64\n\
SET REDSHIFT_SCRIPT_PATH=%REDSHIFT_COMMON_ROOT%\\scripts\n\
SET REDSHIFT_XBMLANGPATH=%REDSHIFT_COMMON_ROOT%\\icons\n\
SET REDSHIFT_RENDER_DESC_PATH=%REDSHIFT_COMMON_ROOT%\\rendererDesc\n\
\n\
SET OPI_PIPELINE_DIR=\\\\domain\\tomsporer\\PIPELINE\n\
\n\
SET MAYA_PLUG_IN_PATH=%REDSHIFT_PLUG_IN_PATH%\n\
SET MAYA_SCRIPT_PATH=%REDSHIFT_SCRIPT_PATH%\n\
SET MAYA_MODULE_PATH=%OPI_PIPELINE_DIR%\\FabricEngine-2.5.0-Windows-x86_64\\DCCIntegrations\\FabricMaya2017;%OPI_PIPELINE_DIR%\\OPI_Tools\\maya;%OPI_PIPELINE_DIR%\\opi\\dccs\\maya\n\
SET XBMLANGPATH=%REDSHIFT_XBMLANGPATH%\n\
SET MAYA_RENDER_DESC_PATH=%REDSHIFT_RENDER_DESC_PATH%\n\
\n\
SET PATH=%REDSHIFT_PLUG_IN_PATH%;%REDSHIFT_CORE_PATH%\\bin\n\
SET PYTHONPATH=%REDSHIFT_SCRIPT_PATH%\n\
\n\
"

    batBody = "\
title Rendering \"" + sceneName + "\"\n\
\"C:\\Program Files\\Autodesk\\Maya%MAYA_VERSION%\\bin\\Render.exe\" -r file \"" + scenePath + "\"\n\
\n\
"

    batFoot = "\
title Rendering completed\n\
\n\
@echo.\n\
@echo Rendering completed\n\
@pause\n\
\n\
"

    batFile = open(output, "w")
    batFile.write(batHead + batEnvVariables + batBody + batFoot)
    batFile.close


  def executeMaya(self):

    maya = self.host.apis['maya']
    cmds = maya.cmds

    openFolder = True

    scenePath = cmds.file(q = True, sceneName = True)
    sceneName = cmds.file(q=True, sceneName=True, shortName=True).rsplit(".")[0]
    projectDir = cmds.workspace(q=True, rootDirectory=True)
    outputPath = os.path.join(projectDir, "Render", "bats")

    if not os.path.exists(outputPath):
      os.makedirs(outputPath)

    outputFile = os.path.join(outputPath, sceneName + ".bat")

    self.writeBatFile(outputFile, sceneName, scenePath)
    if openFolder:
      subprocess.Popen('explorer /select,"' + str(outputFile.replace("/", "\\")) + '"')


