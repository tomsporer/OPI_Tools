# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Tom Sporer. All rights reserved.
#

import os
import sys
import json
import subprocess
import getpass
from datetime import datetime

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException

class exportForCachingTool(DataBaseTool):

  ToolName = 'ExportForCaching'
  ToolLabel = 'Export for Caching...'
  ToolCommand = 'exportforcaching'
  ToolDescription = 'Export for Caching'
  ToolTooltip = 'Export for Caching'

  def __init__(self, host):
    super (exportForCachingTool, self).__init__(host)
    self._noUI = False


  def initialize(self, **args):

    db = self.host.apis['db']
    self.__project = db.queryOne("project", name="Fritt_TV")
    self.__projectPath = db.getPath(self.__project.location)
    self.__frittRoot = self.__projectPath
    self.__newName = False
    self.args.addStaticText("\tExport for Caching \t \t \t")
    self.args.addSpacer(13)
    self.args.add(name="object", type="str", label="Character/Asset", combo=["Char", "Asset"], value="Char")
    self.args.add(name="film", type="str", label="Film", combo=[], value=None, enabled=True)
    self.args.add(name="shot", type="str", label="Shot", combo=[], value=None, enabled=True)
    self.args.beginRow("Name")
    self.args.add(name="name", type="str", label="", combo=[], value=None, enabled=True)
    self.args.addButton("plusName", "+")
    self.args.endRow()
    self.args.add(name="newName", type="str", label="newName", expression="[A-Za-z]+[A-Za-z0-9]*", value=None, enabled=True, hidden=True, optional=True)


  def preexecute(self):
    db = self.host.apis['db']
    maya = self.host.apis['maya']
    cmds = maya.cmds


    # --------------------
    # check selection
    # --------------------
    sel = cmds.ls(selection=True)
    if len(sel) == 0:
      raise OPIException("Nothing selected. Please select a character and retry")
    else:
      sel = sel[0]
      # check for "gChar" group for the character
      if "gChar" not in sel:
        par = cmds.listRelatives(sel, parent=True)
        while par is not None:
          sel = par[0]
          if "gChar" in sel:
            cmds.select(sel)
            break
          par = cmds.listRelatives(sel, parent=True)
        else:
          raise OPIException("Couldn't find the character's top group \"gChar\" in selection")
      # check if selection is a child reference of another reference
      if cmds.referenceQuery(sel, isNodeReferenced=True):
        refNode = cmds.referenceQuery(sel, referenceNode=True)
        refPar = cmds.referenceQuery(refNode, referenceNode=True, parent=True)
        if refPar is not None:
          raise OPIException("The selected object is a child of another reference. The export won't work")
    

    # --------------------
    # Get film from scene path
    # --------------------
    frittFilms = ["- Please select -", "Frittmania", "Lecker", "StripeClub", "SuperStattSuess", "Wettkauen"]
    self.__currentScene = currentScene = cmds.file(q=True, sceneName=True)
    self.__currentSceneFolder = currentSceneFolder = os.path.split(currentScene)[0]
    for frittFilm in frittFilms:
      if frittFilm in currentSceneFolder:
        film = frittFilm
        break
    else:
      film = frittFilms[0]
    
    self.args.get("film")._setCombo(frittFilms, film)


    # --------------------
    # Fill defaults for shot and name list
    # --------------------
    self.fillShotList(film)
    shot = self.args.getValue("shot")
    self.fillNameList(film, shot)


  def fillShotList(self, film):
    # Get shot from scene path
    currentSceneFolder = self.__currentSceneFolder
    frittRoot = self.__frittRoot
    shotlistPath = os.path.join(frittRoot, "3D", "Film_" + film, "shotlist.json")

    frittShots = ["- Please select -"]
    shot = "- Please select -"
    if os.path.exists(shotlistPath):
      with open(shotlistPath, "r") as j:
        shotlist = json.load(j)

      frittShots += sorted(shotlist.keys())
      for frittShot in frittShots:
        if frittShot in currentSceneFolder: 
          shot = frittShot
          break
    elif shot is not "- Please select -":
      print "# WARNING: no shotlist exists for film:" + film
      print "# WARNING: the export will work, but no cache can be written!"

    self.args.get("shot")._setCombo(frittShots, shot)


  def fillNameList(self, film, shot):
    db = self.host.apis['db']
    maya = self.host.apis['maya']
    cmds = maya.cmds
    charOrAss = self.args.getValue("object")
    # Get name from selection
    sel = cmds.ls(selection=True)[0]
    fCacheList = db.query("fritt_export", sql="SELECT * FROM fritt_export WHERE object == \'%s\' AND shot == \'%s\' AND film == \'%s\' ORDER BY name" %(charOrAss, shot, film) )
    nameList = ["- Please select -"]
    for fCache in fCacheList:
      nameList += [fCache.name]
    nameList = sorted(list(set(nameList)))
    # fCacheDict = {}
    # for fCache in fCacheList:
    #   name = fCache.name
    #   versionFound = int(fCache.version)
    #   if fCacheDict.has_key(name):
    #     versionExists = int(fCacheDict[name].version)
    #     if versionFound > versionExists:
    #       fCacheDict[name] = fCache
    #   else:
    #     fCacheDict[name] = fCache
    # if fCacheList:
    #   fCacheKeys = ["- Please select -"]
    #   fCacheKeys += sorted(fCacheDict.keys())
    #   for key in fCacheKeys:
    #     if key in sel:
    #       defaultValue = key
    #   else:
    #     defaultValue = fCacheKeys[0]
    #   self.args.get("name")._setCombo(fCacheKeys, defaultValue)
    # else:
    #   self.args.get("name")._setCombo(["- Please select -"], "- Please select -")
    self.args.get("name")._setCombo(nameList, "- Please select -")


  def onButtonPressed(self, button):
    if button == "plusName":
      self.args.get("newName").hidden = False
      self.args.get("name").enabled = False
      self.__newName = True


  def onValueChanged(self, arg):
    maya = self.host.apis['maya']
    db = self.host.apis['db']

    if arg.name == "film":
      film = arg.value
      self.fillShotList(film)
      shot = self.args.getValue("shot")
      self.fillNameList(film, shot)
    elif arg.name == "shot":
      shot = arg.value
      film = self.args.getValue("film")
      self.fillNameList(film, shot)
    elif arg.name == "object":
      film = self.args.getValue("film")


  def executeMaya(self):
    maya = self.host.apis['maya']
    db = self.host.apis['db']
    cmds = maya.cmds


    # --------------------
    # collect values and variables
    # --------------------
    frittRoot = self.__frittRoot
    charOrAss = self.args.getValue("object")
    if charOrAss == "Character":
      charOrAss = "Char"
    if self.__newName:
      exportName = self.args.getValue("newName")
    else:
      exportName = self.args.getValue("name")
    shot = self.args.getValue("shot")
    film = self.args.getValue("film")
    localAppData = os.getenv("LOCALAPPDATA")

    if exportName == "- Please select -":
      raise OPIException("Please give your export a name")
    if film == "- Please select -":
      raise OPIException("Please select a film from the list")
    if shot == "- Please select -":
      raise OPIException("Please select a shot from the list")


    # --------------------
    # export selection
    # --------------------

    exportDir = os.path.join(frittRoot, "3D", "Film_" + film, shot, "Cache", exportName)
    exportFileName = "_".join([charOrAss, shot, exportName, film])
    exportPath = os.path.join(exportDir, exportFileName + ".mb")
    force = not self.__newName
    exportFile = cmds.file(exportPath, force=force, exportSelected=True, constraints=True, constructionHistory=True, expressions=True, channels=True, shader=True, preserveReferences=True, type="mayaBinary")
    db.getOrCreateNew("fritt_export", object=charOrAss, shot=shot, name=exportName, film=film, fileext="mb", createEmptyFile=False)

    print "# INFO: exported   \"%s\"" %(exportFile)


    # --------------------
    # write log file
    # --------------------
    logFile = os.path.join(exportDir, exportFileName + ".log")
    wTime = datetime.now().strftime("[%Y-%m-%d %H:%M]")
    wScene = cmds.file(q=True, sceneName=True, shortName=True)
    wUser = getpass.getuser()
    if os.path.exists(logFile):
      wBeginning = "\n"
    else:
      wBeginning = "Log\n"
    wLine = "%s%s   \"exported Character\"   %s   %s" %(wBeginning, wTime, wScene, wUser)
    with open(logFile, "a") as t:
      t.write(wLine)


    # --------------------
    # write Deadline Info File
    # --------------------
    sceneName = cmds.file(q=True, sceneName=True, shortName=True).rsplit(".")[0]
    wContent = "Plugin=MayaBatch\n\
Comment=\n\
Priority=90\n\
Department=FRI_Fritt_TV\n\
Frames=1\n\
Name=" + sceneName + " [Script Job]"

    wPath = os.path.join(localAppData, "Thinkbox", "Deadline10", "temp", "maya_deadline_info.job")
    with open(wPath, "w") as infoFile:
      infoFile.write(wContent)

    dlInfoFile = wPath


    # --------------------
    # write Deadline Plugin File
    # --------------------
    wContent = "ScriptJob=True\n\
Version=2017\n\
Build=64bit\n\
ProjectPath=E:/PROJECTS/FRI_Fritt_TV\n\
ScriptFilename=autoExportCache.py\n\
SceneFile=%s" %(os.path.normpath(exportFile).replace("\\", "/"))

    wPath = os.path.join(localAppData, "Thinkbox", "Deadline10", "temp", "maya_deadline_job.job")
    with open(wPath, "w") as pluginFile:
      pluginFile.write(wContent)

    dlPluginFile = wPath


    # --------------------
    # write Maya Deadline Submission File
    # --------------------
    exportCachePy = "E:/PROJECTS/FRI_Fritt_TV/Scripts/autoExportCache.py"
    wContent = dlInfoFile + "\n" + dlPluginFile
    wContent += "\n" + str(exportCachePy)

    wPath = os.path.join(localAppData, "Thinkbox", "Deadline10", "temp", "maya_submission.txt")
    with open(wPath, "w") as dlPluginFile:
      dlPluginFile.write(wContent)

    dlSubmissionFile = wPath


    # --------------------
    # submit to deadline
    # --------------------
    dlcExe = "C:/Program Files/Thinkbox/Deadline10/bin/deadlinecommand.exe"
    dlcArgs = dlSubmissionFile
    o = subprocess.Popen([dlcExe, dlcArgs], stdout = subprocess.PIPE)
    print o.communicate()[0]





















