import os
import sys
import maya
import maya.cmds
import maya.OpenMaya
import maya.OpenMayaMPx
import pymel
import pymel.core

class TSRenderCommand(maya.OpenMayaMPx.MPxCommand):

  def __init__(self):
    maya.OpenMayaMPx.MPxCommand.__init__(self)

  def isUndoable(self):
    return False

  def doIt(self, argList):
    args = self.parseArgs(argList)
    if args['scene']:
      maya.cmds.file(args['scene'], f=True, o=True)

    maya.cmds.setAttr("defaultRenderGlobals.animation", True)
    maya.cmds.setAttr("defaultRenderGlobals.startFrame", args['inframe'])
    maya.cmds.setAttr("defaultRenderGlobals.endFrame", args['outframe'])

    rs = maya.app.renderSetup.model.renderSetup.instance()
    layers = [rs.getDefaultRenderLayer()] + rs.getRenderLayers()
    for layer in layers:
      if layer.name() == args['layer']:
        layer.setRenderable(True)
      else:
        layer.setRenderable(False)

    pymel.core.mel.eval('BatchRender')

    # look for more work
    if os.environ.has_key('OPI_WORKER_ADDRESS'):
      with OPISocket(os.environ['OPI_WORKER_ADDRESS']) as socket:
        data = socket.communicate({'method': 'getAnotherTaskForProcess'})
        if data:
          inframe = data['args']['inframe']
          outframe = data['args']['outframe']
          layer = data['args']['layer']
          camera = data['args']['camera']
          maya.cmds.ts_render(scene='', inframe=inframe, outframe=outframe, layer=layer, camera=camera)

    return True

  def parseArgs(self, args):
    argData = maya.OpenMaya.MArgDatabase(self.syntax(), args)
    result = {}
    if not argData.isFlagSet( 's' ):
      raise Exception('s / scene flag not provided.')
    if not argData.isFlagSet( 'i' ):
      raise Exception('i / inframe flag not provided.')
    if not argData.isFlagSet( 'o' ):
      raise Exception('o / outframe flag not provided.')
    if not argData.isFlagSet( 'l' ):
      raise Exception('l / layer flag not provided.')
    if not argData.isFlagSet( 'c' ):
      raise Exception('c / camera flag not provided.')

    result['scene'] = argData.flagArgumentString( 's', 0 )
    result['inframe'] = argData.flagArgumentInt( 'i', 0 )
    result['outframe'] = argData.flagArgumentInt( 'o', 0 )
    result['layer'] = argData.flagArgumentString( 'l', 0 )
    result['camera'] = argData.flagArgumentString( 'c', 0 )
    return result

  @staticmethod
  def syntaxCreator():
    syntax = maya.OpenMaya.MSyntax()
    syntax.addFlag( 's', 'scene', maya.OpenMaya.MSyntax.kString )
    syntax.addFlag( 'i', 'inframe', maya.OpenMaya.MSyntax.kLong )
    syntax.addFlag( 'o', 'outframe', maya.OpenMaya.MSyntax.kLong )
    syntax.addFlag( 'l', 'layer', maya.OpenMaya.MSyntax.kString )
    syntax.addFlag( 'c', 'camera', maya.OpenMaya.MSyntax.kString )
    return syntax

  # Creator
  @staticmethod
  def creator():
      return maya.OpenMayaMPx.asMPxPtr(TSRenderCommand())

def initializePlugin(mobject):
  mplugin = maya.OpenMayaMPx.MFnPlugin(mobject)

  try:
    mplugin.registerCommand('ts_render', TSRenderCommand.creator, TSRenderCommand.syntaxCreator)
  except Exception as e:
    sys.stderr.write('Failed to register command ts_render. %s' % e)
    raise

def uninitializePlugin(mobject):
  mplugin = maya.OpenMayaMPx.MFnPlugin(mobject)

  try:
    mplugin.deregisterCommand('ts_render')
  except Exception as e:
    sys.stderr.write('Failed to unregister command ts_render. %s' % e)