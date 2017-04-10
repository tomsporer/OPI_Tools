import os
import sys
import glob
import json
import optparse

path = os.path.abspath(__file__)

# cut off the file path
path = os.path.split(path)[0]

# remember this launchers path
launchersPath = path

if launchersPath.lower().startswith('e:'):
  launchersPath = r'\\domain\\tomsporer' + launchersPath[2:]

# go two levels up
path = os.path.split(path)[0]
path = os.path.split(path)[0]

# add opi to the system path
sys.path.append(os.path.join(path, 'opi', 'python'))

from opi.ui.Qt import QtWidgets, QtCore
import opi
import opi.ui.jobs
from opi.ui.jobs.managerwidget import ManagerWidget
from opi.jobs.jobserver import JobServer
from opi.jobs.jobworker import JobWorker
from opi.jobs.jobmanager import JobManager

def job_manager():

  app = QtWidgets.QApplication(sys.argv)

  address = ('192.168.1.25', 6666)
  root = opi.getEmptyUnitTestFolder('job_manager')

  source = os.path.join(root, 'source.txt')
  with open(source, 'wb') as f:
    f.write('foo')

  with JobManager(address) as manager:

    widget = QtWidgets.QWidget()
    widget.setWindowTitle('OPI Job Manager')
    widget.setContentsMargins(5, 5, 5, 5)
    widget.setMinimumWidth(1100)
    widget.setMinimumHeight(900)

    cssPath = os.path.join(os.path.split(opi.ui.jobs.__file__)[0], 'opijobs.css')
    cssContent = open(cssPath, 'rb').read()
    widget.setStyleSheet(cssContent)

    layout = QtWidgets.QHBoxLayout()
    widget.setLayout(layout)

    jobWidget = ManagerWidget(parent=widget, manager=manager)
    layout.addWidget(jobWidget)

    widget.show()
    app.exec_()

job_manager()
