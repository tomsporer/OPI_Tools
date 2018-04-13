# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import sys

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject


class OpenerTool(DataBaseTool):

  ToolName = 'Opener'
  ToolLabel = 'Open Scene...'
  ToolCommand = 'openscene'
  ToolDescription = 'Open Scene'
  ToolTooltip = 'Open Scene'

  def __init__(self, host):
    super (OpenerTool, self).__init__(host)

  def initialize(self, **args):

    db = self.host.apis['db']
    # self.__ProjectsRoot = "E:\\PROJECTS"
    self.__ProjectsRoot = db.root
    self.args.addStaticText("\tOpen Rotkaeppchen Scene \t \t \t")
    self.args.addSpacer(13)
    self.args.add(name="project", label="Project", type="instance", template="project", comboSqlQuery="SELECT * FROM project WHERE name LIKE 'Rotkaeppchen%' ORDER BY name DESC", enabled=True)
    self.args.add(name="bottle", label="Bottle", type="instance", template="levelone", comboSqlQuery="SELECT * FROM levelone WHERE project_id == ${project} ORDER BY name")
    self.args.add(name="product", label="Product", type="instance", template="leveltwo", comboSqlQuery="SELECT * FROM leveltwo WHERE levelone_id == ${bottle} ORDER BY name")
    self.args.add(name="versionlist", label="version", type="str", combo=[])
    self.args.add(name="filedate", label="Date", type="str", value="", enabled=False)


  def preexecute(self):

    db = self.host.apis['db']

    # ----
    # Get current scene instance and set default values for opening location
    # ----
    if self.host.apis.has_key('maya'):
      maya = self.host.apis['maya']
      cmds = maya.cmds
      currentSceneFile = cmds.file(q=True, sn=True)
      currentScenelocation = currentSceneFile.split("PROJECTS/")[-1]
      queryScene = db.queryFromLocation("leveltwo_file", location=currentScenelocation)

      if queryScene != None:
        currentProject = queryScene.project.name
        currentLevelone = queryScene.levelone.name
        currentLeveltwo = queryScene.leveltwo.name
        self.args.get("project").value = currentProject
        self.args.get("bottle").value = currentLevelone
        self.args.get("product").value = currentLeveltwo
    # ----

    self.fillVersionList()


  def execute(self):

    version = self.args.getValue("versionlist")
    pathToOpen = self.__versionlistCombo[str(version)][0]

    print "Opening " + str(pathToOpen)


  def executeMaya(self):

    maya = self.host.apis['maya']
    cmds = maya.cmds

    # ----
    # Check if current scene has been modified 
    # ----
    currentSceneFile = cmds.file(q=True, sn=True)
    fileModified = cmds.file(q=True, modified=True)

    if fileModified:
      confirmDialog = cmds.confirmDialog( title='Save Changes', message='Save Changes to\n' + currentSceneFile, button=['Save', "Don't Save", 'Cancel'], defaultButton='Save', cancelButton='Cancel', dismissString='Cancel' )
      if confirmDialog == 'Save':
        cmds.SaveScene()
      elif confirmDialog == "Don't Save":
        cmds.file(modified=False)
      else:
        raise OPIException( 'Canceled. Scene was not loaded.' )
    # ----

    version = self.args.getValue("versionlist")
    pathToOpen = self.__versionlistCombo[str(version)][0]
    cmds.file(pathToOpen, open=True)


  def onValueChanged(self, arg):
    if arg.name == "project" or arg.name == "bottle" or arg.name == "product":
      self.fillVersionList()
    elif arg.name == "versionlist":
      fileVersion = self.args.getValue("versionlist")
      cTime = self.__versionlistCombo[fileVersion][1]
      self.args.setValue("filedate", cTime)


  def fillVersionList(self):

    fileextMaya = ["ma", "mb"]
    db = self.host.apis['db']
    project = self.args.getValue("project")
    bottle = self.args.getValue("bottle")
    product = self.args.getValue("product")
    fileslist = db.query("leveltwo_file", sql="SELECT * FROM leveltwo_file")

    # ----
    # Creating a dictionary with key=str(version + comment + user) and value=filepath
    # ----
    self.__versionlistCombo = {}
    vlc = self.__versionlistCombo
    for k in fileslist:
      if k.levelone.name == bottle.name and k.leveltwo.name == product.name and k.fileext in fileextMaya:
        if k.name != k.levelone.name + "_" + k.leveltwo.name:
          fileName = k.name + "  -  "
        else:
          fileName = ""
        opiLocation = k.location
        pathToOpen = os.path.join(self.__ProjectsRoot, opiLocation)
        jsonPath = pathToOpen + ".json"
        if os.path.isfile(jsonPath):
          readJson = JsonObject(jsonPath)
          try:
            cText = readJson.comment.text
            if cText:
              cText = "  -  " + cText
          except:
            cText = ""
          try:
            cUser = readJson.comment.user
            if cUser:
              cUser = "  -  " + cUser
          except:
            cUser = ""
          try:
            cTime = readJson.comment.time
          except:
            cTime = ""
          if cText or cUser or cTime:
            fileComment = cUser + cText
          else:
            fileComment = ""
        #     if readJson.comment.text == "":
        #       fileComment = "  -  " + readJson.comment.user
        #     else:
        #       fileComment = "  -  " + readJson.comment.user + " - " + readJson.comment.text
        #   except:
        #     fileComment = ""
        # else:
        #   fileComment = ""
        vlc[fileName + "v" + str(k.version) + fileComment] = [pathToOpen, cTime]
    # ----

    if len(vlc.keys()) > 0:
      sortedVlcKeys = sorted(vlc.keys(), reverse=True)
      self.args.get("versionlist")._setCombo(sortedVlcKeys, sortedVlcKeys[0])
      self.args.get("filedate").value = vlc[sortedVlcKeys[0]][1]
    else:
      self.args.get("versionlist")._setCombo([], None)




# ------------------------------------------
##### Launch Tool directly in python 
# ------------------------------------------


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

  dbRoot = "e:\\PROJECTS"
  
  templateRoot =  os.path.join(path, 'OPI_Tools', 'templates')
  toolRoot =  os.path.join(path, 'OPI_Tools', 'tools')

  db = OpiDB(dbRoot, templateRoot=templateRoot, rootSubFolders=['ROT_Rotkaeppchen'])

  host = OPIHost('python', {'db': db, 'QtWidgets': QtWidgets, 'QtCore': QtCore})
  workshop = OPIWorkShop(host, toolRoot)

  tool = workshop.instantiate(cmd='openscene')
  tool.invokeWithUI()






