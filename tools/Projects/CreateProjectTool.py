# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os, sys
import shutil
import ctypes

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException

class CreateProjectTool(DataBaseTool):

  ToolName = 'CreateProject'
  ToolLabel = 'Create New Project'
  ToolCommand = 'createproject'
  ToolDescription = 'creates a new project'
  ToolTooltip = 'creates a new project'

  def __init__(self, host):
    super (CreateProjectTool, self).__init__(host)

  def initialize(self, **args):

    self.args.add(name='shorthand', type='str', label="shorthand", optional=True, expression="[A-Z][A-Z][A-Z]")
    self.args.add(name='name', type='str', expression="[A-Z]+[a-zA-Z0-9_]*")
    self.args.add(name="active", type="bool", label="Set Active Project", value="true")

  def execute (self):

    name = self.args.getValue('name')
    active = self.args.getValue("active")

    shorthand = self.args.getValue('shorthand')
    if not shorthand:
      shorthand = str(name)[:3].upper().replace("_", "")

    db = self.host.apis['db']

    project = db.createNew('Project', shorthand=shorthand, name=name)
    task3D = db.createNew('Task', project=project, name='3D')
    taskComposite = db.createNew('Task', project=project, name='Composite')    

    #
    # Maya specific project files:
    
    workspaceContent = """
// Tom Sporer Project Definition - Maya 2017

workspace -fr "STL_ATF" "Models";
workspace -fr "DAE_FBX" "Models";
workspace -fr "NX_ATF" "Models";
workspace -fr "OBJ" "Models";
workspace -fr "FBX export" "Models";
workspace -fr "BIF" "Models";
workspace -fr "DAE_FBX export" "Models";
workspace -fr "CATIAV5_ATF" "Models";
workspace -fr "ASS Export" "Models";
workspace -fr "move" "Models";
workspace -fr "FBX" "Models";
workspace -fr "CATIAV4_ATF" "Models";
workspace -fr "eps" "Models";
workspace -fr "translatorData" "Models";
workspace -fr "SAT_ATF" "Models";
workspace -fr "PROE_ATF" "Models";
workspace -fr "INVENTOR_ATF" "Models";
workspace -fr "STEP_ATF" "Models";
workspace -fr "IGES_ATF" "Models";
workspace -fr "ASS" "Models";
workspace -fr "Alembic" "Models";
workspace -fr "illustrator" "Models";
workspace -fr "diskCache" "Models";
workspace -fr "OBJexport" "Models";
workspace -fr "JT_ATF" "Models";
workspace -fr "sound" "Models";
workspace -fr "audio" "Models";
workspace -fr "templates" "Models";

workspace -fr "sourceImages" "Images";
workspace -fr "clips" "Images";
workspace -fr "3dPaintTextures" "Images/3dPaintTextures";

workspace -fr "fluidCache" "Cache/nCache/fluid";
workspace -fr "fileCache" "Cache/nCache";
workspace -fr "particles" "Cache/particles";
workspace -fr "bifrostCache" "Cache/bifrost";

workspace -fr "images" "Render";
workspace -fr "movie" "Render";
workspace -fr "renderData" "Render";
workspace -fr "shaders" "Render/shaders";
workspace -fr "iprImages" "Render/iprImages";
workspace -fr "depth" "Render/depth";
workspace -fr "furShadowMap" "Render/fur/furShadowMap";
workspace -fr "furFiles" "Render/fur/furFiles";
workspace -fr "furEqualMap" "Render/fur/furEqualMap";
workspace -fr "furImages" "Render/fur/furImages";
workspace -fr "furAttrMap" "Render/fur/furAttrMap";

workspace -fr "scripts" "Scripts";
workspace -fr "mel" "Scripts";

workspace -fr "offlineEdit" "{0}/Edits";
workspace -fr "mayaAscii" "{0}";
workspace -fr "autoSave" "{0}/Autosave";
workspace -fr "mayaBinary" "{0}";
workspace -fr "scene" "{0}";

workspace -fr "timeEditor" "Time Editor";

workspace -fr "sceneAssembly" "sceneAssembly";
workspace -fr "teClipExports" "Time Editor/Clip Exports";
""".format(task3D.location.partition('/')[2])

    projectPath = db.getPath(project.location)
    with open(os.path.join(projectPath, 'workspace.mel'), 'wb') as f:
      f.write(workspaceContent)

    #
    # XSI specific project files:

    launchersPath = os.environ['OPI_LAUNCHER_DIR']
    xsiSystemFolder = os.path.join(projectPath, "system")
    os.mkdir(xsiSystemFolder)
    shutil.copy(os.path.join(os.path.split(launchersPath)[0], "xsi", "dsprojectinfo"), xsiSystemFolder)
    # make system folder hidden:
    ctypes.windll.kernel32.SetFileAttributesW(unicode(xsiSystemFolder), 2)


    #
    # Set active project

    if active:
      if self.host.apis.has_key("pymel"):
        self.host.apis['pymel'].core.mel.eval('setProject "%s"' % projectPath.replace("\\", '/'))
      elif self.host.apis.has_key("xsi"):
        xsi = self.host.apis['xsi']
        xsi.ActiveProject = projectPath

