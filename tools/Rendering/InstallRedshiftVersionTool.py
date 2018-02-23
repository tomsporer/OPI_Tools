# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Tom Sporer. All rights reserved.
#

import os
import glob
import subprocess
import zipfile

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
    self.__RedshiftInstallRoot = "\\\\domain\\tomsporer\\PIPELINE\\ThirdParty\\RedShift"
    self.args.add(name="rsZipFile", type="file", label="RedShift Zip", filefilter="*.zip", mustexist=True)

  def preexecute(self):

    redshiftInstallRoot = self.__RedshiftInstallRoot
    if not os.path.exists(redshiftInstallRoot):
      raise OPIException("The path\n\n%s\n\ndoes not exist." % redshiftInstallRoot)
      return

    extractTool = os.path.join(redshiftInstallRoot, 'util', 'xsiaddonExtractor.exe')
    if not os.path.exists(extractTool):
      raise OPIException("The path\n\n%s\n\ndoes not exist." % extractTool)
      return


  def installRedShiftZip(self, redshiftInstallRoot, zipFile):
    QtWidgets = self.host.apis["QtWidgets"]
    version = zipFile.rpartition('_')[2].rpartition('.')[0]
    if len(version) == 0 or version.lower()[0] != 'v':
      msgBox = QtWidgets.QMessageBox
      msgBox.critical(None, "Opi Error", "The zip\n\n%s\n\ndoes not follow the naming convention.\nPlease use zip files with this format:\n\n%s" % (zipFile, 'redshift_v1.2.98.zip'))
      return False
    version = version[1:].lower()
    parts = version.partition('.')
    version = parts[0] + '.' + parts[2].replace('.', '')

    redshiftInstallLocation = os.path.join(redshiftInstallRoot, version)
    if not os.path.exists(redshiftInstallLocation):
      os.makedirs(redshiftInstallLocation)
    else:
      msgBox = QtWidgets.QMessageBox
      msgBox.critical(None, "Opi Error", "The folder\n\n%s\n\nalready exists. Please remove it first and restart this utility." % redshiftInstallLocation)
      return False

    print 'Unzipping %s ....' % zipFile
    with zipfile.ZipFile(zipFile, "r") as z:
      z.extractall(os.path.join(redshiftInstallLocation))

    # # setup the preferences
    # template = """
    # <?xml version=\"1.0\" encoding=\"UTF-8\"?>
    # <redshift_preferences version=\"1.2\">
    #   <preference name=\"CacheFolder\" type=\"string\" value=\"%ZK_PROJECT_SCRATCH_FOLDER%\\Redshift\\Cache\\\" />
    #   <preference name=\"TextureCacheBudgetGB\" type=\"int\" value=\"64\" />
    # </redshift_preferences>
    # """
    # preferencesPath = os.path.join(redshiftInstallLocation, 'Preferences')
    # if not os.path.exists(preferencesPath):
    #   os.makedirs(preferencesPath)
    # xmlPath = os.path.join(preferencesPath, 'preferences.xml')
    # open(xmlPath, 'w').write(template)

    extractTool = os.path.join(redshiftInstallRoot, 'util', 'xsiaddonExtractor.exe')

    addonFiles = glob.glob(os.path.join(redshiftInstallLocation, 'Redshift', 'Plugins', 'Softimage', '*.xsiaddon'))
    for addonFile in addonFiles:
      softimageVersions = [addonFile.lower().rpartition('softimage')[2].partition('.')[0].upper()]
      if softimageVersions[0] == '2014SP2':
        softimageVersions += ['2015SP2']

      for softimageVersion in softimageVersions:
        addonPath = os.path.join(redshiftInstallLocation, 'Softimage'+softimageVersion)
        cmd = [extractTool, '-o', addonPath, addonFile]
        process = subprocess.Popen(cmd)
        process.wait()

    print '\nInstalled to '+redshiftInstallLocation

    return True

  def execute(self):

    QtWidgets = self.host.apis["QtWidgets"]

    redshiftInstallRoot = self.__RedshiftInstallRoot
    rsZipFile = self.args.getValue("rsZipFile")

    result = self.installRedShiftZip(redshiftInstallRoot, rsZipFile)
    if result:
      msgBoxSuccess = QtWidgets.QMessageBox
      msgBoxSuccess.information(None, "RedShift", "Successfully installed.")

