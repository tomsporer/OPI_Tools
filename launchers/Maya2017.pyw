import os
import sys
import glob

path = os.path.abspath(__file__)

# cut off the file path
path = os.path.split(path)[0]

# remember this launchers path
launchersPath = path

# go two levels up
path = os.path.split(path)[0]
path = os.path.split(path)[0]

# add the opi folders
path = os.path.join(path, 'opi', 'python')

# add opi to the system path
sys.path.append(path)

# construct the cfg path
cfgPath = os.path.join(launchersPath, 'configs', 'maya.cfg')

# find the maya executable
# first connect to the registry and get a specific key
from _winreg import ConnectRegistry, OpenKey, EnumKey, QueryValueEx, HKEY_LOCAL_MACHINE
registry = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
key = OpenKey(registry, "SOFTWARE\\Autodesk\\Maya\\2017\\Setup\\InstallPath")
value = QueryValueEx(key, "MAYA_INSTALL_LOCATION")[0]

mayaExe = os.path.join(value, 'bin', 'maya.exe')

os.environ['OPI_LAUNCHER_DIR'] = launchersPath
os.environ['OPI_LAUNCHER_EXECUTABLE'] = str(mayaExe)
os.environ['MAYA_LOCATION'] = str(value)
os.environ['MAYA_VERSION'] = "2017"

# figure out which projects are opi projects
# switch this to a relative path based on the launchersPath
os.environ['OPI_DATABASE_DIR'] = "\\\\192.168.1.10\\tomsporer\\PROJECTS"

# find all subfolders with an opicfg file
subfolders = glob.glob(os.path.join(os.environ['OPI_DATABASE_DIR'], '*', '.opicfg'))
folderNames = []
for subfolder in subfolders:
  folderNames += [os.path.split(os.path.split(subfolder)[0])[1]]

if len(folderNames) == 0:
  folderNames += ['']

os.environ['OPI_DATABASE_SUBFOLDERS'] = os.pathsep.join(folderNames)

# import the opi launcher modules
from opi.launchers.environment import Environment

env = Environment(cfgPath)
env.launch()
