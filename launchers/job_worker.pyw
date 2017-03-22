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
from opi.ui.jobs.workerwidget import WorkerWidget
from opi.jobs.jobserver import JobServer
from opi.jobs.jobworker import JobWorker
from opi.jobs.jobmanager import JobManager

def job_worker():

  app = QtWidgets.QApplication(sys.argv)

  address = ('192.168.1.25', 6666)

  with JobWorker(address, ping_interval=1.0) as worker:
    with JobManager(address) as manager:
      widget = WorkerWidget(parent=None, worker=worker, manager=manager)
      widget.setContentsMargins(5, 5, 5, 5)
      widget.setMinimumWidth(600)
      widget.setMinimumHeight(900)

      cssPath = os.path.join(os.path.split(opi.ui.jobs.__file__)[0], 'opijobs.css')
      cssContent = open(cssPath, 'rb').read()
      widget.setStyleSheet(cssContent)

      widget.show()
      app.exec_()

job_worker()
