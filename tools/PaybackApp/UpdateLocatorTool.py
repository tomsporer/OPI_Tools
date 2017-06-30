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

class UpdateLocatorTool(DataBaseTool):

  ToolName = 'UpdateLocator'
  ToolLabel = 'Update Locator'
  ToolCommand = 'updatelocator'
  ToolDescription = 'Update Locator'
  ToolTooltip = 'Update Locator'

  def __init__(self, host):
    super (UpdateLocatorTool, self).__init__(host)
    # self._noUI = True

  def initialize(self, **args):
    self.args.add(name="selection", type="str", value=args.get("selection", ""), hidden=True)
    self.args.add(name="genericassets", type="bool", value=args.get("genericassets", False))
    self.args.add(name="randoffset", type="bool", value=args.get("randoffset", False))
    
  def preexecute(self, **args):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    sel = self.args.getValue("selection")
    if sel == "":
      sel = cmds.ls(selection=True)
    else:
      sel = sel.split()

    self.__sel = sel

  def deleteAlembicNode(self, rootLocator):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    lr = cmds.listRelatives(rootLocator, allDescendents=True, path=True)
    for r in lr:
      if cmds.nodeType(r) == "mesh":
        lc = cmds.listConnections(r, connections=True)
        for c in lc:
          if "AlembicNode" in c:
            cmds.delete(c)
            break
        else:
          continue
      else:
        continue
      break

  def executeMaya(self):
    db = self.host.apis['db']
    maya = self.host.apis['maya']
    cmds = maya.cmds

    project = db.queryOne("project", name="Payback_App")

    ws = self.workShop
    importCacheTool = ws.instantiate(cmd="importcache")

    refFolder = "E:/PROJECTS/PAY_Payback_App/Models/ref"
    sel = self.__sel

    possibleAssets = db.query("pointee_asset", project=project)

    progressMax = len(sel)
    progress = float(0)
    for loc in sel:
      percent = round((progress/progressMax)*100, 1)
      print "# ---- PROGRESS: %s%% ----" %(percent)
      cObject = loc.split("_")[0]
      cType = loc.split("_")[1]
      cName = loc.split("_")[2]
      cLocator = loc.split("_")[3]

      if self.args.getValue("randoffset"):
        randOffset = randint(-50, 0)
      else:
        randOffset = 0

      self.deleteAlembicNode(loc)

      # Importing new pointee ref under empty locator
      foundPointeeRef = False
      while not foundPointeeRef:
        children = cmds.listRelatives(loc, children=True)
        if len(children) == 1:
          print "# INFO: no Pointee ref model found. importing now..."
          refName = "Pointee_clean"
          refFilePath = os.path.join(refFolder, refName + ".mb")

          loadUnload = randint(0, 100)
          refImport = cmds.file( refFilePath, reference=True, type="mayaBinary", ignoreVersion=True, mergeNamespacesOnClash=False, namespace=refName, returnNewNodes=True)
          pointeeRefNamespace = cmds.ls(refImport[0], showNamespace=True)[1]
          pointeeRef = pointeeRefNamespace + ":" + refName

          cmds.parent( pointeeRef, loc, relative=True)

          foundPointeeRef = True
        
        # Cleaning up locator with children
        else:
          print "# INFO: found children. cleaning up..."
          for c in children:
            if cmds.referenceQuery(c, isNodeReferenced=True):
              refFile = cmds.referenceQuery(c, filename=True)
              if refFile.split("{")[0] != "E:/PROJECTS/PAY_Payback_App/Models/ref/Pointee_clean.mb":
                print "# INFO: removing reference \"" + str(c) + "\""
                for nonRef in cmds.listRelatives(c, children=True):
                  if not cmds.referenceQuery(nonRef, isNodeReferenced=True):
                    print "# INFO: deleting \"%s\"" %(nonRef)
                    cmds.delete(nonRef)
                cmds.file(refFile, removeReference=True, force=True)
              else:
                foundPointeeRef = True
                pointeeRef = c
                pointeeRefNamespace = cmds.ls(c, showNamespace=True)[1]
            elif not cmds.objectType(c, isType="locator"):
              print "# INFO: deleting \"%s\"" %(c)
              cmds.delete(c)

      # Importing pointee cache
      print "# INFO: importing cache..."
      if cName == "Random":
        pCacheList = db.query("pointee_cache", project=project, object=cObject, type=cType)
        numCaches = len(pCacheList)
        pCache = pCacheList[randint(0, numCaches-1)]
      else:
        pCache = db.queryOne("pointee_cache", project=project, object=cObject, type=cType, name=cName)
      cmds.select(pointeeRef)
      importCache = importCacheTool.invoke(object=cObject, type=cType, cache=pCache, importMode="Merge")
      importCacheNodes = importCache["cacheNode"].split()
      abcNode = cmds.rename(importCacheNodes[0], loc + "_AlembicNode")
      cmds.setAttr(abcNode + ".cycleType", 1) # 1 = loop
      cmds.setAttr(abcNode + ".offset", randOffset)

      # Special case
      if cType == "Special":
        print "# INFO: importing special asset"
        assetQuery = db.query("pointee_asset", project=project, type="Special")
        for asset in assetQuery:
          if asset.name.lower() in cName.lower():
            # Importing asset ref
            refName = "Asset_Special_" + asset.name
            refFilePath = os.path.join(refFolder, refName + ".mb")

            refImport = cmds.file( refFilePath, reference=True, type="mayaBinary", ignoreVersion=True, mergeNamespacesOnClash=False, namespace=refName, returnNewNodes=True)
            refNamespace = cmds.ls(refImport[0], showNamespace=True)[1]
            assetRef = refNamespace + ":" + refName

            cmds.parent( assetRef, loc, relative=True)

            # Importing asset cache
            aCache = db.queryOne("pointee_cache", project=project, object="Asset", type=cType, name=cName)
            if aCache == None:
              missingCache = "Asset_%s_%s.abc" %(cType, cName)
              print "# ERROR: No cache found for special asset. Missing \"%s\"" %(missingCache)
            else:
              cmds.select(assetRef)
              importCache = importCacheTool.invoke(object="Asset", type=cType, cache=aCache, importMode="Merge")
              importCacheNodes = importCache["cacheNode"].split()
              abcNode = cmds.rename(importCacheNodes[0], "Asset_%s_%s_%s_AlembicNode" %(cType, cName, cLocator))
              cmds.setAttr(abcNode + ".cycleType", 1) # 1 = loop
              cmds.setAttr(abcNode + ".offset", randOffset)

            break
        else:
          print "# ERROR: no asset found for special cache \"%s\"" %(cName)


      if "baby" in cName.lower():
        # Importing baby hair
        refName = "Asset_Baby_Hair"
        refFilePath = os.path.join(refFolder, refName + ".mb")

        refImport = cmds.file( refFilePath, reference=True, type="mayaBinary", ignoreVersion=True, mergeNamespacesOnClash=False, namespace=refName, returnNewNodes=True)
        refNamespace = cmds.ls(refImport[0], showNamespace=True)[1]
        assetRef = refNamespace + ":" + refName

        cmds.parent( assetRef, loc, relative=True)

        cmds.parentConstraint(pointeeRefNamespace + ":M_Body_JNT", assetRef, maintainOffset=False)
        cmds.scaleConstraint(pointeeRefNamespace + ":M_Body_JNT", assetRef, maintainOffset=False)

      if self.args.getValue("genericassets"):
        # Import generic assets
        if "girl" in cName.lower():
          # Importing girl schleife
          refName = "Asset_Girl_Schleife"
          refFilePath = os.path.join(refFolder, refName + ".mb")

          refImport = cmds.file( refFilePath, reference=True, type="mayaBinary", ignoreVersion=True, mergeNamespacesOnClash=False, namespace=refName, returnNewNodes=True)
          refNamespace = cmds.ls(refImport[0], showNamespace=True)[1]
          assetRef = refNamespace + ":" + refName

          cmds.parent( assetRef, loc, relative=True)

          cmds.parentConstraint(pointeeRefNamespace + ":M_Body_JNT", assetRef, maintainOffset=False)
          cmds.scaleConstraint(pointeeRefNamespace + ":M_Body_JNT", assetRef, maintainOffset=False)
        else:
          # Choosing random generic assets
          gAssetList = db.query("pointee_asset", project=project, type="Girl")
          numGAssets = len(gAssetList)
          tAssetList = db.query("pointee_asset", project=project, type="Top")
          numTAssets = len(tAssetList)
          eAssetList = db.query("pointee_asset", project=project, type="Eyes")
          numEAssets = len(eAssetList)
          mAssetList = db.query("pointee_asset", project=project, type="Mouth")
          numMAssets = len(mAssetList)
          percentGirl = 20
          percentTop = 65
          percentEyes = 20
          percentMouth = 35
          randGirl = randint(0, 100)
          randTop = randint(0, 100)
          randEyes = randint(0, 100)
          randMouth = randint(0, 100)
          assetList = []
          if randGirl <= percentGirl:
            assetList.append(gAssetList[randint(0,numGAssets-1)])
          else:
            if randTop <= percentTop:
              assetList.append(tAssetList[randint(0,numTAssets-1)])
            if randEyes <= percentEyes:
              assetList.append(eAssetList[randint(0,numEAssets-1)])
            if randMouth <= percentMouth:
              assetList.append(mAssetList[randint(0,numMAssets-1)])

          # Importing assets
          for asset in assetList:
            refName = "Asset_%s_%s" %(asset.type, asset.name)
            refFilePath = os.path.join(refFolder, refName + ".mb")

            refImport = cmds.file( refFilePath, reference=True, type="mayaBinary", ignoreVersion=True, mergeNamespacesOnClash=False, namespace=refName, returnNewNodes=True)
            refNamespace = cmds.ls(refImport[0], showNamespace=True)[1]
            assetRef = refNamespace + ":" + refName

            cmds.parent( assetRef, loc, relative=True)

            cmds.parentConstraint(pointeeRefNamespace + ":M_Body_JNT", assetRef, maintainOffset=False)
            cmds.scaleConstraint(pointeeRefNamespace + ":M_Body_JNT", assetRef, maintainOffset=False)

      progress += 1



    # Restore original selection
    cmds.select(sel)

