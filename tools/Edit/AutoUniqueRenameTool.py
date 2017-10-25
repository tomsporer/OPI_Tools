# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import re
from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class AutoUniqueRenameTool(Tool):

  ToolName = 'AutoUniqueRenameTool'
  ToolLabel = 'Make names unique'
  ToolCommand = 'autouniquerenametool'
  ToolDescription = 'Make names of selected objects unique in the scene'
  ToolTooltip = 'Make names unique'

  def __init__(self, host):
    super (AutoUniqueRenameTool, self).__init__(host)
    self._noUI = True


  def executeMaya(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    sel = cmds.ls(selection=True)
     
    if sel:
      #Sort selection by hierarchy so that we don't rename a parent before a child.
      sel.sort(key=lambda obj: obj.count('|'), reverse=True)

      #the selection is lost when renaming, so we make a new selection list
      cmds.select(clear=True)
      newSel = []
      for name in sel:
        transform = cmds.objectType(name) == "transform"
        # extract the base name
        m = re.compile("[^|]*$").search(name) 
        shortname = m.group(0)

        # extract the numeric suffix
        m2 = re.compile(".*[^0-9]").match(shortname) 
        if m2:
            stripSuffix = m2.group(0)
        else:
            stripSuffix = shortname
         
        #rename, adding '#' as the suffix, which tells maya to find the next available number
        newname = cmds.rename(name, (stripSuffix + "#")) 
        print "renamed %s to %s" % (name, newname)

        #if the renamed node is a transform node, i.e. no shape node, we'll add it to the selection list
        if transform:
          newSel += [newname]
          
      cmds.select(newSel)
    else:
      print "Nothing selected"
           
