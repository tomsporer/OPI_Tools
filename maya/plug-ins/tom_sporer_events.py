import os
import sys
import maya
import maya.cmds as cmds
import maya.OpenMaya
import maya.OpenMayaMPx

import pymel
import pymel.core

def onNewScene(userdata):

  # set units
  maya.cmds.currentUnit(linear='cm', angle='deg', time='pal')
  print '\n---------------------------------\nTom Sporer defaults set\n---------------------------------'

def setProjectPath():
  # set the project path
  filePath = maya.cmds.file(q=True, sn=True)
  folder = os.path.split(filePath)[0]
  while folder:
    workspace = os.path.join(folder, 'workspace.mel')
    if os.path.exists(workspace):
      pymel.core.mel.eval('setProject "%s"' % folder.replace("\\", '/'))
      break
    if folder == os.path.split(folder)[0]:
      break
    folder = os.path.split(folder)[0]

def checkForRenderSetupMismatch():
  # Check Preferred Render Setup System in Maya Preferences
  prefRenderSetup = cmds.optionVar(q="renderSetupEnable")
  # 1 = New Render Setup
  # 0 = Legacy Render Layers

  # Check Render Setup System in current Scene
  renderLayers = cmds.ls( type="renderLayer" )
  # renderLayers.remove("defaultRenderLayer")

  # ignore default render layers
  for rl in cmds.ls(type="renderLayer"):
    if "defaultRenderLayer" in rl:
        renderLayers.remove(rl)

  try:
    renderSetupLayers = cmds.ls( type="renderSetupLayer" )
  except:
    renderSetupLayers = []

  cleanUp = False
  if prefRenderSetup == 1:
    if len(renderLayers) > len(renderSetupLayers):
      if renderSetupWarning(1) == "Clean up":
        dialogMsg = "Delete the following legacy render layer(s)?\n"
        for renderSetupLayer in renderSetupLayers:
          renderLayers.remove("rs_" + renderSetupLayer)
        for renderLayer in renderLayers:
          dialogMsg += "\n" + renderLayer
        cleanUp = True
  else:
    if len(renderSetupLayers) > 0:
      renderSetupWarning(0)
      # Todo: Implement clean up dialog to delete obsolete render setup layers.
      #       Note: Currently (in Maya 2017 Update 3) deleting render setup layers 
      #       while being in render setup mode and having the render layer editor open
      #       crashes the editor window.
      
  if cleanUp:
    dialog = cmds.confirmDialog(title="Delete Layers", message=dialogMsg, button=["Delete", "Cancel"], cancelButton="Cancel", dismissString="Cancel", icon="question")
    if dialog == "Delete":
      for renderLayer in renderLayers:
        cmds.delete(renderLayer)


def renderSetupWarning(prefRenderSetup):
  if prefRenderSetup == 1:
    dialogMsg = "Warning: This file contains legacy render layers and Maya is currently in Render Setup mode."
    dialog = cmds.confirmDialog(title="Render Setup Mismatch", message=dialogMsg, button=["Clean up", "Ok"], cancelButton="Ok", dismissString="Ok", icon="warning")
  else:
    dialogMsg = "Warning: This file contains render setup nodes and Maya is currently in Legacy Render Layers mode."
    dialog = cmds.confirmDialog(title="Render Setup Mismatch", message=dialogMsg, button="Ok", cancelButton="Ok", dismissString="Ok", icon="warning")
  return dialog

def onSceneLoad(userdata):
  # onNewScene(userdata)
  maya.cmds.currentUnit(linear='cm', angle='deg')
  setProjectPath()
  checkForRenderSetupMismatch()

def onSceneSave(userdata):
  setProjectPath()

def beforeSceneSave(userdata):
  prefRenderSetup = cmds.optionVar(q="renderSetupEnable")
  # 1 = New Render Setup
  # 0 = Legacy Render Layers
  if prefRenderSetup == 1:
    try:
      cmds.editRenderLayerGlobals( currentRenderLayer="defaultRenderLayer" )
      print "# INFO: set 'defaultRenderLayer' as current render layer before saving the scene"
    except:
      print "# WARNING: FAILED to set 'defaultRenderLayer' as current render layer before saving the scene!"
  
def initializePlugin(mobject):
  mplugin = maya.OpenMayaMPx.MFnPlugin(mobject)

  try:
    globals()['ts_gOnSceneNewCallbackId'] = maya.OpenMaya.MSceneMessage.addCallback(maya.OpenMaya.MSceneMessage.kAfterNew, onNewScene);
  except Exception as e:
    sys.stderr.write('Failed to register kAfterNew callback.')
    raise

  try:
    globals()['ts_gOnSceneLoadCallbackId'] = maya.OpenMaya.MSceneMessage.addCallback(maya.OpenMaya.MSceneMessage.kAfterOpen, onSceneLoad);
  except Exception as e:
    sys.stderr.write('Failed to register kAfterOpen callback.')
    raise

  try:
    globals()['ts_gOnSceneSaveCallbackId'] = maya.OpenMaya.MSceneMessage.addCallback(maya.OpenMaya.MSceneMessage.kAfterSave, onSceneSave);
  except Exception as e:
    sys.stderr.write('Failed to register kAfterSave callback.')
    raise

  try:
    globals()['ts_gBeforeSceneSaveCallbackId'] = maya.OpenMaya.MSceneMessage.addCallback(maya.OpenMaya.MSceneMessage.kBeforeSave, beforeSceneSave);
  except Exception as e:
    sys.stderr.write('Failed to register kBeforeSave callback.')
    raise

def uninitializePlugin(mobject):
  mplugin = maya.OpenMayaMPx.MFnPlugin(mobject)

  try:
    maya.OpenMaya.MSceneMessage.removeCallback(globals()['ts_gOnSceneNewCallbackId'])
  except:
    sys.stderr.write('Failed to remove kAfterNew callback.')
    raise

  try:
    maya.OpenMaya.MSceneMessage.removeCallback(globals()['ts_gOnSceneLoadCallbackId'])
  except:
    sys.stderr.write('Failed to remove kAfterOpen callback.')
    raise

  try:
    maya.OpenMaya.MSceneMessage.removeCallback(globals()['ts_gOnSceneSaveCallbackId'])
  except:
    sys.stderr.write('Failed to remove kAfterSave callback.')
    raise

  try:
    maya.OpenMaya.MSceneMessage.removeCallback(globals()['ts_gBeforeSceneSaveCallbackId'])
  except:
    sys.stderr.write('Failed to remove kBeforeSave callback.')
    raise
