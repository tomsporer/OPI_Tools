# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os, sys
import shutil
import ctypes

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException

class SetRenderOutputTool(DataBaseTool):

  ToolName = 'SetRenderOutput'
  ToolLabel = 'Set Output Paths'
  ToolCommand = 'setrenderoutput'
  ToolDescription = 'set the paths for the renders'
  ToolTooltip = 'sets the paths for the renders'

  def __init__(self, host):
    super (SetRenderOutputTool, self).__init__(host)

  def initialize(self, **args):

    self.args.add(name='projectname', label='project', type='str')
    self.args.add(name="rendername", type="str", label="render name", value=args.get('name', None))
    self.args.add(name="version", type="str", value='001', enabled=False)

  def preexecute(self, **args):

    db = self.host.apis['db']
    maya = self.host.apis['maya']
    
    # check the project name
    # if it is not specified, set it based on the project
    projectname = self.args.getValue('projectname')
    if projectname is None:
      filePath = maya.cmds.file(q=True, sn=True)
      project = db.queryFromPath('Project', filePath)
      if not project:
        raise OPIException('The scene is not in a valid project!')
      arg = self.args.get('projectname')
      arg.value = project.name
      arg.enabled = False

    # check the render name, and set it based on the scene if possible
    rendername = self.args.getValue('rendername')
    if rendername is None:
      filePath = maya.cmds.file(q=True, sn=True)
      rendername = os.path.split(filePath)[1]
      rendername = rendername.rpartition('.')[0]
      rendername = rendername.rpartition('_')[0]

      arg = self.args.get('rendername')
      arg.value = rendername
      self.onValueChanged(arg)

  def __getProject(self):
    db = self.host.apis['db']
    projectname = self.args.getValue('projectname')
    project = db.queryOne('Project', name=projectname)
    if not project:
      raise OPIException('Project "%s" does not exist.' % projectname)
    return project

  def onValueChanged(self, arg):

    db = self.host.apis['db']

    if arg.name == 'rendername':

      version = '001'
      
      # find the highest version
      project = self.__getProject()
      model = db.getTemplate('Render').model
      renders = project.renders.where(model.name == arg.value).order_by(-model.version)
      if renders.count() > 0:
        lastRender = renders.get()
        version = str(lastRender.version + 1).rjust(3, '0')

      arg = self.args.get('version')
      arg._setValue(version, forceEnabled=True)

  def executeMaya (self):

    projectname = self.args.getValue('projectname')
    rendername = self.args.getValue('rendername')
    version = self.args.getValue('version')

    db = self.host.apis['db']

    # todo: inspect render setup
    # set renderer to redshift (maybe in defaults?)
    # set image format to exr
    # set file prefix accordingly (so that we end up as Render/name/version/aovname)

    project = self.__getProject()
    render = db.createNew('Render', project=project, name=rendername, version=int(version))

    # todo: for all render layers create the right aov
    # we might also need a tool to generate the default AOVs for redshift

    pass
