import os
import sys

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
cfgPath = os.path.join(launchersPath, 'configs', 'xsi.cfg')

# find the xsi executable
# first connect to the registry and get a specific key
from _winreg import ConnectRegistry, OpenKey, EnumKey, QueryValueEx, HKEY_LOCAL_MACHINE
registry = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
key = OpenKey(registry, "SOFTWARE\\Autodesk\\Softimage\\InstallPaths")
value = QueryValueEx(key, "2015")[0]

xsiExe = os.path.join(value, 'Application', 'bin', 'xsi.exe')

os.environ['OPI_LAUNCHER_EXECUTABLE'] = str(xsiExe)
os.environ['XSI_LOCATION'] = str(value).rstrip("\\")
os.environ['XSI_VERSION'] = "2015"

# import the opi launcher modules
from opi.launchers.environment import Environment

env = Environment(cfgPath)
env.launch()



# import os

# for key in sorted(os.environ.keys()):
# 	Application.Logmessage(str(key) + ":" + str(os.environ[key])