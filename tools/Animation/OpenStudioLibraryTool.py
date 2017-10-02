# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class OpenStudioLibraryTool(Tool):

  ToolName = 'OpenStudioLibrary'
  ToolLabel = 'Open Studio Library'
  ToolCommand = 'openstudiolibrary'
  ToolDescription = 'Open Studio Library'
  ToolTooltip = 'Open Studio Library'

  def __init__(self, host):
    super (OpenStudioLibraryTool, self).__init__(host)
    self._noUI = True


  def executeMaya(self):

    import studiolibrary
    studiolibrary.main()