# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import sys
import re

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException
from opi.storage.jsonobject import JsonObject



class SetRenderOutputTool(DataBaseTool):

  ToolName = 'SetRenderOutput'
  ToolLabel = 'Set Output Paths...'
  ToolCommand = 'setrenderoutput'
  ToolDescription = 'set the paths for the renders'
  ToolTooltip = 'Render Output Settings'

  def __init__(self, host):
    super (SetRenderOutputTool, self).__init__(host)

  def initialize(self, **args):

    self.args.beginRow("Renderer")
    self.args.addStaticText("Redshift")
    self.args.endRow()
    self.args.addSpacer(7)
    self.args.add(name='projectname', label='project', type='str', enabled=False)
    self.args.add(name="renderpath", type="folder", label="render path", value="", enabled=True, expression="[a-zA-Z0-9_/]*")
    self.args.add(name="renderfolder", type="str", label="renderfolder(hidden)", value="", hidden=True)
    self.args.add(name="renderlayerSubfolder", label="Render Layer Subfolder", type="bool", value=False)
    self.args.addSpacer(5,1)
    self.args.add(name="usescenetoken", label="Use <Scene> as Version", type="bool", value=False)
    self.args.beginRow("render name")
    self.args.add(name="rendername", type="str", label="", value="")
    self.args.addButton("takeSceneName", "<<")
    self.args.endRow()
    self.args.beginRow("version")
    self.args.add(name="version", label="", type="str", expression='[0-9]+[0-9]*')
    self.args.addButton("plusOne", "+1")
    self.args.endRow()
    self.args.addSpacer(5,1)
    self.args.beginRow("Camera subfolder")
    self.args.add(name="camsubfolderBefore", label="Before version", type="bool", value=False)
    self.args.add(name="camsubfolderAfter", label="After version", type="bool", value=False)
    self.args.endRow()
    self.args.addSpacer(5,1)
    self.args.beginRow("camera")
    self.args.add(name="changeCamera", label="", type="bool", value=False)
    self.args.add(name="camera", label="", type="str", combo=[], enabled=False)
    self.args.endRow()
    self.args.beginRow('range')
    self.args.add(name="changeRange", label="", type="bool", value=False)
    self.args.add(name="in", type="int", enabled=False)
    self.args.add(name="out", type="int", enabled=False)
    self.args.endRow()
    self.args.beginRow("padding")
    self.args.add(name="changePadding", label="", type="bool", value=False)
    self.args.add(name="padding", label="", type="int", range=[1, 5], enabled=False)
    self.args.endRow()
    self.args.add(name="skipExisting", label="skip existing", type="bool", value=False)
    self.args.beginRow("resolution")
    self.args.add(name="changeResolution", label="", type="bool", value=False)
    self.args.add(name="resX", label="X", type="int", enabled=False)
    self.args.add(name="resY", label="Y", type="int", enabled=False)
    self.args.endRow()


  def onButtonPressed(self, button):

    if button == "plusOne":
      usescenetoken = self.args.getValue("usescenetoken")
      if usescenetoken == False:
        version = self.args.getValue("version")
        versionPlus = str(int(version) + 1).rjust(2,"0")
        self.args.setValue("version", versionPlus)
    elif button == "takeSceneName":
      usescenetoken = self.args.getValue("usescenetoken")
      if usescenetoken == False:
        self.args.setValue("rendername", self.__scenename)


  def onValueChanged(self, arg):


    if arg.name == "camsubfolderBefore" and arg.value == True:
      self.args.setValue("camsubfolderAfter", False)
    elif arg.name == "camsubfolderAfter" and arg.value == True:
      self.args.setValue("camsubfolderBefore", False)
    elif arg.name == "changeRange":
      self.args.get("in").enabled = arg.value
      self.args.get("out").enabled = arg.value
    elif arg.name == "in":
      if arg.value > self.args.getValue("out"):
        self.args.setValue("out", arg.value)
    elif arg.name == "out":
      if arg.value < self.args.getValue("in"):
        self.args.setValue("in", arg.value)
    elif arg.name == "changeResolution":
      self.args.get("resX").enabled = arg.value
      self.args.get("resY").enabled = arg.value
    elif arg.name == "changeCamera":
      self.args.get("camera").enabled = arg.value
    elif arg.name == "changePadding":
      self.args.get("padding").enabled = arg.value
    elif arg.name == "renderpath":
      if arg.value != self.__prevRenderpath:
        renderpath = arg.value.replace("/", "\\")
        renderfolder = renderpath.split("Render\\")[-1]
        if renderpath == renderfolder:
          renderfolder = ""
        self.args.setValue("renderfolder", renderfolder)
        # self.__readJson()
        self.__prevRenderpath = arg.value
    elif arg.name == "usescenetoken":
      self.args.get("rendername").enabled = not arg.value
      self.args.get("version").enabled = not arg.value

  def preexecute(self, **args):

    db = self.host.apis['db']
    maya = self.host.apis['maya']
    cmds = maya.cmds
    mel = maya.mel

    # ----
    # get current scene data and set default values
    # ----
    self.__filepath = cmds.file(q=True, sn=True)
    self.__filename = os.path.split(self.__filepath)[1]
    self.__scenename = self.__filename.rsplit(".", 1)[0]
    rangeIn = cmds.getAttr("defaultRenderGlobals.startFrame")
    rangeOut = cmds.getAttr("defaultRenderGlobals.endFrame")
    self.args.setValue("in", rangeIn)
    self.args.setValue("out", rangeOut)
    padding = cmds.getAttr("defaultRenderGlobals.extensionPadding")
    if 1 <= padding <= 5:
      self.args.setValue("padding", padding)
    else:
      self.args.setValue("padding", 5)
      self.args.setValue("changePadding", True)
      self.args.get("padding").enabled = True
    resolutionX = cmds.getAttr("defaultResolution.width")
    resolutionY = cmds.getAttr("defaultResolution.height")
    self.args.setValue("resX", resolutionX)
    self.args.setValue("resY", resolutionY)
    renderEngine = cmds.getAttr('defaultRenderGlobals.ren')
    self.__versionFromPrefix = "01"
    # ----


    # check current render engine
    if renderEngine == "redshift":
      self.__isRedshift = True
      if not cmds.window("unifiedRenderGlobalsWindow", exists=True) or not cmds.objExists("redshiftOptions"):
        mel.eval('unifiedRenderGlobalsWindow;')
        mel.eval('fillSelectedTabForCurrentRenderer;')
        cmds.evalDeferred("pass")
        # cmds.workspaceControl("unifiedRenderGlobalsWindow", e=True, visible=False)
        cmds.layout("unifiedRenderGlobalsWindow", e=True, visible=False)
      skipExisting = cmds.getAttr("redshiftOptions.skipExistingFrames")
      self.args.setValue("skipExisting", skipExisting)
    else:
      self.__isRedshift = False


    # # check the project name
    # # if it is not specified, set it based on the project
    # try:
    #   project = db.queryFromPath('Project', self.__filepath)
    #   if not project:
    #     raise OPIException('The scene is not in a valid project!')
    # except:
    #   raise OPIException('The current scene is not part of a project.')
    # projectname = project.name

    project = cmds.workspace( q=True, sn=True )
    projectname = os.path.split(project)[1]
    self.args.setValue('projectname', projectname)


    # ----
    # check and read saved renderOutputInfo
    # ----

    def checkVersionFolder(path):
      pathHead, pathTail = os.path.split(path)
      if re.match("[vV][0-9]+", pathTail):
        self.__versionFromPrefix = pathTail[1:]
        return True
      elif pathTail.lower() == "<scene>":
        self.args.setValue("usescenetoken", True)
        self.args.get("rendername").enabled = False
        self.args.get("version").enabled = False
        return True
      else:
        return False

    def checkCameraFolder(path):
      pathHead, pathTail = os.path.split(path)
      if pathTail == "<Camera>":
        return True
      else:
        return False

    def checkRenderLayerFolder(path):
      pathHead, pathTail = os.path.split(path)
      if pathTail.lower() == "<renderlayer>":
        return True
      else:
        return False

    def checkSceneFolder(path):
      pathHead, pathTail = os.path.split(path)
      if pathTail.lower() == "<scene>":
        return True
      else:
        return False


    renderPrefix = str(cmds.getAttr("defaultRenderGlobals.imageFilePrefix"))
    renderPrefix = renderPrefix.replace("/", "\\")
    projectPath = cmds.workspace( q=True, rootDirectory=True )

    scenename = self.__scenename
    if scenename:
      while scenename[-1].isdigit() or scenename[-1] == "_":
        scenename = scenename[:-1]
      if scenename[-2:] == "_v" or scenename[-2:] == "_V":
        scenename = scenename[:-2]
    self.__scenename = scenename  

    if len(renderPrefix) == 0 or renderPrefix == "None":
      renderpath = os.path.join(projectPath, "Render")
      renderfolder = ""
      self.__versionFromPrefix = "01" # default
      self.args.setValue("rendername", scenename)
      self.args.setValue("renderlayerSubfolder", True)
      self.args.setValue("usescenetoken", True)
      self.args.setValue("rendername", "<Scene>")
      self.args.get("rendername").enabled = False
      self.args.get("version").enabled = False

    else:
      renderpath, rendername = os.path.split(renderPrefix) # rip off filename

      rendernameparts = rendername.split("_")
      if "<RenderLayer>" in rendernameparts:
        rendernameparts.remove("<RenderLayer>")
      for rendernamepart in rendernameparts:
        if re.match("[vV][0-9]+", rendernamepart):
          rendernameparts.remove(rendernamepart)
      rendername = "_".join(rendernameparts)
      if rendername:
        self.args.setValue("rendername", rendername)
      else:
        self.args.setValue("rendername", scenename)

      # check for renderlayer subfolder
      if checkRenderLayerFolder(renderpath):
        renderpath = os.path.split(renderpath)[0]
        self.args.setValue("renderlayerSubfolder", True)

      # check if folder at end is a version or camera folder
      if checkVersionFolder(renderpath):
        renderpath = os.path.split(renderpath)[0]
        if checkCameraFolder(renderpath):
          renderpath = os.path.split(renderpath)[0]
          self.args.setValue("camsubfolderBefore", True)
      elif checkCameraFolder(renderpath):
        renderpath = os.path.split(renderpath)[0]
        self.args.setValue("camsubfolderAfter", True)
        if checkVersionFolder(renderpath):
          renderpath = os.path.split(renderpath)[0]


      if renderPrefix[1] == ":":
        renderfolder = renderpath.split("Render\\")[-1]
        if renderpath == renderfolder:
          renderfolder = ""
      else:
        renderfolder = renderpath
        if len(renderpath) == 0:
          renderpath = os.path.join(projectPath, "Render")
        else:
          renderpath = os.path.join(projectPath, "Render", renderpath)

    self.args.setValue('version', self.__versionFromPrefix)
    self.args.setValue("renderpath", renderpath)
    self.__prevRenderpath = renderpath
    self.args.setValue("renderfolder", renderfolder)

    # self.__readJson()
    # ----


    # ----
    # Get Scene Cameras and fill UI Combo box
    # ----
    cameraList = cmds.ls(cameras=True)
    if "frontShape" in cameraList:
      cameraList.remove("frontShape")
    if "sideShape" in cameraList:
      cameraList.remove("sideShape")
    if "topShape" in cameraList:
      cameraList.remove("topShape")
    if "leftShape" in cameraList:
      cameraList.remove("leftShape")
    if len(cameraList) < 1:
      raise OPIException("No renderable Camera found")

    self.__cameraComboDict = {}
    cameraDict = self.__cameraComboDict
    renderableCams = 0
    for cam in cameraList:
      camName = cam.replace("Shape", "")
      cameraDict[camName] = cam
      if cmds.getAttr(cam + ".renderable") == 1:
        renderableCam = camName
        renderableCams += 1

    sortedCameraKeys = sorted(cameraDict.keys())

    if renderableCams == 1:
      self.args.get("camera")._setCombo(sortedCameraKeys, renderableCam)
    else:
      # self.args.setValue("changeCamera", True)
      # self.args.get("changeCamera").enabled = False
      # self.args.get("camera").enabled = True
      self.args.get("camera")._setCombo(sortedCameraKeys, sortedCameraKeys[0])
    # ----


  def __getJsonPath(self):
    
    # get from renderpath:
    renderpath = self.args.getValue("renderpath")
    jsonPath = os.path.join(renderpath, "renderOutputInfo.json")

    return jsonPath


  def __readJson(self):
    filename = self.__filename
    scenename = self.__scenename
    defaultVersion = self.__versionFromPrefix
    jsonPath = self.__getJsonPath()
    readJson = JsonObject(jsonPath)
    version = readJson.get("version", defaultVersion)
    rendername = readJson.get("rendername", scenename)
    # self.args.setValue('version', version)
    # self.args.setValue("rendername", rendername)

  def execute(self):
    print "heeeeellooooooo"

  def executeMaya (self):

    maya = self.host.apis['maya']
    cmds = maya.cmds
    mel = maya.mel

    # ----
    # Get data from UI
    # ----
    projectname = self.args.getValue('projectname')
    renderpath = self.args.getValue('renderpath')
    renderfolder = self.args.getValue('renderfolder')
    usescenetoken = self.args.getValue('usescenetoken')
    rendername = self.args.getValue('rendername')
    version = self.args.getValue('version')
    version = version.rjust(2, '0')
    renderlayerSubfolder = self.args.getValue("renderlayerSubfolder")
    # camsubfolder = self.args.getValue("camsubfolder")
    camsubfolderBefore = self.args.getValue("camsubfolderBefore")
    camsubfolderAfter = self.args.getValue("camsubfolderAfter")
    changeCamera = self.args.getValue("changeCamera")
    camera = self.args.getValue("camera")
    changeRange = self.args.getValue("changeRange")
    startFrame = self.args.getValue('in')
    endFrame = self.args.getValue('out')
    changePadding = self.args.getValue("changePadding")
    padding = self.args.getValue('padding')
    changeResolution = self.args.getValue("changeResolution")
    resX = self.args.getValue("resX")
    resY = self.args.getValue("resY")
    skipExisting = self.args.getValue("skipExisting")
    # ----



    # ----
    # Set Render Output Settings
    # ----
    if not self.__isRedshift:
      cmds.setAttr('defaultRenderGlobals.ren', 'redshift', type='string')

    if usescenetoken:
      renderfile = "<Scene>_<RenderLayer>"
    else:
      renderfile = rendername + "_<RenderLayer>_V" + str(version)
    if camsubfolderBefore:
      renderpath = os.path.join(renderpath, "<Camera>")
    if usescenetoken:
      renderpath = os.path.join(renderpath, "<Scene>")
    else:
      renderpath = os.path.join(renderpath, "V" + version)
    if camsubfolderAfter:
      renderpath = os.path.join(renderpath, "<Camera>")
    if renderlayerSubfolder:
      renderpath = os.path.join(renderpath, "<RenderLayer>")
    renderPrefix = os.path.join(renderpath, renderfile)

    cmds.setAttr("defaultRenderGlobals.imageFilePrefix", renderPrefix, type="string")
    cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)
    cmds.setAttr("redshiftOptions.imageFormat", 1) # 1 = exr
    cmds.setAttr("defaultRenderGlobals.animation", True)
    cmds.setAttr("defaultRenderGlobals.useMayaFileName", False)
    cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", True)
    cmds.setAttr("defaultRenderGlobals.periodInExt", True)
    cmds.setAttr("redshiftOptions.skipExistingFrames", skipExisting)

    if changeRange:
      cmds.setAttr("defaultRenderGlobals.startFrame", int(startFrame))
      cmds.setAttr("defaultRenderGlobals.endFrame", int(endFrame))

    if changePadding:
      cmds.setAttr("defaultRenderGlobals.extensionPadding", int(padding))

    if changeResolution:
      lockAspect = cmds.getAttr("defaultResolution.aspectLock")
      cmds.setAttr("defaultResolution.aspectLock", False)
      cmds.setAttr("defaultResolution.width", int(resX))
      cmds.setAttr("defaultResolution.height", int(resY))
      if not mel.eval('exists checkAspectLockHeight2;'):
        # We need a few commands that help with keeping the pixel aspect ratio at 1 and only adjusting the device aspect ratio (maya default is the other way around)
        # Those commands do not exist until they are forced to load. Loading the defaultResolution node into the Attribute Editor can do that.
        mel.eval('updateAE "defaultResolution"')
        # Loading the defaultResolution node into the Attribute Editor takes some time. We need it to finish before continuing. 
        # The command 'evalDeferred' does exactly this. It waits until all previous processes are done, then continues executing the next lines
        cmds.evalDeferred("pass") 
      mel.eval('checkAspectLockHeight2 "defaultResolution"')
      mel.eval('checkAspectLockWidth2 "defaultResolution"')
      mel.eval('redshiftUpdatePixelAspectRatio')
      mel.eval('redshiftUpdateResolution')
      cmds.setAttr("defaultResolution.aspectLock", lockAspect)
      cmds.evalDeferred("cmds.setAttr(\"defaultResolution.pixelAspect\", 1)")

    # if delRenderGlobalsWindow:
    #   cmds.deleteUI("unifiedRenderGlobalsWindow")


    # Set renderable Camera
    if changeCamera:
      cmds.setAttr("frontShape.renderable", 0)
      cmds.setAttr("sideShape.renderable", 0)
      cmds.setAttr("topShape.renderable", 0)

      cameraDict = self.__cameraComboDict
      cameraShape = cameraDict[camera]
      for cam in cameraDict.keys():
        shape = cameraDict[cam]
        if shape != cameraShape:
          cmds.setAttr(shape + ".renderable", 0)
        else:
          cmds.setAttr(shape + ".renderable", 1)
    # ----


    # # save render output info to json
    # jsonPath = self.__getJsonPath()
    # saveJson = JsonObject(jsonPath)
    # saveJson.version = version
    # saveJson.rendername = rendername
    # saveJson.write()





