# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import sys

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException

class NewBottleOrProductTool(DataBaseTool):

  ToolName = 'NewBottleOrProduct'
  ToolLabel = 'New Bottle or Product...'
  ToolCommand = 'newbottleorproduct'
  ToolDescription = 'New Bottle or Product'
  ToolTooltip = 'New Bottle or Product'

  def __init__(self, host):
    super (NewBottleOrProductTool, self).__init__(host)

  def initialize(self, **args):

    self.args.add(name="bottle", type="instance", template="levelone", comboSqlQuery="SELECT * FROM levelone", optional=True, enabled=True)
    self.args.add(name="bottleNew", type="bool", value=False, label="new bottle")
    self.args.add(name="brand", type="str", combo=["Rk", "Gm", "Mu"], value="Rk", optional=True, enabled=False)
    self.args.add(name="bottletype", type="str", expression="[A-Z]+[a-zA-Z0-9_]*", optional=True, enabled=False)
    self.__row = self.args.beginRow("size")
    self.args.add(name="size", type="str", expression="[0-9]*", label="", optional=True, enabled=False)
    self.args.addStaticText("liters")
    self.args.endRow()
    self.args.addSpacer(10)
    self.args.add(name="productNew", type="bool", value=False, label="new product")
    self.args.add(name="serialNumber", type="str", optional=True, hidden=True, expression="[0-9]*")
    self.args.add(name="flavor", type="str", optional=True, hidden=True, expression="[A-Z]+[a-zA-Z0-9_]*")
    self.args.addSpacer(10)
    self.args.addButton("doit", "Create, then add more")


  def execute(self):

    db = self.host.apis['db']
    project = db.queryOne("Project", name="Rotkaeppchen")
    
    bottleNew = self.args.getValue("bottleNew")
    if bottleNew:
      brand = self.args.getValue("brand")
      bottletype = self.args.getValue("bottletype")
      size = self.args.getValue("size")
      bottleName = brand + "_" + bottletype + "_" + size + "l"
      createBottle = db.getOrCreateNew('Levelone', project=project, name=bottleName)
      # print "Created folder for bottle: " + bottleName
    else:
      bottleName = self.args.getValue("bottle").name

    bottle = db.queryOne("Levelone", name=bottleName)

    createModelingTask = db.getOrCreateNew("Leveltwo", levelone=bottle, name="_modeling")

    productNew = self.args.getValue("productNew")
    if productNew:
      serialNumber = self.args.getValue("serialNumber")
      flavor = self.args.getValue("flavor")
      productName = serialNumber + "_" + flavor
      createProduct = db.getOrCreateNew("Leveltwo", levelone=bottle, name=productName)
      # print "Created folder for product: " + productName

    print "Completed."



  def onButtonPressed(self, button):

    if button == "doit":
      self.execute()


  def onValueChanged(self, arg):

    if arg.name == "bottleNew":
      self.args.get("bottle").enabled = not arg.value
      self.args.get("brand").enabled = arg.value
      self.args.get("bottletype").enabled = arg.value
      self.args.get("size").enabled = arg.value
      # self.__row.hidden = not arg.value
      # self.args.layout.refresh()

    if arg.name == "productNew":
      self.args.get("serialNumber").hidden = not arg.value
      self.args.get("flavor").hidden = not arg.value




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

  tool = workshop.instantiate(cmd='newbottleorproduct')
  tool.invokeWithUI()


