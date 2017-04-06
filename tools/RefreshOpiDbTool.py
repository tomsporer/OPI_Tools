# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.client.database import DataBase as OpiDB


class RefreshOpiDbTool(DataBaseTool):

  ToolName = 'RefreshDb'
  ToolLabel = 'Refresh Database'
  ToolCommand = 'refreshdatabase'
  ToolDescription = 'Refresh Database'
  ToolTooltip = 'Refresh Database'

  def __init__(self, host):
    super (RefreshOpiDbTool, self).__init__(host)
    self._noUI = True


  def preexecute(self):
    print "\nOPI: Refresh Database - Starting\nPlease wait a moment..."

  def execute(self):


    db = self.host.apis['db']
    opiDbRoot = os.environ['OPI_DATABASE_DIR']
    opiTemplateRoot = os.environ['OPI_TEMPLATE_DIR']
    opiProjects = db.query("project", sql="SELECT * FROM project")

    opiProjectLocations = []
    for p in opiProjects:
      opiProjectLocations.append(str(p.location))
    # print opiProjectLocations
    self.host.apis['db'] = OpiDB(opiDbRoot, templateRoot=opiTemplateRoot, rootSubFolders=opiProjectLocations)

    print "Refresh Database - Completed!"

