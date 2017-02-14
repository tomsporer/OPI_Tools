import os
import sys
import maya
import maya.cmds
import maya.OpenMaya
import maya.OpenMayaMPx


def initializePlugin(mobject):
  mplugin = maya.OpenMayaMPx.MFnPlugin(mobject)

  # try:
  #   gOnSceneNewCallbackId = maya.OpenMaya.MSceneMessage.addCallback(maya.OpenMaya.MSceneMessage.kBeforeNew, onSceneDefaults);
  # except Exception as e:
  #   sys.stderr.write('Failed to register kBeforeNew callback.')
  #   raise

  # try:
  #   gOnSceneLoadCallbackId = maya.OpenMaya.MSceneMessage.addCallback(maya.OpenMaya.MSceneMessage.kAfterOpen, onSceneDefaults);
  # except Exception as e:
  #   sys.stderr.write('Failed to register kAfterOpen callback.')
  #   raise

def uninitializePlugin(mobject):
  mplugin = maya.OpenMayaMPx.MFnPlugin(mobject)

  # try:
  #   maya.OpenMaya.MSceneMessage.removeCallback(gOnSceneNewCallbackId)
  # except:
  #   sys.stderr.write('Failed to remove kBeforeNew callback.')
  #   raise

  # try:
  #   maya.OpenMaya.MSceneMessage.removeCallback(gOnSceneLoadCallbackId)
  # except:
  #   sys.stderr.write('Failed to remove kAfterOpen callback.')
  #   raise
