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

    saveSelection = cmds.ls(selection=True)

    project = db.queryOne("project", name="Payback_App")

    locShapes = cmds.ls(type="locator")
    locTransforms = []
    for locShape in locShapes:
      locTransforms += cmds.listRelatives(locShape, parent=True)

    for loc in locTransforms:
      if ":" in loc:
        # print "# INFO: loc: \"" + loc + "\" - has a namespace"
        continue
      if len(loc.split("_")) != 4:
        # print "# INFO: loc: \"" + loc + "\" - length =/= 4"
        continue
      if len(cmds.listRelatives(loc, children=True)) > 1:
        # print "# INFO: loc: \"" + loc + "\" - more than one child"
        continue
      if not loc.split("_")[3].startswith("locator"):
        # print "# INFO: loc: \"" + loc + "\" - is probably no master locator"
        continue
        

      pObject = loc.split("_")[0]
      pType = loc.split("_")[1]
      pName = loc.split("_")[2]
      pLocator = loc.split("_")[3]
      
      if pName == "Random":
        pCacheList = db.query("pointee_cache", project=project, object=pObject, type=pType)
        numCaches = len(pCacheList)
        pCache = pCacheList[randint(0, numCaches-1)]
      else:
        pCache = db.queryOne("pointee_cache", project=project, object=pObject, type=pType, name=pName)

      refFolder = "E:/PROJECTS/PAY_Payback_App/Models/ref"
      refName = "Pointee_clean"
      refFilePath = os.path.join(refFolder, refName + ".mb")

      refImport = cmds.file( refFilePath, reference=True, type="mayaBinary", ignoreVersion=True, mergeNamespacesOnClash=False, namespace=refName, returnNewNodes=True)
      refNamespace = cmds.ls(refImport[0], showNamespace=True)[1]
      refParent = refNamespace + ":" + refName

      cmds.parent( refParent, loc, relative=True)

      ws = self.workShop
      importCacheTool = ws.instantiate(cmd='importcache')

      importCache = importCacheTool.invoke(object=pObject, type=pType, cache=pCache, importMode="Merge")
      importCacheNodes = importCache["cacheNode"].split()
      cmds.rename(importCacheNodes[0], loc + "_AlembicNode")

    
    cmds.select(saveSelection)