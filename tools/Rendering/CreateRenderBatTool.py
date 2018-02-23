# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import sys
import json
import subprocess
from collections import OrderedDict

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException



class CreateRenderBatTool(DataBaseTool):

  ToolName = 'CreateRenderBat'
  ToolLabel = 'Create Render Bat File...'
  ToolCommand = 'createrenderbat'
  ToolDescription = 'creates a bat file to render multiple scenes'
  ToolTooltip = 'Create Render Bat'

  def __init__(self, host):
    super (CreateRenderBatTool, self).__init__(host)

  def initialize(self, **args):

    self.args.add(name='scenefile', label='Add Scene File', type='file', mustexist=True)
    self.args.add(name="sceneListDisplay", label="Scenes", type="str", combo=[], enabled=True)
    self.args.addButton("removeSelected", "Remove Selected")
    self.args.addButton("clearList", "Clear List")
    self.args.add(name="output", label="Output Path", type="file", mustexist=False, filefilter="*.bat")
    self.args.add(name="openFolder", label="Open Folder", type="bool", value=True)


  def writeBatFile(self, path):

    sceneList = self.args.get("sceneListDisplay").combo
    numScenes = len(sceneList)

    batHead = "\
@echo off\n\
@echo.\n\
@echo starting render for " + str(numScenes) + " scenes\n\
@echo.\n\
\n\
SET MAYA_VERSION=" + os.environ.get("MAYA_VERSION") + "\n\
SET OPI_LAUNCHER_DIR=\\\\domain\\tomsporer\\PIPELINE\\OPI_Tools\\launchers\n\
SET MAYA_LOCATION=" + os.environ.get("MAYA_LOCATION") + "\n\
\n\
"

    # Get environment variables from OPI cfg file
    cfgFile = os.path.join(os.environ.get("OPI_LAUNCHER_DIR"), "configs", "maya.cfg")
    with open(cfgFile, "r") as f:
      j = json.load(f, object_pairs_hook=OrderedDict)
      jEnv = j["environment"]
      # cfgEnvList = ["MAYA_MODULE_PATH", "MAYA_PLUG_IN_PATH", "MAYA_SCRIPT_PATH", "PYTHONPATH", "FABRIC_EXTS_PATH", "FABRIC_DFG_PATH"]
      # cfgEnvDict = {}
      # for env in cfgEnvList:
      #   cfgEnvDict[env] = ";".join(jEnv[env]).replace("${", "%").replace("}", "%").replace("/", "\\")

    # copy all environment variables from the cfg file to the bat file
    batEnvVariables = ""
    for env in jEnv.keys():
      value = ";".join(jEnv[env]).replace("${", "%").replace("}", "%").replace("/", "\\")
      batEnvVariables += "SET %s=%s\n" %(env, value)
    batEnvVariables += "\n"


#     batEnvVariables = "\
# SET ADSKFLEX_LICENSE_FILE=@192.168.1.14;@192.168.1.21;@192.168.1.22\n\
# SET peregrinel_LICENSE=39554@192.168.1.16\n\
# SET REDSHIFT_VERSION=" + os.environ.get("RS_VERSION") + "\n\
# SET REDSHIFT_INSTALLATION_ROOT=" + os.environ.get("REDSHIFT_INSTALLATION_ROOT") + "\n\
# SET REDSHIFT_ROOT=%REDSHIFT_INSTALLATION_ROOT%\\RedShift\n\
# SET REDSHIFT_CORE_PATH=%REDSHIFT_ROOT%\\%REDSHIFT_VERSION%\\Redshift\n\
# SET REDSHIFT_COREDATAPATH=%REDSHIFT_CORE_PATH%\n\
# SET REDSHIFT_COMMON_ROOT=%REDSHIFT_CORE_PATH%\\Plugins\\Maya\\Common\n\
# SET REDSHIFT_PLUG_IN_PATH=%REDSHIFT_CORE_PATH%\\Plugins\\Maya\\%MAYA_VERSION%\\nt-x86-64\n\
# SET REDSHIFT_SCRIPT_PATH=%REDSHIFT_COMMON_ROOT%\\scripts\n\
# SET REDSHIFT_XBMLANGPATH=%REDSHIFT_COMMON_ROOT%\\icons\n\
# SET REDSHIFT_RENDER_DESC_PATH=%REDSHIFT_COMMON_ROOT%\\rendererDesc\n\
# \n\
# \n\
# SET MAYA_PLUG_IN_PATH=" + cfgEnvDict["MAYA_PLUG_IN_PATH"] + "\n\
# SET MAYA_SCRIPT_PATH=" + cfgEnvDict["MAYA_SCRIPT_PATH"] + "\n\
# SET MAYA_MODULE_PATH=" + cfgEnvDict["MAYA_MODULE_PATH"] + "\n\
# SET XBMLANGPATH=%REDSHIFT_XBMLANGPATH%\n\
# SET MAYA_RENDER_DESC_PATH=%REDSHIFT_RENDER_DESC_PATH%\n\
# \n\
# SET PATH=%REDSHIFT_PLUG_IN_PATH%;%REDSHIFT_CORE_PATH%\\bin\n\
# SET PYTHONPATH=" + cfgEnvDict["PYTHONPATH"] + "\n\
# SET FABRIC_EXTS_PATH=" + cfgEnvDict["FABRIC_EXTS_PATH"] + "\n\
# SET FABRIC_DFG_PATH=" + cfgEnvDict["FABRIC_DFG_PATH"] + "\n\
# \n\
# "

    batBody = ""

    for scene in sceneList:
      batBody += "\
title Rendering \"" + scene + "\"\n\
\"C:\\Program Files\\Autodesk\\Maya%MAYA_VERSION%\\bin\\Render.exe\" -r file \"" + scene + "\"\n\
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

    batFile = open(path, "w")
    batFile.write(batHead + batEnvVariables + batBody + batFoot)
    batFile.close


  def execute(self):

    QtWidgets = self.host.apis["QtWidgets"]
    msgBox = QtWidgets.QMessageBox
    sceneList = self.args.get("sceneListDisplay").combo
    outputPath = self.args.getValue("output")
    if len(sceneList) == 0:
      dialog = msgBox.information(None, "No Scenes Selected", "No Scenes were selected.\nNo bat file was created", msgBox.StandardButton.Retry | msgBox.StandardButton.Abort)
      if dialog == msgBox.Retry:
        self.invokeWithUI(output=outputPath)
    elif outputPath == None:
      dialog = msgBox.information(None, "No Output Defined", "There was no output path specified!", msgBox.StandardButton.Retry | msgBox.StandardButton.Abort)
      if dialog == msgBox.Retry:
        self.invokeWithUI(sceneListDisplay=sceneList)
    else:
      print "This is where we would normally create the bat file. Unfortunately, this script only works when started out of Maya. Sorry."
      # self.writeBatFile(outputPath)


  def executeMaya(self):

    sceneList = self.args.get("sceneListDisplay").combo
    outputPath = self.args.getValue("output")
    if len(sceneList) == 0:
      dialog = cmds.confirmDialog(title="No Scenes Selected", message="No Scenes were selected.\nNo bat file was created", button=["Retry", "Abort"], defaultButton="Retry", cancelButton="Abort", dismissString="Abort")
      if dialog == "Retry":
        self.invokeWithUI(output=outputPath)
    elif outputPath == None:
      dialog = cmds.confirmDialog(title="No Output Defined", message="There was no output path specified!", button=["Retry", "Abort"], defaultButton="Retry", cancelButton="Abort", dismissString="Abort")
      if dialog == "Retry":
        self.invokeWithUI(sceneListDisplay=sceneList)
    else:
      self.writeBatFile(outputPath)
      if self.args.getValue("openFolder"):
        subprocess.Popen('explorer /select,"' + str(outputPath.replace("/", "\\")) + '"')


  def onValueChanged(self,arg):

    if arg.name == "scenefile":
      selScene = self.args.getValue("scenefile")
      combo = self.args.get("sceneListDisplay").combo
      if selScene not in combo:
        combo.append(selScene)
      self.args.get("sceneListDisplay")._setCombo(combo, combo[-1])

  def onButtonPressed(self, button):

    if button == "clearList":
      self.args.get("sceneListDisplay")._setCombo([], "")
    elif button == "removeSelected":
      sceneList = self.args.get("sceneListDisplay")
      sceneList.combo.remove(sceneList.value)
      if len(sceneList.combo) != 0:
        self.args.get("sceneListDisplay")._setCombo(sceneList.combo, sceneList.combo[-1])
      else:
        self.args.get("sceneListDisplay")._setCombo([], "")



# Todo

# UI:
# select scene file
# button "add"
# override framerange (mit checkbox)
# comment box mit allen selktierten scene files
# button "clear" um die box zu leeren
# bat file save as location/name


if __name__ == '__main__':

  import os
  import opi
  from opi.client.database import DataBase as OpiDB
  from opi.tools.host import Host as OPIHost
  from opi.tools.workshop import WorkShop as OPIWorkShop
  from opi.ui.Qt import QtWidgets, QtCore

  path = os.path.split(os.path.abspath(__file__))[0]
  path = os.path.split(path)[0]
  path = os.path.split(path)[0]
  path = os.path.split(path)[0]

  dbRoot = "e:\\projects"
  
  templateRoot =  os.path.join(path, 'OPI_Tools', 'templates')
  toolRoot =  os.path.join(path, 'OPI_Tools', 'tools')

  db = OpiDB(dbRoot, templateRoot=templateRoot, rootSubFolders=[''])

  host = OPIHost('python', {'db': db, 'QtWidgets': QtWidgets, 'QtCore': QtCore})
  workshop = OPIWorkShop(host, toolRoot)

  tool = workshop.instantiate(cmd='createrenderbat')
  tool.invokeWithUI()

