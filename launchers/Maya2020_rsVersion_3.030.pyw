import os
import sys
import glob
import json
import optparse

path = os.path.abspath(__file__)

# cut off the file path
path, filename = os.path.split(path)

# remember this launchers path
launchersPath = path
if launchersPath.lower().startswith('e:'):
  launchersPath = r'\\domain\\tomsporer' + launchersPath[2:]
  
# add the opi folders
path = os.path.split(path)[0]
path = os.path.split(path)[0]
path = os.path.join(path, 'opi', 'python')

# add opi to the system path
sys.path.append(path)

# construct the cfg path
if "rsVersion" in filename:
  cfgPath = os.path.join(launchersPath, 'configs', 'maya.cfg')
  cfgPathRsVersion = os.path.join(launchersPath, 'configs', 'maya_rsVersion.cfg')

  # safety: override maya_rsVersion.cfg file to match maya.cfg, if it doesn't
  with open(cfgPath, 'r') as cfgFile:
    cfgFile = cfgFile.read()
    lines = cfgFile.split("\n")
    for line in lines:
      if "\"RS_VERSION\":" in line:
        lines.remove(line)
    cfgFileWithoutRS = "\n".join(lines)

  with open(cfgPathRsVersion, 'r') as cfgFileRsVersion:
    cfgFileRsVersion = cfgFileRsVersion.read()
      
  if cfgFileWithoutRS == cfgFileRsVersion:
    pass
  else:
    with open(cfgPathRsVersion, 'w') as cfgFileRsVersion:
      cfgFileRsVersion.write(cfgFileWithoutRS)


  cfgPath = cfgPathRsVersion
  rsVersion = os.path.splitext(filename)[0][-5:]
  os.environ["RS_VERSION"] = rsVersion
elif "vray" in filename:
  cfgPath = os.path.join(launchersPath, 'configs', 'maya_vray.cfg')
elif "minimalOpi" in filename:
  cfgPath = os.path.join(launchersPath, 'configs', 'maya_minimalOpi.cfg')
else:
  cfgPath = os.path.join(launchersPath, 'configs', 'maya.cfg')

# find the maya executable
# first connect to the registry and get a specific key
import _winreg
from _winreg import ConnectRegistry, OpenKey, EnumKey, QueryValueEx, HKEY_LOCAL_MACHINE
registry = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
key = OpenKey(registry, "SOFTWARE\\Autodesk\\Maya\\2020\\Setup\\InstallPath", 0, (_winreg.KEY_WOW64_64KEY + _winreg.KEY_READ))
value = QueryValueEx(key, "MAYA_INSTALL_LOCATION")[0]

# setup options for running maya in batch mode
prog = os.path.basename(__file__)
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage, version="%prog 1.0")
parser.add_option("-s", "--sourcefile", dest="sourcefile", help="The source file")
parser.add_option("-b", "--batch", dest="batch", help="Set this to launch maya batch instead", action="store_true", default=False)
parser.add_option("-c", "--command", dest="command", help="The mel command to run. Needs to be specified in conjunction with --batch.")
description = optparse.OptionGroup(parser, "Description", "Launches Maya 2018.")
parser.add_option_group(description)
options, args = parser.parse_args()

if options.batch:
  if options.command is None:
    parser.print_help()
    sys.exit()

  mayaExe = os.path.join(value, 'bin', 'mayabatch.exe')

  os.environ['OPI_LAUNCHER_EXECUTABLE'] = str(mayaExe)
  os.environ['OPI_LAUNCHER_ARGS'] = json.dumps(['-command', options.command])
else:
  mayaExe = os.path.join(value, 'bin', 'maya.exe')
  os.environ['OPI_LAUNCHER_EXECUTABLE'] = str(mayaExe)

os.environ['OPI_LAUNCHER_DIR'] = launchersPath
os.environ['MAYA_LOCATION'] = str(value)
os.environ['MAYA_VERSION'] = "2020"


# figure out which projects are opi projects
# switch this to a relative path based on the launchersPath
if launchersPath.lower().find('pipeline') == -1:
  tempDir = "c:\\temp\\TomSporer\\Projects"
  if not os.path.exists(tempDir):
    os.makedirs(tempDir)
  os.environ['OPI_DATABASE_DIR'] = tempDir
  os.environ['REDSHIFT_INSTALLATION_ROOT'] = "c:\\temp\\TomSporer"
else:
  # os.environ['OPI_DATABASE_DIR'] = "\\\\192.168.1.10\\tomsporer\\PROJECTS"
  os.environ['OPI_DATABASE_DIR'] = "E:\\PROJECTS"

# folderNames = ['']
folderNames = ['FRI_Fritt_TV', 'FRI_Fritt_BumperAdShyCherry']

os.environ['OPI_DATABASE_SUBFOLDERS'] = os.pathsep.join(folderNames)

# exclude folders
# folders with an 'opiExcludeSubFolder.opiex' file inside will be excluded
# folders with an 'opiIncludeSubFolder.opiex' file inside will be included
excludeRootSubFoldersSubFolders = {}
for folderName in folderNames:
  if folderName == "":
    continue
  excludeRootSubFoldersSubFolders[folderName] = ["3D", "Client_From", "Client_To", "Composite", "Images", "Models", "Render", "Output"]
  excludeFolders = glob.glob(os.path.join(os.environ['OPI_DATABASE_DIR'], folderName, '*', 'opiExcludeSubFolder.opiex'))
  includeFolders = glob.glob(os.path.join(os.environ['OPI_DATABASE_DIR'], folderName, '*', 'opiIncludeSubFolder.opiex'))
  for excludeFolder in excludeFolders:
    excludeRootSubFoldersSubFolders[folderName] += [os.path.split(os.path.split(excludeFolder)[0])[1]]
  for includeFolder in includeFolders:
    includeFolderName = os.path.split(os.path.split(includeFolder)[0])[1]
    if includeFolderName in excludeRootSubFoldersSubFolders[folderName]:
      excludeRootSubFoldersSubFolders[folderName].remove(includeFolderName)

# exclude folders
# excludeRootSubFoldersSubFolders["FRI_Fritt_TV"] += ["3D"] # example
# include folders
# excludeRootSubFoldersSubFolders["BEI_Spiel"].remove("Models") # example

# set env variable
os.environ['OPI_DATABASE_EXLUDESUBFOLDERSSUBFOLDERS'] = json.dumps(excludeRootSubFoldersSubFolders) 

# import the opi launcher modules
from opi.launchers.environment import Environment

env = Environment(cfgPath)
env.launch()
