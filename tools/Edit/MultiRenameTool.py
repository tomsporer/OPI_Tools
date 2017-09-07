# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#


from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class MultiRenameTool(Tool):

  ToolName = 'MultiRenameTool'
  ToolLabel = 'Rename multiple...'
  ToolCommand = 'multirenametool'
  ToolDescription = 'Rename multiple objects at once'
  ToolTooltip = 'Rename multiple objects at once'

  def __init__(self, host):
    super (MultiRenameTool, self).__init__(host)
    self._noUI = False


  def initialize(self, **args):
    self.args.add(name="addStart", type="str", label="Add Prefix", value="")
    self.args.add(name="replaceA", type="str", label="Replace...", value="")
    self.args.add(name="replaceB", type="str", label="With", value="")
    self.args.add(name="addEnd", type="str", label="Add Suffix", value="")
    self.args.add(name="removeNamespace", type="bool", label="Remove Namespace", value=False)
    self.args.addSpacer(5,1)
    self.args.beginRow("New Name")
    self.args.add(name="changeName", type="bool", label="", value=False)
    self.args.add(name="newName", type="str", label="New Name", value="*", enabled=False)
    self.args.endRow()

  def onValueChanged(self, arg):
    addStart = self.args.getValue("addStart")
    replaceA = self.args.getValue("replaceA")
    replaceB = self.args.getValue("replaceB")
    addEnd = self.args.getValue("addEnd")
    if arg.name == "changeName":
      self.args.get("newName").enabled = arg.value
    elif not arg.name == "newName":
      self.args.get("newName").value = addStart + "*" + addEnd



  def executeMaya(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    addStart = self.args.getValue("addStart")
    replaceA = self.args.getValue("replaceA")
    replaceB = self.args.getValue("replaceB")
    addEnd = self.args.getValue("addEnd")
    removeNamespace = self.args.getValue("removeNamespace")
    changeName = self.args.getValue("changeName")
    newName = self.args.getValue("newName")

    sel = cmds.ls(selection=True)
    for s in sel:
      oldNamespace = cmds.ls(s, showNamespace=True)[1]
      if oldNamespace == ":" or removeNamespace:
        oldNamespace = ""
      else:
        oldNamespace += ":"
      oldName = s.split("|")[-1].split(":")[-1]
      if changeName:
        cmds.rename(s, oldNamespace + newName)
      else:
        cmds.rename(s, oldNamespace + addStart + oldName.replace(replaceA, replaceB) + addEnd)
      