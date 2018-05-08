# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import re
import sys

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class RigLabelJointsTool(Tool):

  ToolName = 'RigLabelJoints'
  ToolLabel = 'Label Joints'
  ToolCommand = 'riglabeljoints'
  ToolDescription = 'Label Joints'
  ToolTooltip = 'Label Joints'

  def __init__(self, host):
    super (RigLabelJointsTool, self).__init__(host)

  def initialize(self, **args):
    self.args.add(name="side", type="str", combo=["Get from jnt name", "M", "L", "R"], value=args.get('side', "Get from jnt name"))


  def executeMaya(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    sel = cmds.ls(selection=True)
    setSide = self.args.getValue("side")
    sConvert = {"M":0, "L":1, "R":2}
    for jnt in sel:
      if cmds.objectType(jnt) != "joint":
        continue
      if setSide == "Get from jnt name":
        s = jnt.split("_")
        for ssplit in s:
          if ssplit in sConvert:
            side = sConvert[ssplit]
            s.remove(ssplit)
            sName = "_".join(s)
            break
        else:
          print "# INFO: could not get side from jnt name for \"%s\"" %(jnt)
          side = 3
          sName = jnt
      else:
        side = sConvert[setSide]
            
      cmds.setAttr(jnt + ".side", side)
      cmds.setAttr(jnt + ".type", 18) # 18 = Other
      cmds.setAttr(jnt + ".otherType", sName, type="string")