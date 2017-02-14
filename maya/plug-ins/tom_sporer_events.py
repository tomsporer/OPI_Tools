import os
import sys
import maya
import maya.cmds
import maya.OpenMaya
import maya.OpenMayaMPx

import pymel
import pymel.core

def onSceneDefaults(userdata):

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
    folder = os.path.split(folder)[0]

def onSceneLoad(userdata):
  onSceneDefaults(userdata)
  setProjectPath()

def onSceneSave(userdata):
  setProjectPath()

def initializePlugin(mobject):
  mplugin = maya.OpenMayaMPx.MFnPlugin(mobject)

  try:
    globals()['ts_gOnSceneNewCallbackId'] = maya.OpenMaya.MSceneMessage.addCallback(maya.OpenMaya.MSceneMessage.kAfterNew, onSceneDefaults);
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
