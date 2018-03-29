# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Tom Sporer. All rights reserved.
#

import os
import json

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException

class importFrittCacheTool(DataBaseTool):

  ToolName = 'ImportFrittCache'
  ToolLabel = 'Import Fritt Cache...'
  ToolCommand = 'importfrittcache'
  ToolDescription = 'Import Fritt Cache'
  ToolTooltip = 'Import Fritt Cache'

  def __init__(self, host):
    super (importFrittCacheTool, self).__init__(host)
    self._noUI = False


  def initialize(self, **args):

    db = self.host.apis['db']
    self.__dbRoot = db.root
    self.__project = db.queryOne("project", name="Fritt_TV")
    self.__projectPath = db.getPath(self.__project.location)
    self.__frittRoot = self.__projectPath


    self.__flavsOne = ["Strawberry"]
    self.__flavsTwo = ["Barkeeper", "Cherry", "Lemon", "Orange", "Raspberry"]
    self.__flavsThree = ["Wildberry"]
    self.__flavsMinis = ["MiniGranat", "MiniLitschi", "MiniMango"]

    flavsList = ["- Please select -"] + sorted(self.__flavsOne + self.__flavsTwo + self.__flavsThree + self.__flavsMinis)

    self.args.addStaticText("\tImport Cache \t \t \t")
    self.args.addSpacer(13)
    self.args.add(name="charFlav", type="str", label="Character", combo=flavsList, value=flavsList[0])
    self.args.add(name="film", type="str", label="Film", combo=[], value=None, enabled=True)
    self.args.add(name="shot", type="str", label="Shot", combo=[], value=None, enabled=True)
    self.args.add(name="name", type="str", label="Cache", combo=[], value=None, enabled=True)


  def preexecute(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    # --------------------
    # Get film from scene path
    # --------------------
    frittFilms = ["- Please select -"] #, "Frittmania", "Wettkauen" , "Lecker", "SuperStattSuess", "StripeClub"
    opiProjects = os.getenv("OPI_DATABASE_SUBFOLDERS").split(";")
    for opiProject in opiProjects:
      if opiProject.startswith("FRI_Fritt"):
        frittFilms += [opiProject.replace("FRI_Fritt_", "")]
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
    dbRoot = self.__dbRoot
    # shotlistPath = os.path.join(frittRoot, "3D", "Film_" + film, "shotlist.json")
    shotlistPath = os.path.join(dbRoot, "FRI_Fritt_" + film, "3D", "shotlist.json")

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
    # Get name from selection
    fCacheList = db.query("fritt_export", sql="SELECT * FROM fritt_export WHERE object == \'%s\' AND shot == \'%s\' AND film == \'%s\' ORDER BY name" %("Char", shot, film) )
    nameList = ["- Please select -"]
    fCacheDict = {}
    for fCache in fCacheList:
      nameList += [fCache.name]
      fCacheDict[fCache.name] = fCache
    nameList = sorted(list(set(nameList)))

    self.args.get("name")._setCombo(nameList, "- Please select -")

    self.__fCacheDict = fCacheDict


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
    mel = maya.mel


    def increment(scenePath):
      sceneFolder, sceneFile = os.path.split(scenePath)
      sceneFileName, sceneFileExt = os.path.splitext(sceneFile)

      if sceneFileName[-1].isdigit() == True: # check if there is already a version number at the end and increment if true
        i = 1
        while sceneFileName[-i].isdigit() == True:
          lastDigit = i
          i = i + 1
        oldFileVersion = sceneFileName[-lastDigit:]
        newFileVersion = str(int(oldFileVersion) + 1).rjust(len(oldFileVersion), "0")
        constantFileName = str(sceneFileName[:-lastDigit])

      savePath = os.path.join(sceneFolder, constantFileName + newFileVersion)
      return savePath + sceneFileExt


    # --------------------
    # Get alembic file path
    # --------------------
    fCacheDict = self.__fCacheDict
    name = self.args.getValue("name")
    fCache = fCacheDict[name]
    fCachePath = db.getPath(fCache.location)
    abcPath = os.path.splitext(fCachePath)[0] + "_v001.abc"
    if not os.path.exists(abcPath):
      raise OPIException("Oops, there's no cache file that matches your arguments")
    incrPath = increment(abcPath)
    while os.path.exists(incrPath):
      abcPath = incrPath
      incrPath = increment(abcPath)


    # --------------------
    # Get reference file path and import
    # --------------------
    charFlav = self.args.getValue("charFlav")
    if charFlav == "- Please select -":
      raise OPIException("Please select a character from the list")
    elif charFlav in self.__flavsOne:
      charRefDir = os.path.join(self.__frittRoot, "3D", "REFERENCE", "ONE")
    elif charFlav in self.__flavsTwo:
      charRefDir = os.path.join(self.__frittRoot, "3D", "REFERENCE", "TWO")
    elif charFlav in self.__flavsThree:
      charRefDir = os.path.join(self.__frittRoot, "3D", "REFERENCE", "THREE")
    elif charFlav in self.__flavsMinis:
      charRefDir = os.path.join(self.__frittRoot, "3D", "REFERENCE", "MINIS")

    charRefName = charFlav + "_Clean"
    charRefPath = charRefName + ".mb"
    charRefPath = os.path.join(charRefDir, charRefPath)

    refNodes = cmds.file(charRefPath, r=True, type="mayaBinary", mergeNamespacesOnClash=False, namespace=charRefName, returnNewNodes=True)
    refShapes = []
    for refNode in refNodes:
      if cmds.objectType(refNode) == "transform":
        refShapes += [refNode]


    # --------------------
    # Import abc cache
    # --------------------
    abcImportString = "AbcImport -mode import -connect \""
    abcImportString += refShapes[0]
    if len(refShapes) > 1:
      for shape in refShapes[1:]:
        abcImportString += " " + str(shape)
    abcImportString += "\""
    abcImportString += " \"%s\"" %(abcPath.replace("\\", "/"))
    cacheNode = mel.eval(abcImportString)
