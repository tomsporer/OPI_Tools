# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os, sys

from opi.tools.tool import Tool
from opi.common.opiexception import OPIException

class SubmitRenderTool(Tool):

  ToolName = 'SubmitRender'
  ToolLabel = 'Submit Render'
  ToolCommand = 'submitrender'
  ToolDescription = 'submits a render job to the opi jobs server'
  ToolTooltip = 'submits a render job to the opi jobs server'

  def __init__(self, host):
    super (SubmitRenderTool, self).__init__(host)

  def initialize(self, **args):

    if not os.environ.has_key('OPI_SERVER_ADDRESS'):
      raise OPIException('The environment variable OPI_SERVER_ADDRESS is not set. Cannot submit render.')

    md = self.metaData

    self.args.add(name='destination', type='folder', mustexist=True, value=md.get('destination', None))

  def preexecute(self, **args):
    pass

  def execute (self):

    destination = self.args.getValue('destination')

    print 'weeeeee'

    # store the metadata for the next time around
    self.metaData.destination = destination
