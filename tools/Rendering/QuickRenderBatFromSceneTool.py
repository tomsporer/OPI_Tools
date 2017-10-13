# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import sys
import json
import subprocess

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException



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

    # Get environment variables from OPI cfg file
    cfgFile = os.path.join(os.environ.get("OPI_LAUNCHER_DIR"), "configs", "maya.cfg")
    with open(cfgFile, "r") as f:
      j = json.load(f)
      jEnv = j["environment"]
      cfgEnvList = ["MAYA_MODULE_PATH", "MAYA_PLUG_IN_PATH", "MAYA_SCRIPT_PATH", "PYTHONPATH", "FABRIC_EXTS_PATH", "FABRIC_DFG_PATH"]
      cfgEnvDict = {}
      for env in cfgEnvList:
        cfgEnvDict[env] = ";".join(jEnv[env]).replace("${", "%").replace("}", "%").replace("/", "\\")


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
SET OPI_LAUNCHER_DIR=\\\\domain\\tomsporer\\PIPELINE\\OPI_Tools\\launchers\n\
\n\
SET MAYA_PLUG_IN_PATH=" + cfgEnvDict["MAYA_PLUG_IN_PATH"] + "\n\
SET MAYA_SCRIPT_PATH=" + cfgEnvDict["MAYA_SCRIPT_PATH"] + "\n\
SET MAYA_MODULE_PATH=" + cfgEnvDict["MAYA_MODULE_PATH"] + "\n\
SET XBMLANGPATH=%REDSHIFT_XBMLANGPATH%\n\
SET MAYA_RENDER_DESC_PATH=%REDSHIFT_RENDER_DESC_PATH%\n\
\n\
SET PATH=%REDSHIFT_PLUG_IN_PATH%;%REDSHIFT_CORE_PATH%\\bin\n\
SET PYTHONPATH=" + cfgEnvDict["PYTHONPATH"] + "\n\
SET FABRIC_EXTS_PATH=" + cfgEnvDict["FABRIC_EXTS_PATH"] + "\n\
SET FABRIC_DFG_PATH=" + cfgEnvDict["FABRIC_DFG_PATH"] + "\n\
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


