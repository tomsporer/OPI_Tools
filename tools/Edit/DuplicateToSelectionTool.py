# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#


from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class DuplicateToSelectionTool(Tool):

  ToolName = 'DuplicateToSelectionTool'
  ToolLabel = 'Duplicate to Selection...'
  ToolCommand = 'duplicatetoselectiontool'
  ToolDescription = 'Duplicate the last object in the selection to the selected objects'
  ToolTooltip = 'Duplicate Object to Selection'

  def __init__(self, host):
    super (DuplicateToSelectionTool, self).__init__(host)
    self._noUI = False


  def initialize(self, **args):
    self.args.addStaticText("\tDuplicate Object to Selection \t \t")
    self.args.addSpacer(13)

    self.args.beginRow("Geometry Type")
    self.args.addStaticText("")
    self.args.endRow()
    self.args.add(name="copy", type="bool", label="Copy", value=True)
    self.args.add(name="instance", type="bool", label="Instance", value=False)
    self.args.addSpacer(1)
    self.args.beginRow("Duplicate")
    self.args.addStaticText("")
    self.args.endRow()
    self.args.add(name="duplFirst", type="bool", label="First in Selection", value=True)
    self.args.add(name="duplLast", type="bool", label="Last in Selection", value=False)
    self.args.addSpacer(1)
    self.args.addSpacer(7,1)
    self.args.beginRow("Match Transforms")
    self.args.addStaticText("")
    self.args.endRow()
    self.args.add(name="matchT", type="bool", label="Translate", value=True)
    self.args.add(name="matchR", type="bool", label="Rotate", value=True)
    self.args.add(name="matchS", type="bool", label="Scale", value=True)
    self.args.addSpacer(1)
    self.args.addSpacer(7,1)
    self.args.beginRow("Hierarchy Options")
    self.args.addStaticText("")
    self.args.endRow()
    self.args.add(name="replace", type="bool", label="Replace Targets", value=True)
    self.args.add(name="replaceHierarchy", type="bool", label="Replace Target Hierarchies", value=False)
    self.args.add(name="asChild", type="bool", label="Make Child of Targets", value=False)
    self.args.add(name="asParent", type="bool", label="Make Parent of Targets", value=False)
    self.args.add(name="noParenting", type="bool", label="None (don't change Hierarchy)", value=False)
    self.args.addSpacer(1)
    self.args.addSpacer(7,1)
    self.args.beginRow("Duplicate Options")
    self.args.addStaticText("")
    self.args.endRow()
    self.args.add(name="duplInputGraph", type="bool", label="Duplicate input graph", value=False)
    self.args.add(name="duplInputConns", type="bool", label="Duplicate input connections", value=False)
    self.args.addSpacer(1)
    self.args.addSpacer(7,1)
    self.args.add(name="delOriginal", type="bool", label="Delete Original", value=False)

  def onValueChanged(self, arg):
    if arg.name == "copy":
      self.args.get("instance").value = not arg.value
    elif arg.name == "instance":
      self.args.get("copy").value = not arg.value

    if arg.name == "duplFirst":
      self.args.get("duplLast").value = not arg.value
    elif arg.name == "duplLast":
      self.args.get("duplFirst").value = not arg.value

    # if arg.name == "replace":
    #   self.args.get("replaceHierarchy").value = False
    #   self.args.get("asChild").value = False
    #   self.args.get("asParent").value = False
    #   self.args.get("noParenting").value = not arg.value
    # elif arg.name == "replaceHierarchy":
    #   self.args.get("replace").value = False
    #   self.args.get("asChild").value = False
    #   self.args.get("asParent").value = False
    #   self.args.get("noParenting").value = not arg.value
    # elif arg.name == "asChild":
    #   self.args.get("replace").value = False
    #   self.args.get("replaceHierarchy").value = False
    #   self.args.get("asParent").value = False
    #   self.args.get("noParenting").value = not arg.value
    # elif arg.name == "asParent":
    #   self.args.get("replace").value = False
    #   self.args.get("replaceHierarchy").value = False
    #   self.args.get("asChild").value = False
    #   self.args.get("noParenting").value = not arg.value
    # elif arg.name == "noParenting":
    #   self.args.get("replaceHierarchy").value = False
    #   self.args.get("asChild").value = False
    #   self.args.get("asParent").value = False
    #   self.args.get("replace").value = not arg.value

    hierOptions = ["replace", "replaceHierarchy", "asChild", "asParent", "noParenting"]
    if arg.name in hierOptions:
      if arg.value == True:
        for hierOption in hierOptions:
          if not hierOption == arg.name:
            self.args.get(hierOption).value = False
      else:
        if arg.name == "noParenting":
          self.args.get("replace").value = True
        else:
          self.args.get("noParenting").value = True
          

    if arg.name == "duplInputGraph" and arg.value == True:
      self.args.get("duplInputConns").value = False
    elif arg.name == "duplInputConns" and arg.value == True:
      self.args.get("duplInputGraph").value = False


  def executeMaya(self):
    maya = self.host.apis['maya']
    cmds = maya.cmds

    matchT = self.args.getValue("matchT")
    matchR = self.args.getValue("matchR")
    matchS = self.args.getValue("matchS")

    replace = self.args.getValue("replace")
    replaceHierarchy = self.args.getValue("replaceHierarchy")
    asChild = self.args.getValue("asChild")
    asParent = self.args.getValue("asParent")
    noParenting = self.args.getValue("noParenting")

    instance = self.args.getValue("instance")
    duplInputGraph = self.args.getValue("duplInputGraph")
    duplInputConns = self.args.getValue("duplInputConns")

    duplFirst = self.args.getValue("duplFirst")
    duplLast = self.args.getValue("duplLast")

    delOriginal = self.args.getValue("delOriginal")

    sel = cmds.ls(selection=True)

    if duplFirst:
      targets = sel[1:]
      hero = sel[0]
    if duplLast:
      targets = sel[:-1]
      hero = sel[-1]


    for target in targets:
      if instance:
        duplHero = cmds.instance(hero)
      else:
        duplHero = cmds.duplicate(hero, upstreamNodes=duplInputGraph, inputConnections=duplInputConns)[0]

      if matchT or matchR or matchS:
        cmds.matchTransform(duplHero, target, pos=matchT, rot=matchR, scl=matchS)

      if noParenting:
        pass
      else:
        if asChild:
          cmds.parent(duplHero, target)
        else:
          # Start reparenting duplicates and targets
          tParent = cmds.listRelatives(target, parent=True, path=True)
          duplParent = cmds.listRelatives(duplHero, parent=True, path=True)
          if not tParent:
            # If the target has no parent, it's the world root.
            if cmds.listRelatives(duplHero, parent=True):
              # Only parent to world if it not already is.
              cmds.parent(duplHero, world=True)
          elif not tParent == duplParent:
            # Only parent if the duplicate and target don't already have the same parent.
            cmds.parent(duplHero, tParent)

          if asParent:
            cmds.parent(target, duplHero)

        # Delete targets when they get replaced
        if replace:
          tChildren = cmds.listRelatives(target, children=True, path=True)
          tShape = cmds.listRelatives(target, shapes=True, path=True)
          if tShape:
            for shape in tShape:
              tChildren.remove(shape)
          if tChildren:
            cmds.parent(tChildren, duplHero)
          cmds.delete(target)
        elif replaceHierarchy:
          cmds.delete(target)

    if delOriginal:
      cmds.delete(hero)