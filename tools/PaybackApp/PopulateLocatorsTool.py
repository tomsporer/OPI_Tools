# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Tom Sporer. All rights reserved.
#

import os
import sys
from random import randint

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject

class PopulateLocatorsTool(DataBaseTool):

  ToolName = 'PopulateLocators'
  ToolLabel = 'Populate Locators'
  ToolCommand = 'populatelocators'
  ToolDescription = 'Populate Locators'
  ToolTooltip = 'Populate Locators'

  def __init__(self, host):
    super (PopulateLocatorsTool, self).__init__(host)
    self._noUI = True


  def executeMaya(self):
    db = self.host.apis['db']
    maya = self.host.apis['maya']
    cmds = maya.cmds

    sel = cmds.ls(selection=True)

    if len(sel) == 0:
      locShapes = cmds.ls(type="locator")
      locTransforms = []
      for locShape in locShapes:
        locTransforms += cmds.listRelatives(locShape, parent=True)
    else:
      locTransforms = sel

    project = db.queryOne("project", name="Payback_App")

    ws = self.workShop
    updateLocatorTool = ws.instantiate(cmd='updatelocator')

    locList = ""
    for loc in locTransforms:
      if ":" in loc:
        # print "# INFO: loc: \"" + loc + "\" - has a namespace"
        continue
      elif len(loc.split("_")) != 4:
        # print "# INFO: loc: \"" + loc + "\" - length =/= 4"
        continue
      elif len(cmds.listRelatives(loc, children=True)) > 1:
        # print "# INFO: loc: \"" + loc + "\" - more than one child"
        continue
      elif not loc.split("_")[3].startswith("locator"):
        # print "# INFO: loc: \"" + loc + "\" - is probably no master locator"
        continue
      else:
        locList += loc + " "

    if not locList == "":
      updateLocatorTool.invoke(selection=locList)

    
    cmds.select(sel)