# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import sys

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException



class SetRenderOutputTool(DataBaseTool):

  ToolName = 'SetRenderOutputTest'
  ToolLabel = 'Set Output Paths Test'
  ToolCommand = 'setrenderoutput'
  ToolDescription = 'set the paths for the renders'
  ToolTooltip = 'sets the paths for the renders'

  def __init__(self, host):
    super (SetRenderOutputTool, self).__init__(host)

  def initialize(self, **args):

    self.args.add(name='projectname', label='project', type='str', value=args.get('projectname', None), enabled=False)
    self.args.add(name="renderfolder", type="str", label="render folder", value="", enabled=True, expression="[a-zA-Z0-9_/]*")
    self.args.add(name="rendername", type="str", label="render name", value=args.get('rendername', ""))
    self.args.beginRow("version")
    self.args.add(name="version", label="", type="str", value=args.get('version', None), expression='[0-9]+[0-9]*')
    self.args.addButton("plusOne", "+1")
    self.args.endRow()
    self.args.beginRow('range')
    self.args.add(name="changeRange", label="", type="bool", value=False)
    self.args.add(name="in", type="int", value=args.get('in', None), optional=True, enabled=False)
    self.args.add(name="out", type="int", value=args.get('out', None), optional=True, enabled=False)
    self.args.endRow()

  def preexecute(self, **args):

    db = self.host.apis['db']


    if self.host.apis.has_key('maya'):
      maya = self.host.apis['maya']
      filePath = maya.cmds.file(q=True, sn=True)
    else:
      filePath = "E:/PROJECTS/BEI_Spiel/3D/asdf.ma"
    filename = os.path.split(filePath)[1]


    # check the project name
    # if it is not specified, set it based on the project
    projectname = self.args.getValue('projectname')
    if projectname is None:
      project = None
      try:
        project = db.queryFromPath('Project', filePath)
        if not project:
          raise OPIException('The scene is not in a valid project!')
      except:
        raise OPIException('The current scene is not part of a project.')
      projectname = project.name
      self.args.setValue('projectname', projectname)


    # check saved metaData
    version = self.args.getValue('version')
    renderfolder = self.args.getValue("renderfolder")
    rendername = self.args.getValue("rendername")
    if version is None:
      version = self.metaData.get(projectname+'_version', '01')
      self.args.setValue('version', version)
    if renderfolder == "":
      renderfolder = self.metaData.get(projectname+"_renderfolder", "")
      self.args.setValue("renderfolder", renderfolder)
    if rendername == "":
      scenename = filename.rsplit("_", 1)[0]
      rendername = self.metaData.get(projectname+"_rendername", scenename)
      self.args.setValue("rendername", rendername)



  def __getProject(self):
    db = self.host.apis['db']
    projectname = self.args.getValue('projectname')
    project = db.queryOne('Project', name=projectname)
    if not project:
      raise OPIException('Project "%s" does not exist.' % projectname)
    return project

  def execute(self):
    print "heeeeellooooooo"
    # self.executeMaya()

  def executeMaya (self):

    projectname = self.args.getValue('projectname')
    renderfolder = self.args.getValue('renderfolder')
    rendername = self.args.getValue('rendername')
    version = self.args.getValue('version')
    version = version.rjust(2, '0')
    startFrame = self.args.getValue('in')
    endFrame = self.args.getValue('out')

    db = self.host.apis['db']
    maya = self.host.apis['maya']

  #   # todo: inspect render setup
  #   # set renderer to redshift (maybe in defaults?)
  #   # set image format to exr
  #   # set file prefix accordingly (so that we end up as Render/name/version/aovname)


    project = self.__getProject()
    render = db.getOrCreateNew('Render', project=project, name=renderfolder, version=int(version))
    
    # try:
    #   rs = maya.app.renderSetup.model.renderSetup.instance()
    # except:
    #   raise OPIException('Legacy Render Layers are currently NOT supported')

    renderfile = rendername + "_<renderlayer>_V" + str(version)
    renderPrefix = os.path.join(renderfolder, "V" + version, renderfile)
    print "renderPrefix: " + renderPrefix

    maya.cmds.setAttr("defaultRenderGlobals.imageFilePrefix", renderPrefix, type="string")
    maya.cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)
    maya.cmds.setAttr("redshiftOptions.imageFormat", 1) # 1 = exr
    maya.cmds.setAttr("defaultRenderGlobals.animation", True)
    maya.cmds.setAttr("defaultRenderGlobals.extensionPadding", 5)
    maya.cmds.setAttr("defaultRenderGlobals.useMayaFileName", False)
    maya.cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", True)
    maya.cmds.setAttr("defaultRenderGlobals.periodInExt", True)

    if self.args.getValue("changeRange") == True:
      maya.cmds.setAttr("defaultRenderGlobals.startFrame", int(startFrame))
      maya.cmds.setAttr("defaultRenderGlobals.endFrame", int(endFrame))

    # store the metadata for the next run
    setattr(self.metaData, projectname+'_version', version)
    setattr(self.metaData, projectname+"_renderfolder", renderfolder)
    setattr(self.metaData, projectname+"_rendername", rendername)
  #   # layers = rs.getRenderLayers()
  #   # print len(layers)

  #   # for layer in layers:
  #   #     print layer.name()



  def onButtonPressed(self, button):

    if button == "plusOne":
      version = self.args.getValue("version")
      versionPlus = str(int(version) + 1).rjust(2,"0")
      self.args.setValue("version", versionPlus)

  def onValueChanged(self, arg):

    if arg.name == "changeRange":
      self.args.get("in").enabled = arg.value
      self.args.get("out").enabled = arg.value
    elif arg.name == "in":
      if arg.value > self.args.getValue("out"):
        self.args.setValue("out", arg.value)
    elif arg.name == "out":
      if arg.value < self.args.getValue("in"):
        self.args.setValue("in", arg.value)







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

  db = OpiDB(dbRoot, templateRoot=templateRoot, rootSubFolders=['BEI_Spiel'])

  host = OPIHost('python', {'db': db, 'QtWidgets': QtWidgets, 'QtCore': QtCore})
  workshop = OPIWorkShop(host, toolRoot)

  tool = workshop.instantiate(cmd='setrenderoutput')
  tool.invokeWithUI()

