# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2017, Helge Mathee. All rights reserved.
#

import os
import glob

import opi
import peewee
from opi.client.database import DataBase as OpiDB

def test_tom_create_database():

  root = "\\\\192.168.1.10\\tomsporer\\PROJECTS"

  # find all subfolders with an opicfg file
  subfolders = glob.glob(os.path.join(root, '*', '.opicfg'))
  folderNames = []
  for subfolder in subfolders:
    folderNames += [os.path.split(os.path.split(subfolder)[0])[1]]

  if len(folderNames) == 0:
    folderNames += ['']

  # next you need some templates to use, we'll just use the samples
  templateSource = os.path.join(os.path.split(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])[0], 'templates')

  # ok - we are ready now to launch the data base. let's create one
  # and point it to our root
  db = OpiDB(root, templateRoot=templateSource, rootSubFolders=folderNames)

  projects = db.query('Project')

  for project in projects:
    print project.location

if __name__ == '__main__':
  test_tom_create_database()
