# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import sys
import getpass

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject

class SaverTool(DataBaseTool):

  ToolName = 'Saver'
  ToolLabel = 'Save as...'
  ToolCommand = 'saveas'
  ToolDescription = 'Save as'
  ToolTooltip = 'Save as'

  def __init__(self, host):
    super (SaverTool, self).__init__(host)

  def initialize(self, **args):

    self.__ProjectsRoot = "E:\\PROJECTS"
    self.args.add(name="project", label="Project", type="instance", template="project", comboSqlQuery="SELECT * FROM project WHERE project.name == 'Rotkaeppchen'", enabled=False)
    self.args.add(name="bottle", label="Bottle", type="instance", template="levelone", comboSqlQuery="SELECT * FROM levelone")
    self.args.add(name="product", label="Product", type="instance", template="leveltwo", comboSqlQuery="SELECT * FROM leveltwo WHERE levelone_id == ${bottle} ORDER BY name")
    self.args.add(name="latestVersion", label="Latest Version", type="str", enabled=False)
    self.args.beginRow("New Version")
    self.args.add(name="newVersion", label="", type="str", value="001", padding=3)
    self.args.addButton("plusOne", "+1")
    self.args.endRow()
    self.args.add(name="fileToSave", label="Filename", type="str", private=True, enabled=False)
    self.args.add(name="comment", label="Comment (optional)", type="comment", value="")


  def preexecute(self):

    db = self.host.apis['db']

    # ----
    # Get current scene instance and set default values for saving location
    # ----
    if self.host.apis.has_key('maya'):
      maya = self.host.apis['maya']
      cmds = maya.cmds
      currentSceneFile = cmds.file(q=True, sn=True)
      currentScenelocation = currentSceneFile.split("PROJECTS/")[-1]
      queryScene = db.queryFromLocation("leveltwo_file", location=currentScenelocation)

      if queryScene != None:
        currentLevelone = queryScene.levelone.name
        currentLeveltwo = queryScene.leveltwo.name
        self.args.get("bottle").value = currentLevelone
        self.args.get("product").value = currentLeveltwo
    # ----

    self.getLatestVersion()
    self.updateFilename()

  def execute(self):

    db = self.host.apis['db']

    product = self.args.getValue("product")
    newVersion = self.args.getValue("newVersion")
    fileToSave = self.args.getValue("fileToSave")
    savePath = os.path.join(self.__ProjectsRoot, product.location, fileToSave)

    print "Saving as " + str(savePath)

  def executeMaya(self):

    db = self.host.apis['db']
    maya = self.host.apis['maya'] 
    cmds = maya.cmds

    product = self.args.getValue("product")
    newVersion = self.args.getValue("newVersion")
    fileToSave = self.args.getValue("fileToSave")
    savePath = os.path.join(self.__ProjectsRoot, product.location, fileToSave)

    if os.path.isfile(savePath):
      confirmDialog = cmds.confirmDialog( title='Save As', message=fileToSave + " already exists.\nDo you want to replace it?", button=['Yes', "No"], defaultButton='No', cancelButton='No', dismissString='No' )
      if confirmDialog != 'Yes':
        self.invokeWithUI()

    maya.cmds.file(rename = savePath)
    maya.cmds.file(save = True)
    db.getOrCreateNew("Leveltwo_File", leveltwo=product, version=newVersion, fileext="ma", createEmptyFile=False)
    self.saveJson(savePath)

  def onValueChanged(self, arg):

    if type(arg) != type("str"):
      if arg.name == "project" or arg.name == "bottle" or arg.name == "product":
        self.getLatestVersion()
        self.updateFilename()
      elif arg.name == "newVersion":
        self.updateFilename()
    else:
      if arg == "buttonPressedPlusone":
        self.updateFilename()

  def onButtonPressed(self, button):

    newVersion = self.args.getValue("newVersion")
    if button == "plusOne":
      versionPlus = str(int(newVersion) + 1).rjust(3,"0")
      self.args.get("newVersion").value = versionPlus
      self.onValueChanged(arg="buttonPressedPlusone")

  def getLatestVersion(self):

    db = self.host.apis['db']
    product = self.args.getValue("product")
    latestVersionQuery = db.query("leveltwo_file", sql="SELECT * FROM leveltwo_file WHERE leveltwo_id == %d ORDER BY version DESC" % (product.id, ))
    if len(latestVersionQuery) == 0:
      latestVersion = "000"
    else:
      latestVersion = latestVersionQuery[0].version
    self.args.get("latestVersion").value = str(latestVersion)
    self.args.get("newVersion").value = str(int(latestVersion) + 1).rjust(3, "0")

  def updateFilename(self):

    bottle = self.args.getValue("bottle")
    product = self.args.getValue("product")
    newVersion = self.args.getValue("newVersion")
    self.args.get("fileToSave").value = str(bottle.name) + "_" + str(product.name) + "_v" + str(newVersion) + ".ma"

  def saveJson(self, savePath):

    comment = self.args.getValue("comment")
    jsonSavePath = savePath + ".json"
    jsonobj = JsonObject(jsonSavePath)
    jsonobj.comment = comment
    jsonobj.write()





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

  tool = workshop.instantiate(cmd='saveas')
  tool.invokeWithUI()






