# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os, sys
import shutil
import ctypes

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException

class SubmitRenderTool(DataBaseTool):

  ToolName = 'SubmitRender'
  ToolLabel = 'Submits a scene for rendering'
  ToolCommand = 'submitrender'
  ToolDescription = 'Submits a scene for rendering'
  ToolTooltip = 'Submits a scene for rendering'

  def __init__(self, host):
    super (SubmitRenderTool, self).__init__(host)

  def initialize(self, **args):

    self.args.add(name='projectname', label='project', type='str', value=args.get('projectname', None))
    self.args.add(name="rendername", type="str", label="render name", value=args.get('name', 'default'))
    self.args.add(name="version", type="str", value=args.get('version', None), expression='[0-9]+[0-9]*')
    self.args.beginRow('range')
    self.args.add(name="in", type="int", value=args.get('in', None))
    self.args.add(name="out", type="int", value=args.get('out', None))
    self.args.endRow()

  def preexecute(self, **args):

    db = self.host.apis['db']
    maya = self.host.apis['maya']


    # check the project name
    # if it is not specified, set it based on the project
    projectname = self.args.getValue('projectname')
    if projectname is None:
      filePath = maya.cmds.file(q=True, sn=True)
      project = None
      try:
        project = db.queryFromPath('Project', filePath)
        if not project:
          raise OPIException('The scene is not in a valid project!')
      except:
        raise OPIException('The current scene is not part of a project.')
      arg = self.args.get('projectname')
      projectname = project.name
      arg.value = project.name
      arg.enabled = False

    # check the version
    version = self.args.getValue('version')
    if version is None:
      version = self.metaData.get(projectname+'_version', '001')
      self.args.setValue('version', version)

    # check the input and output
    for argName in ['in', 'out']:
      arg = self.args.get(argName)
      value = arg.value
      if arg.value is None:
        if argName == 'in':
          arg.value = maya.cmds.playbackOptions(q=True, animationStartTime=True)
        else:
          arg.value = maya.cmds.playbackOptions(q=True, animationEndTime=True)

  def __getProject(self):
    db = self.host.apis['db']
    projectname = self.args.getValue('projectname')
    project = db.queryOne('Project', name=projectname)
    if not project:
      raise OPIException('Project "%s" does not exist.' % projectname)
    return project

  def executeMaya (self):

    projectname = self.args.getValue('projectname')
    rendername = self.args.getValue('rendername')
    version = self.args.getValue('version')
    version = version.rjust(3, '0')
    startFrame = self.args.getValue('in')
    endFrame = self.args.getValue('out')

    db = self.host.apis['db']
    maya = self.host.apis['maya']

    # todo: inspect render setup
    # set renderer to redshift (maybe in defaults?)
    # set image format to exr
    # set file prefix accordingly (so that we end up as Render/name/version/aovname)



    project = self.__getProject()
    render = db.getOrCreateNew('Render', project=project, name=rendername, version=int(version))
    
    rs = maya.app.renderSetup.model.renderSetup.instance()
    layers = rs.getRenderLayers()
    for layer in layers:
      print str(layer.name())
      aov = db.getOrCreateNew('Aov', render=render, name=str(layer.name()))

    path = db.getPath(render.location)
    path = os.path.join(path, '<RenderLayer>', "%s_<RenderLayer>" % render.name)

    # todo: we should remap UNC paths as well.

    maya.cmds.setAttr("defaultRenderGlobals.imageFilePrefix", path, type="string")
    maya.cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)
    maya.cmds.setAttr("defaultRenderGlobals.animation", True)
    maya.cmds.setAttr("defaultRenderGlobals.extensionPadding", 4)
    maya.cmds.setAttr("defaultRenderGlobals.useMayaFileName", False)
    maya.cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", True)
    maya.cmds.setAttr("defaultRenderGlobals.periodInExt", True)
    maya.cmds.setAttr("defaultRenderGlobals.startFrame", int(startFrame))
    maya.cmds.setAttr("defaultRenderGlobals.endFrame", int(endFrame))

    # store the metadata for the next run
    setattr(self.metaData, projectname+'_version', version)
    # layers = rs.getRenderLayers()
    # print len(layers)

    # for layer in layers:
    #     print layer.name()
