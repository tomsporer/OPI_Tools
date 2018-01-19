import os.path
import os
import sys
import subprocess
import traceback


from win32com.client import constants
##-------------------------------------------------------------------------------------
## SubmitSoftimageToDeadline.py
## Thinkbox Software Inc, 2016
##
## This proxy script submits a Softimage scene to Deadline to be rendered.
##-------------------------------------------------------------------------------------

##-------------------------------------------------------------------------------------
## CALL BACKS
##-------------------------------------------------------------------------------------
def XSILoadPlugin(in_reg):
    
    #Set up some basic information for the whole plug-in
    in_reg.Name = "Submit Softimage To Deadline Python Style"
    in_reg.Author = "Ryan Russell (Thinkbox Software Inc)"
    in_reg.Email = "support@thinkboxsoftware.com"
    in_reg.URL = "http://www.thinkboxsoftware.com/deadline/"
    in_reg.Major = 1
    in_reg.Minor = 0
    
    # Register the SubmitToDeadline command
    in_reg.RegisterCommand("SubmitSoftimageToDeadline_PY", "SubmitSoftimageToDeadline")
    
    # Register a Menu as another plug-in item to appear in the render menu
    in_reg.RegisterMenu(constants.siMenuTbRenderRenderID , "SSTDPYMenu", False, False)
    
    #set up the custom path
    repositoryScripts=GetRepositoryPath("submission/Softimage/Main")        
        
    if repositoryScripts not in sys.path :
        sys.path.append( repositoryScripts)
        Application.LogMessage( "Appending \"" + repositoryScripts + "\" to system path to import SoftimageToDeadline module", 8 )
    else:
        Application.LogMessage( "\"%s\" is already in the system path" % repositoryScripts, 8 )
   
    # Finish with success notification
    return True

def SubmitSoftimageToDeadline_PY_Init(in_context):
    oCmd = in_context.Source
    oCmd.ReturnValue = False
    return True

def SubmitSoftimageToDeadline_PY_Execute(in_context):
    Main(in_context)

def SSTDPYMenu_Init(in_context):
    oMnu = in_context.Source
    menuitem = oMnu.AddCallbackItem( "Submit Softimage to Deadline", "Main" )
    return True


##-------------------------------------------------------------------------------------
## FUNCTIONS
##-------------------------------------------------------------------------------------

def GetDeadlineCommand():
    deadlineBin = ""
    try:
        deadlineBin = os.environ['DEADLINE_PATH']
    except KeyError:
        #if the error is a key error it means that DEADLINE_PATH is not set. however Deadline command may be in the PATH or on OSX it could be in the file /Users/Shared/Thinkbox/DEADLINE_PATH
        pass
        
    # On OSX, we look for the DEADLINE_PATH file if the environment variable does not exist.
    if deadlineBin == "" and  os.path.exists( "/Users/Shared/Thinkbox/DEADLINE_PATH" ):
        with open( "/Users/Shared/Thinkbox/DEADLINE_PATH" ) as f:
            deadlineBin = f.read().strip()

    deadlineCommand = os.path.join(deadlineBin, "deadlinecommand")
    
    return deadlineCommand

# Get The Repository Path using DeadlineCommand
def GetRepositoryPath(folder):
    deadlineCommand = GetDeadlineCommand()
    
    startupinfo = None
    if os.name == 'nt':
        # Python 2.6 has subprocess.STARTF_USESHOWWINDOW, and Python 2.7 has subprocess._subprocess.STARTF_USESHOWWINDOW, so check for both.
        if hasattr( subprocess, '_subprocess' ) and hasattr( subprocess._subprocess, 'STARTF_USESHOWWINDOW' ):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
        elif hasattr( subprocess, 'STARTF_USESHOWWINDOW' ):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    proc = subprocess.Popen([deadlineCommand, '-getrepositorypath', folder], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
    proc.stdin.close()
    proc.stderr.close()    
    path = proc.stdout.read()

    if path == "":
        Application.LogMessage( "The SoftimageToDeadline.py script could not be found in the Deadline Repository. Please make sure that the Deadline Client has been installed on this machine, that the Deadline Client bin folder is set in the DEADLINE_PATH environment variable, and that the Deadline Client has been configured to point to a valid Repository.", 2 )
    else:
        path = path.replace("\n","").replace("\r","")
    return path

##-------------------------------------------------------------------------------------
## MAIN FUNCTION
##-------------------------------------------------------------------------------------

def Main(in_context):
    try:
        import SoftimageToDeadline
        SoftimageToDeadline.Main()
    except:
        Application.LogMessage( traceback.format_exc() )
        Application.LogMessage( "An error was encountered when loading SoftimageToDeadline.py. Please make sure that the Deadline Client has been installed on this machine, that the Deadline Client bin folder is set in the DEADLINE_PATH environment variable, and that the Deadline Client has been configured to point to a valid Repository.", 2 )
        
