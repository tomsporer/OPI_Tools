# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import json
import os

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class ExportToAfterEffectsTool(Tool):

  ToolName = 'ExportToAfterEffectsTool'
  ToolLabel = 'Export selection to After Effects...'
  ToolCommand = 'exporttoaftereffectstool'
  ToolDescription = 'Export selected Cameras and locator to After Effects'
  ToolTooltip = 'Export selected Cameras and locator to After Effects'

  def __init__(self, host):
    super (ExportToAfterEffectsTool, self).__init__(host)
    self._noUI = False

  def initialize(self, **args):
    self.args.addStaticText("\tExport selection to After Effects \t \t")
    self.args.addSpacer(13)

    self.args.beginRow("Frame Range")
    self.args.add(name="animStart", label="Start", type="int", value=1)
    self.args.add(name="animEnd", label="End", type="int", value=10)
    self.args.add(name="fps", label="Fps", type="float", value=25)
    self.args.endRow()
    self.args.addSpacer(5)
    self.args.add(name="camsAnimated", label="Camera(s) animated", type="bool", value=True)
    self.args.add(name="locsAnimated", label="Locator(s) animated", type="bool", value=True)
    self.args.addSpacer(5)
    self.args.beginRow("Resolution")
    self.args.add(name="fromRenderSettings", label="From Render Settings", type="bool", value=True)
    self.args.endRow()
    self.args.beginRow("")
    self.args.add(name="resolutionX", label="", type="int", value=1920, enabled=False)
    self.args.add(name="resolutionY", label="", type="int", value=1080, enabled=False)
    self.args.endRow()
    self.args.addSpacer(10)
    self.args.add(name="output", label="Output", type="file", mustexist=False, filefilter="*.json")


  def preexecute(self, **args):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    rangeIn = cmds.getAttr("defaultRenderGlobals.startFrame")
    rangeOut = cmds.getAttr("defaultRenderGlobals.endFrame")
    self.args.setValue("animStart", rangeIn)
    self.args.setValue("animEnd", rangeOut)

    resX = cmds.getAttr("defaultResolution.width")
    resY = cmds.getAttr("defaultResolution.height")
    self.args.setValue("resolutionX", resX)
    self.args.setValue("resolutionY", resY)

    sceneName = os.path.split(cmds.file(q = True, sceneName = True))[1].split(".")[0]
    workspace = cmds.workspace( q=True, sn=True )
    output = os.path.join(workspace, "Cache", sceneName + ".json")

    i = 1
    while os.path.exists(output):
      output = os.path.join(workspace, "Cache", sceneName + str(i) + ".json")
      i += 1

    self.args.setValue("output", output)

  def onValueChanged(self, arg):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    if arg.name == "fromRenderSettings":
      self.args.get("resolutionX").enabled = not arg.value
      self.args.get("resolutionY").enabled = not arg.value
      if arg.value == True:
        resX = cmds.getAttr("defaultResolution.width")
        resY = cmds.getAttr("defaultResolution.height")
        self.args.setValue("resolutionX", resX)
        self.args.setValue("resolutionY", resY)



  def executeMaya(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds
    mel = maya.mel


    animStart = self.args.getValue("animStart")
    animEnd = self.args.getValue("animEnd")
    fps = self.args.getValue("fps")
    frameOffset = 0 - animStart
    # ^ the Maya Importer for After Effects fails to correctly set the start frame of the Comp
    # Therefore we will simply always start writing keyframes at frame 0
    camsAnimated = self.args.getValue("camsAnimated")
    locsAnimated = self.args.getValue("locsAnimated")
    resolutionX = self.args.getValue("resolutionX")
    resolutionY = self.args.getValue("resolutionY")
    output = self.args.getValue("output")


    def getPosition(obj):
      return cmds.xform(obj, q=True, translation=True, worldSpace=True)

    def getScale(obj):
      return cmds.xform(obj, q=True, scale=True, worldSpace=True)

    def getOrientation(obj):
      roo = cmds.xform(obj, q=True, rotateOrder=True)
      ra = cmds.xform(obj, q=True, rotateAxis=True)
      cmds.xform(tempLoc, roo=roo, ra=ra)
      cmds.matchTransform(tempLoc, obj)
      cmds.xform(tempLoc, preserve=True, roo="zyx", ra=[0,0,0]) # We need to convert Maya's rotation order to After Effects' rotation order
      rotation = cmds.xform(tempLoc, q=True, rotation=True, worldSpace=True)
      #cmds.xform(obj, preserve=True, roo=roo, ra=ra)
      return rotation

    def getFocalLength(camShape):
      focalLength = cmds.getAttr(cam + ".focalLength")
      return focalLength

    def getHorizontalFilmAperture(camShape):
      horizontalFilmAperture = cmds.getAttr(cam + ".horizontalFilmAperture") * 25.4 #inch to mm
      return horizontalFilmAperture


    MayaToAE = {}


    currentTime = cmds.currentTime(q=True)
    sceneName = os.path.split(cmds.file(q = True, sceneName = True))[1]

    MayaToAE["projectName"] = sceneName
    MayaToAE["animationLength"] = animEnd - animStart + 1
    MayaToAE["animationStart"] = animStart
    MayaToAE["frameRate"] = fps
    MayaToAE["resolution"] = [resolutionX, resolutionY]
    MayaToAE["lights"] = {}
    MayaToAE["solids"] = {}

    nullsToAE = MayaToAE["nulls"] = {}
    camsToAE = MayaToAE["cameras"] = {}

    sel = cmds.ls(selection=True)
    tempLoc = cmds.spaceLocator()
    tempLoc = cmds.rename(tempLoc, "tempAEexportLoc")
    nullsToExport = []
    camsToExport = []

    for obj in sel:

      objType = cmds.objectType(obj)
      if objType != "transform":
        continue

      shape = cmds.listRelatives(obj, shapes=True, path=True)
      if shape:
        shapeType = cmds.objectType(shape[0])

        if shapeType == "locator":
          nullsToExport.append(obj)

        elif shapeType == "camera":
          camsToExport.append(obj)

    if locsAnimated or camsAnimated:
      cmds.currentTime(animStart)


    for null in nullsToExport:
      nullData = {}
      nullData["position"] = getPosition(null)
      nullData["rotation"] = getOrientation(null)
      nullData["scale"] = getScale(null)
      if locsAnimated:
        nullData["animation"] = {}
      nullsToAE[null] = nullData

    for cam in camsToExport:
      camShape = cmds.listRelatives(cam, shapes=True, path=True)[0]
      camData = {}
      camData["position"] = getPosition(cam)
      camData["rotation"] = getOrientation(cam)
      camData["scale"] = getScale(cam)
      camData["focalLength"] = getFocalLength(camShape)
      camData["horizontalFilmPlane"] = getHorizontalFilmAperture(camShape)
      if camsAnimated:
        camData["animation"] = {}
      camsToAE[cam] = camData


    if locsAnimated or camsAnimated:
      for frame in range(animStart, animEnd + 1):

        if locsAnimated:
          for null in nullsToExport:

            nullAnim = nullsToAE[null]["animation"]
            nullAnim[str(frame + frameOffset)] = {
              "position": getPosition(null),
              "rotation": getOrientation(null),
              "scale": getScale(null)
            }

        if camsAnimated:
          for cam in camsToExport:

            camShape = cmds.listRelatives(cam, shapes=True, path=True)[0]
            camAnim = camsToAE[cam]["animation"]
            camAnim[str(frame + frameOffset)] = {
              "position": getPosition(cam),
              "rotation": getOrientation(cam),
              "focalLength": getFocalLength(camShape),
              "horizontalFilmPlane": getHorizontalFilmAperture(camShape)
            }


        mel.eval("playButtonStepForward;")



    with open(output, "w") as o:
      json.dump(MayaToAE, o, indent = 4)


    print "# INFO: successfully exported json file to " + str(output)

    cmds.delete(tempLoc)
    cmds.currentTime(currentTime)