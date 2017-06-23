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

class LoadUnloadRefTool(DataBaseTool):

  ToolName = 'LoadUnload'
  ToolLabel = 'Load/Unload references'
  ToolCommand = 'loadunloadref'
  ToolDescription = 'Load/Unload references'
  ToolTooltip = 'Load/Unload references'

  def __init__(self, host):
    super (LoadUnloadRefTool, self).__init__(host)

  def initialize(self, **args):

    self.args.addStaticText("\tLoad/Unload References \t \t \t")
    self.args.addSpacer(13)
    self.args.add(name="percentage", type="int", label="Percentage Loaded", range=[0,100], value=100)

  def executeMaya(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    percentage = self.args.getValue("percentage")


    references = cmds.file(q=True, reference=True )
    

    # for ref in references:
    #   refNode = cmds.referenceQuery(ref, referenceNode=True)
    #   uRand = randint(0, 100)
    #   if uRand <= percentage:
    #     cmds.file(loadReference=refNode)
    #   else:
    #     cmds.file(unloadReference=refNode)
      
    n = 1/(float(percentage)/100)
    p = n
    r = 1
    for ref in references:
      refNode = cmds.referenceQuery(ref, referenceNode=True)
      isLoaded = cmds.referenceQuery(refNode, isLoaded=True)
      if r >= p:
        if not isLoaded:
          cmds.file(loadReference=refNode)
        p = p + n
      else:
        if isLoaded:
          cmds.file(unloadReference=refNode)
      r += 1
