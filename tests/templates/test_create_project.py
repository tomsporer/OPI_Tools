# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2017, Helge Mathee. All rights reserved.
#

import os

import opi
import peewee
from opi.client.database import DataBase as OpiDB

def test_tom_create_project():

  root = opi.getEmptyUnitTestFolder('test_tom_create_project')

  # next you need some templates to use, we'll just use the samples
  templateSource = os.path.join(os.path.split(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])[0], 'templates')

  # ok - we are ready now to launch the data base. let's create one
  # and point it to our root
  backend = peewee.SqliteDatabase(os.path.join(root, "test.db"))
  db = OpiDB(root, templateRoot=templateSource, backend=backend)

  project = db.createNew('Project', shorthand='PRO', name='ProjectX')
  task3D = db.createNew('Task', project=project, name='3D')
  taskComposite = db.createNew('Task', project=project, name='Composite')

if __name__ == '__main__':
  test_tom_create_project()
