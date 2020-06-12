import os
import sys
import json

path = os.path.abspath(__file__)

# cut off the file path
path, filename = os.path.split(path)

# remember this launchers path
launchersPath = path

# add the opi folders
path = os.path.split(path)[0]
path = os.path.split(path)[0]
path = os.path.join(path, 'opi', 'python')

# add opi to the system path
sys.path.append(path)

if launchersPath.lower().startswith('e:'):
  launchersPath = r'\\domain\\tomsporer' + launchersPath[2:]

# construct the cfg path
houdiniMajorVersion = filename[7:-4]
cfgPath = os.path.join(launchersPath, 'configs', 'houdini%s.cfg' %(houdiniMajorVersion))
cfgJson = json.load(open(cfgPath))
houdiniVersion = cfgJson["environment"]["HOUDINI_VERSION"][0]


# find the houdini executable
# first connect to the registry and get a specific key
import _winreg
from _winreg import ConnectRegistry, OpenKey, EnumKey, QueryValueEx, HKEY_LOCAL_MACHINE
registry = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
key = OpenKey(registry, "SOFTWARE\\Side Effects Software\\Houdini %s" %(houdiniVersion), 0, (_winreg.KEY_WOW64_64KEY + _winreg.KEY_READ))
value = QueryValueEx(key, "InstallPath")[0]

houdiniExe = os.path.join(value, 'bin', 'hindie.exe')
os.environ['OPI_LAUNCHER_EXECUTABLE'] = str(houdiniExe)

os.environ['OPI_LAUNCHER_DIR'] = launchersPath
os.environ['HOUDINI_LOCATION'] = str(value)
os.environ['HOUDINI_VERSION'] = houdiniVersion

# import the opi launcher modules
from opi.launchers.environment import Environment

env = Environment(cfgPath)
env.launch()
