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

class UpdateRsProxyTool(DataBaseTool):

  ToolName = 'UpdateRsProxy'
  ToolLabel = 'Update rsProxy'
  ToolCommand = 'updatersproxy'
  ToolDescription = 'Update rsProxy'
  ToolTooltip = 'Update rsProxy'


  def __init__(self, host):
    super (UpdateRsProxyTool, self).__init__(host)
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

  def getAlembicNode(self, rootLocator):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    lr = cmds.listRelatives(rootLocator, allDescendents=True, path=True)
    for r in lr:
      lc = cmds.listConnections(r, connections=True)
      if not lc == None:
        for c in lc:
          if "AlembicNode" in c:
            return c
            break

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
    mel = maya.mel

    project = db.queryOne("project", name="Payback_App")

    ws = self.workShop
    importCacheTool = ws.instantiate(cmd="importcache")

    refFolder = "E:/PROJECTS/PAY_Payback_App/Models/ref"
    sel = self.__sel

    possibleAssets = db.query("pointee_asset")

    progressMax = len(sel)
    progress = float(0)
    for loc in sel:
      percent = round((progress/progressMax)*100, 1)
      print "# ---- PROGRESS: %s%% ----" %(percent)
      print "# INFO: Updating " + loc
      cObject = loc.split("_")[0]
      cType = loc.split("_")[1]
      cName = loc.split("_")[2]
      cLocator = loc.split("_")[3]

      if self.args.getValue("randoffset"):
        randOffset = randint(-50, 0)
      else:
        randOffset = 0

      self.deleteAlembicNode(loc)

      # Importing new centerJnt under empty locator
      foundCenterJnt = False
      while not foundCenterJnt:
        children = cmds.listRelatives(loc, children=True, path=True)
        if len(children) == 1:
          print "# INFO: no centerJnt ref model found. importing now..."
          refName = "Pointee_centerJnt"
          refFilePath = os.path.join(refFolder, refName + ".mb")

          loadUnload = randint(0, 100)
          refImport = cmds.file( refFilePath, reference=True, type="mayaBinary", ignoreVersion=True, mergeNamespacesOnClash=False, namespace=refName, returnNewNodes=True)
          pointeeRefNamespace = cmds.ls(refImport[0], showNamespace=True)[1]
          pointeeRef = pointeeRefNamespace + ":" + refName

          cmds.parent( pointeeRef, loc, relative=True)
          foundCenterJnt = True
        
        # Cleaning up locator with children
        else:
          print "# INFO: found children. cleaning up..."
          for c in children:
            if cmds.referenceQuery(c, isNodeReferenced=True):
              print "c is ref " + c
              refFile = cmds.referenceQuery(c, filename=True)
              if refFile.split("{")[0] != "E:/PROJECTS/PAY_Payback_App/Models/ref/Pointee_centerJnt.mb":
                print "# INFO: removing reference \"" + str(c) + "\""
                for nonRef in cmds.listRelatives(c, children=True):
                  if not cmds.referenceQuery(nonRef, isNodeReferenced=True):
                    print "# INFO: deleting \"%s\"" %(nonRef)
                    cmds.delete(nonRef)
                cmds.file(refFile, removeReference=True, force=True)
              else:
                foundCenterJnt = True
                pointeeRef = c
                pointeeRefNamespace = cmds.ls(c, showNamespace=True)[1]
            elif not cmds.objectType(c, isType="locator"):
              print "# INFO: deleting \"%s\"" %(c)
              cmds.delete(c)


      # Importing centerJnt cache
      print "# INFO: importing centerJnt cache..."
      if cName == "Random":
        pCacheList = db.query("pointee_cache", object=cObject, type="CenterJnt")
        numCaches = len(pCacheList)
        pCache = pCacheList[randint(0, numCaches-1)]
        cName = pCache.name
      else:
        pCache = db.queryOne("pointee_cache", object=cObject, type="CenterJnt", name=cName)
      cmds.select(pointeeRef)
      importCache = importCacheTool.invoke(object=cObject, type="CenterJnt", cache=pCache, importMode="Merge")
      importCacheNodes = importCache["cacheNode"].split()
      abcNode = cmds.rename(importCacheNodes[0], loc + "_AlembicNode")
      cmds.setAttr(abcNode + ".cycleType", 1) # 1 = loop
      cmds.setAttr(abcNode + ".offset", randOffset)

      # Importing Pointee rsProxy
      print "# INFO: importing Pointee rsProxy..."
      cmds.select(clear=True)
      createProxy = mel.eval("redshiftCreateProxy();")
      pxyNode = createProxy[0]
      pxyShape = createProxy[1]
      pxyPlaceholder = createProxy[2]
      cmds.setAttr(pxyNode + ".useFrameExtension", 1)
      cmds.setAttr(pxyNode + ".fileName", "E:/PROJECTS/PAY_Payback_App/Cache/rsProxy/Pointee_rsProxy_%s_####.rs" %(cName), type="string")
      abcRangeEnd = cmds.getAttr(abcNode + ".endFrame")
      cmds.expression(string="%s.frameExtension=((frame+%s-1)%%%s)+1" %(pxyNode, abs(randOffset), abcRangeEnd))
      cmds.parent( pxyPlaceholder, loc, relative=True)


      if self.args.getValue("genericassets"):
        # Import generic assets
        print "# INFO: importing generic assets..."
        if "baby" in cName.lower():
          pass
        elif "girl" in cName.lower():
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
          gAssetList = db.query("pointee_asset", type="Girl")
          numGAssets = len(gAssetList)
          tAssetList = db.query("pointee_asset", type="Top")
          numTAssets = len(tAssetList)
          eAssetList = db.query("pointee_asset", type="Eyes")
          numEAssets = len(eAssetList)
          mAssetList = db.query("pointee_asset", type="Mouth")
          numMAssets = len(mAssetList)
          percentGirl = 5
          percentTop = 60
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

