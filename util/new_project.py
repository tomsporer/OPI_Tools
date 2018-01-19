import os
import opi
from opi.client.database import DataBase as OpiDB
from opi.tools.host import Host as OPIHost
from opi.tools.workshop import WorkShop as OPIWorkShop
from opi.ui.Qt import QtWidgets, QtCore

filepath = os.path.abspath(__file__)

dbRoot = "e:\\projects"

path = os.path.split(filepath)[0]
path = os.path.split(path)[0]
path = os.path.split(path)[0]


templateRoot =  os.path.join(path, 'OPI_Tools', 'templates')
toolRoot =  os.path.join(path, 'OPI_Tools', 'tools')
os.environ["OPI_TOOL_DIR"] = toolRoot

db = OpiDB(dbRoot, templateRoot=templateRoot, rootSubFolders=[''])

host = OPIHost('python', {'db': db, 'QtWidgets': QtWidgets, 'QtCore': QtCore})
workshop = OPIWorkShop(host, toolRoot)

tool = workshop.instantiate(cmd='createproject')
tool.invokeWithUI(active=False)



