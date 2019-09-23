import os
import tkFileDialog

# -------------------------------------------
# This Script will add a new menu item in the Yeti menu, which will run the
# command to return the currently used license.
# 
# 1. Run the script (double click)
# 2. Select the Yeti plugin folder (ex. E:/PIPELINE/ThirdParty/Yeti/Yeti-v3.5.2_Maya2019-windows)
# 
# -------------------------------------------

fileLocation = os.path.dirname(__file__)
pipelineDir = os.path.split(os.path.split(fileLocation)[0])[0]
thirdpartyDir = os.path.join(pipelineDir, "ThirdParty")
if os.path.exists(thirdpartyDir):
    initialDir = thirdpartyDir
else:
    initialDir = fileLocation

yetiDir = tkFileDialog.askdirectory(initialdir=initialDir, title="Select Yeti plugin folder")

pgYeti = os.path.join(yetiDir, "scripts", "pgYeti.mel")

if not os.path.exists(pgYeti):
    raise Exception("No pgYeti.mel file was found in selected directory")

with open(pgYeti, "r") as mel:
    content = mel.read()
    lines = content.split("\n")
    for i in range(len(lines)):
        line = lines[i]
        if "menuItem -label \"Return License\"" in line:
            raise Exception("Return License menuItem already in file")
        if "menuItem -label \"Help\"" in line:
            helpLine = lines[i]
            break
    helpCode = helpLine.split("menuItem -label ")[1]
    retLicCode = "\"Return License\" -command \"pgYetiCommand -returnLicense\";"
    retLicLine = helpLine.replace(helpCode, retLicCode)
    lines.insert(i, retLicLine)
    newContent = "\n".join(lines)

with open(pgYeti, "w") as mel:
    mel.write(newContent)