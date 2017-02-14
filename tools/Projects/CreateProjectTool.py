# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os, sys

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

    self.args.add(name='shorthand', type='str', expression="[A-Z][A-Z][A-Z]")
    self.args.add(name='name', type='str', expression="[A-Z]+[a-zA-Z0-9_]*")

  def execute (self):

    shorthand = self.args.getValue('shorthand')
    name = self.args.getValue('name')

    db = self.host.apis['db']
  
    project = db.createNew('Project', shorthand=shorthand, name=name)
    task3D = db.createNew('Task', project=project, name='3D')
    taskComposite = db.createNew('Task', project=project, name='Composite')    

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

workspace -fr "images" "Images";
workspace -fr "sourceImages" "Images";
workspace -fr "clips" "Images";
workspace -fr "3dPaintTextures" "Images/3dPaintTextures";

workspace -fr "fluidCache" "Cache/nCache/fluid";
workspace -fr "fileCache" "Cache/nCache";
workspace -fr "particles" "Cache/particles";
workspace -fr "bifrostCache" "Cache/bifrost";

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

    self.host.apis['pymel'].core.mel.eval('setProject "%s"' % projectPath.replace("\\", '/'))
