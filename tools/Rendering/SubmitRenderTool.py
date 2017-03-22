# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import sys
import math
import shutil
import ctypes

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
import opi.networking.unctools as unctools
from opi.jobs.jobmanager import JobManager

from opi.ui.args.listviewargwidget import ListViewArgWidget

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
    self.args.add(name="rendername", type="str", label="render name", value=args.get('name', 'sh01'))
    self.args.add(name="version", type="str", value=args.get('version', None), expression='[0-9]+[0-9]*')
    self.args.beginRow('range')
    self.args.add(name="in", type="int", value=args.get('in', None))
    self.args.add(name="out", type="int", value=args.get('out', None))
    self.args.endRow()
    self.args.add(name="package", type="int", value=args.get('package', 10))
    self.args.add(name="layers", type="str", value=args.get('layers', None))

  def preexecute(self, **args):

    db = self.host.apis['db']
    maya = self.host.apis['maya']

    # check all external paths
    uncMap = unctools.getUNCMap()
    nodes = maya.cmds.ls()
    changedSomething = False
    for node in nodes:
        t = maya.cmds.nodeType(node)
        param = None
        if t == 'file':
          param = 'fileTextureName'
        else:
          continue
        path = maya.cmds.getAttr('%s.%s' % (node, param))
        mappedPath = unctools.remapPath(path, uncMap)
        if mappedPath != path:
          changedSomething = True
          maya.cmds.setAttr('%s.%s' % (node, param), mappedPath, type='string')
          self.log("Remapped %s to %s" % (path, mappedPath))

    # check the project name
    # if it is not specified, set it based on the project
    projectname = self.args.getValue('projectname')
    if projectname is None:
      self.__filePath = maya.cmds.file(q=True, sn=True)
      self.__filePath = unctools.remapPath(self.__filePath, uncMap)
      project = None
      try:
        project = db.queryFromPath('Project', self.__filePath)
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

    layers = self.args.getValue('layers')
    if layers is None:
      rs = maya.app.renderSetup.model.renderSetup.instance()
      layers = [rs.getDefaultRenderLayer()] + rs.getRenderLayers()
      layerNames = []
      for layer in layers:
          if not layer.isRenderable():
            continue
          layerNames += [str(layer.name())]
      arg = self.args.get('layers')
      arg.value = ','.join(layerNames)

    if changedSomething:
      maya.cmds.file(save=True, f=True)

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
    packageSize = self.args.getValue('package')
    enabledLayers = self.args.getValue('layers').split(',')

    db = self.host.apis['db']
    maya = self.host.apis['maya']
    pymel = self.host.apis['pymel']

    # todo: inspect render setup
    # set renderer to redshift (maybe in defaults?)
    # set image format to exr
    # set file prefix accordingly (so that we end up as Render/name/version/aovname)

    project = self.__getProject()

    render = db.getOrCreateNew('Render', project=project, name=rendername, version=int(version))

    rs = maya.app.renderSetup.model.renderSetup.instance()
    layers = [rs.getDefaultRenderLayer()] + rs.getRenderLayers()
    for layer in layers:
      layerName = str(layer.name())
      if layerName == 'defaultRenderLayer':
        layerName = 'masterLayer'

      aov = db.getOrCreateNew('Aov', render=render, name=layerName)

    path = db.getPath(render.location)
    path = os.path.join(path, '<RenderLayer>', "%s_<RenderLayer>" % render.name)

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

    with JobManager((os.environ['OPI_JOB_SERVER'], 6666)) as manager:
      group_id = manager.getOrCreateProjectGroup('Tom Sporer')
      project_id = manager.getOrCreateProject(group_id=group_id, name='%s_%s' % (project.shorthand, project.name))

      launcher = None
      if self.host.name == 'maya':
        mayaVersion = str(pymel.core.mel.eval('getApplicationVersionAsFloat'))
        if mayaVersion.endswith('.0'):
          mayaVersion = mayaVersion.rpartition('.')[0]
        software_id = manager.getOrCreateSoftware(name='Maya', version=mayaVersion, registrykey='HKEY_LOCAL_MACHINE/SOFTWARE\\Autodesk\\Maya\\{0}\\Setup\\InstallPath|MAYA_INSTALL_LOCATION'.format(mayaVersion))
        launcher = '%s/Maya%s.pyw' % (os.environ['OPI_LAUNCHER_DIR'], mayaVersion.partition('.')[0])
      else:
        # other apps are not yet implemented
        return

      taskCount = int((1 + endFrame - startFrame) / packageSize)

      renderCamera = None
      cameras = pymel.core.mel.eval("listTransforms -cameras;")
      for camera in cameras:
        if maya.cmds.getAttr(camera+'.renderable'):
          renderCamera = camera

      for layer in layers:

        layerName = str(layer.name())

        if not layerName in enabledLayers:
          continue

        layerLabel = layerName
        if layerLabel == 'defaultRenderLayer':
          layerLabel = 'masterLayer'

        job_id = manager.createJob(
          name="%s - %s" % (version, layerLabel),
          owner="user", # todo
          type='LauncherTask',
          project_id=project_id,
          software_id=software_id,
          launcher=launcher)

        for task_id in range(taskCount):
          i = task_id * packageSize + startFrame
          o = i + packageSize - 1
          if o > endFrame:
            o = endFrame

          cmd =  'loadPlugin "tom_sporer_commands"; loadPlugin "tom_sporer_events"; loadPlugin("opi_maya"); '
          cmd += 'ts_render -s "%s" -i %d -o %d -l "%s" -c "%s";' % (self.__filePath, i, o, layerName, renderCamera)
          manager.createTask(job_id=job_id, package=task_id, status='pending', taskargs={'batch': None, 'command': cmd, 'sourcefile': self.__filePath})

    maya.cmds.file(f=True, s=True)

  # implement this to provide a custom widget
  def getWidgetForArg(self, parent, arg, **args):
    maya = self.host.apis['maya']

    if arg.name == 'layers':
      previousValue = arg.value
      rs = maya.app.renderSetup.model.renderSetup.instance()
      layers = [rs.getDefaultRenderLayer()] + rs.getRenderLayers()
      layerNames = []
      for layer in layers:
          layerNames += [str(layer.name())]
      arg.value = ','.join(layerNames)

      widget = ListViewArgWidget(parent, arg, **args)
      arg.value = previousValue
      return widget

    return super(SubmitRenderTool, self).getWidgetForArg(parent, arg, **args)
