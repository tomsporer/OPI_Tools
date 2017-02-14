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

    
