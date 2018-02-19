# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class RigFindDuplicateNamesTool(Tool):

  ToolName = 'RigFindDuplicateNames'
  ToolLabel = 'Find Duplicate Names'
  ToolCommand = 'rigfindduplicatenames'
  ToolDescription = 'Find Objects with the same Name'
  ToolTooltip = 'Find Objects with the same Name'

  def __init__(self, host):
    super (RigFindDuplicateNamesTool, self).__init__(host)
    self._noUI = True


  def executeMaya(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    # sel = cmds.ls(dagObjects=True)
    sel = [d for d in cmds.ls() if "|" in d]
    objs = []
    for s in sel:
      objs.append(s.split("|")[-1])

    duplicates = {name : objs.count(name) for name in objs}
    # for dupl in duplicates.keys():
    #   if duplicates[dupl] == 1:
    #     duplicates.pop(dupl)

    if duplicates.keys() != []:
      numDupls = len(duplicates.keys())
      print "# INFO: %s Duplicate Names Found:" %numDupls
      print duplicates
      dialogDupls = ""
      for dupl in duplicates.keys():
        dialogDupls += "\"%s\" - %s times\n" %(dupl, duplicates[dupl])

      dialog = cmds.confirmDialog(title="Duplicate Names Found!", message="Duplicate Names Found!\n\n" + dialogDupls, button=["Ok", "Select Duplicates"], defaultButton="Ok", cancelButton="Ok", dismissString="Ok")
      if dialog == "Select Duplicates":
        cmds.select(clear=True)
        for dupl in duplicates.keys():
          cmds.select("*|" + dupl, add=True)

    else:
      print "# INFO: No duplicates found"
      dialog = cmds.confirmDialog(title="No Duplicates Found.", message="No duplicate names found.", button=["Ok"], defaultButton="Ok", cancelButton="Ok", dismissString="Ok")