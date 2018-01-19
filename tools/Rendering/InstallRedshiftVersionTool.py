# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import glob
import subprocess
import zipfile
# import zookeeper

from opi.tools.databasetool import DataBaseTool
from opi.common.opiexception import OPIException


class InstallRedshiftVersionTool(DataBaseTool):

  ToolName = 'InstallRedshiftVersion'
  ToolLabel = 'Install Redshift Version'
  ToolCommand = 'installredshiftversion'
  ToolDescription = 'Install a new Redshift version'
  ToolTooltip = 'Install a new Redshift version'

  def __init__(self, host):
    super (InstallRedshiftVersionTool, self).__init__(host)
    self._noUI = False

  def initialize(self, **args):
    self.__softimage_workgroup_root = "\\\\192.168.1.10\\public\\zookeeper\\workgroups"
    self.args.add(name="rsZipFile", type="file", label="RedShift Zip", filefilter="*.zip", mustexist=True)

  def preexecute(self):

    QtWidgets = self.host.apis["QtWidgets"]

    softimage_workgroup_root = self.__softimage_workgroup_root
    if not os.path.exists(softimage_workgroup_root):
      raise OPIException("The path\n\n%s\n\ndoes not exist." % softimage_workgroup_root)
      return

    extractTool = os.path.join(softimage_workgroup_root, 'util', 'xsiaddonExtractor.exe')
    if not os.path.exists(extractTool):
      raise OPIException("The path\n\n%s\n\ndoes not exist." % extractTool)
      return



  def installRedShiftZip(self, softimage_workgroup_root, zipFile):
    QtWidgets = self.host.apis["QtWidgets"]
    version = zipFile.rpartition('_')[2].rpartition('.')[0]
    if len(version) == 0 or version.lower()[0] != 'v':
      msgBox = QtWidgets.QMessageBox
      msgBox.critical(None, "ZooKeeper Error", "The zip\n\n%s\n\ndoes not follow the naming convention.\nPlease use zip files with this format:\n\n%s" % (zipFile, 'redshift_v1.2.98.zip'))
      return False
    version = version[1:].lower()
    parts = version.partition('.')
    version = parts[0] + '.' + parts[2].replace('.', '')

    workgroup = os.path.join(softimage_workgroup_root, 'renderer', 'RedShift', version)
    if not os.path.exists(workgroup):
      os.makedirs(workgroup)
    else:
      msgBox = QtWidgets.QMessageBox
      msgBox.critical(None, "ZooKeeper Error", "The folder\n\n%s\n\nalready exists. Please remove it first and restart this utility." % workgroup)
      return False

    print 'Unzipping %s ....' % zipFile
    with zipfile.ZipFile(zipFile, "r") as z:
      z.extractall(os.path.join(workgroup))

    # setup the preferences
    template = """
    <?xml version=\"1.0\" encoding=\"UTF-8\"?>
    <redshift_preferences version=\"1.2\">
      <preference name=\"CacheFolder\" type=\"string\" value=\"%ZK_PROJECT_SCRATCH_FOLDER%\\Redshift\\Cache\\\" />
      <preference name=\"TextureCacheBudgetGB\" type=\"int\" value=\"64\" />
    </redshift_preferences>
    """
    # <preference name="AllCudaDevices" type="string" value="0:Quadro K6000," />
    # <preference name="SelectedCudaDevices" type="string" value="0:Quadro K6000," />
    preferencesPath = os.path.join(workgroup, 'Preferences')
    if not os.path.exists(preferencesPath):
      os.makedirs(preferencesPath)
    xmlPath = os.path.join(preferencesPath, 'preferences.xml')
    open(xmlPath, 'w').write(template)

    extractTool = os.path.join(softimage_workgroup_root, 'util', 'xsiaddonExtractor.exe')

    addonFiles = glob.glob(os.path.join(workgroup, 'Redshift', 'Plugins', 'Softimage', '*.xsiaddon'))
    for addonFile in addonFiles:
      softimageVersions = [addonFile.lower().rpartition('softimage')[2].partition('.')[0].upper()]
      if softimageVersions[0] == '2014SP2':
        softimageVersions += ['2015SP2']

      for softimageVersion in softimageVersions:
        addonPath = os.path.join(workgroup, 'Softimage'+softimageVersion)
        cmd = [extractTool, '-o', addonPath, addonFile]
        process = subprocess.Popen(cmd)
        process.wait()

        # hmathee: don't create the pathconfig files anymore - we are not using them
        # xmlPath = os.path.join(addonPath, 'Application', 'Plugins', 'bin', 'nt-x86-64', 'pathconfig.xml')
        # template = "<path name=\"REDSHIFT_COREDATAPATH\" value=\"%s\" />\n"
        # template += "<path name=\"REDSHIFT_PREFSPATH\" value=\"%s\" />\n"
        # xmlContent = template % (
        #   "%ZK_SOFTIMAGE_WORKGROUP_ROOT%/renderer/RedShift/%ZK_RENDERER_VERSION%/RedShift",
        #   "%ZK_SOFTIMAGE_WORKGROUP_ROOT%/renderer/RedShift/%ZK_RENDERER_VERSION%/Preferences/preferences.xml")
        # open(xmlPath,'w').write(xmlContent)

    print '\nInstalled to '+workgroup

    return True

  def execute(self):

    QtWidgets = self.host.apis["QtWidgets"]

    softimage_workgroup_root = self.__softimage_workgroup_root
    rsZipFile = self.args.getValue("rsZipFile")

    result = self.installRedShiftZip(softimage_workgroup_root, rsZipFile)
    if result:
      msgBoxSuccess = QtWidgets.QMessageBox
      msgBoxSuccess.information(None, "RedShift", "Successfully installed.")

