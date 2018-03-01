#################################################

__author__  = "Jon Metzger, Maryann O'Connell, Himanjal Sharma"
__date__    = "01/09/18 - 02/22/18"
__copyright__   = "Copyright 2018, Major Qualifying Project"
__credits__     = "Vincent Chen, Andrew Tran, Mark Claypool"
__department__  = "Software Security"
__company__     = "NVidia"
__version__     = "1.0"
__status__  = "Development"

#################################################



from subprocess import *
import subprocess
import tempfile
import time
import untangle
import datetime
import os 
import re
import string
from mask import mask
from Tkinter import *
from launchQemu import launchServer

lgrey = '#d9d9d9'
black = '#000000'
white = '#ffffff'
green = '#98FB98'
yellow = '#ffff00'
pink ='#ffa797'


MASK_TO_APPLY = "flipAlt"
PORTNUMBER = 1234

class trigger:
    reg = ""
    val = ""
    op = ""


class Model:


    faults = []
    cFile = ""
    xmlFile = ""
    logfileName = ""
    log = None
    topLevel = None
    pluginProcess = None
    tempf = None
    feedbackLine = None
    pointer = 0
    regList = []
    choices = {'r0':0, 'r1':0, 'r2':0, 'r3':0, 'r4':0, 'r5':0, 'r6':0, 'r7':0, 'r8':0, 'r9':0, 'r10':0, 'r11':0, 'r12':0, 'sp':0, 'lr':0, 'pc':0, 'cpsr':0}


    #initializez the Model
    def __init__(self, top):
        self.topLevel = top
        self.tempf = tempfile.TemporaryFile()
        self.logfileName = "LogFile_" + datetime.datetime.now().strftime("%B_%d_%Y__%I:%M%p") + ".txt"
        self.log = "\n***** LOGFILE *****\n\n"#open(self.logfileName, 'a')



    def onClose(self):
        self.log = self.log + "\n\n***** END OF LOGFILE *****\n\n"
        with open(self.logfileName, "w") as f:
            f.write(self.log)
            #print self.log
            f.close()

    #Prints the output from GDB to the Console in app
    def printOutput(self, lines):
        #print line
        time.sleep(0.1)
        for line in lines.split('\n'):
            if line == "(gdb) ": continue
            if len(line) < 1: continue
            line = " > [ " + line + " ]"
            self.topLevel.gdb_table.insert(END, line)
            self.log = self.log + line + "\n"
            self.topLevel.gdb_table.update()
            self.topLevel.gdb_table.see("end")

    #stores the feedback line in data and highlights the line in source code
    def setFeedback(self, lineNo):
        
        #print "Selecting FeedBack"

        if self.feedbackLine is None:
            self.feedbackLine = lineNo
            self.topLevel.source_table.itemconfig(int(lineNo) - 1,{'bg':green})
        else:
            self.topLevel.source_table.itemconfig(int(self.feedbackLine) - 1,{'bg':white})
            self.topLevel.source_table.itemconfig(int(lineNo) - 1,{'bg':green})
            self.feedbackLine = lineNo

        self.topLevel.source_table.update()
    

    #Parses the XML file and populates List Faults with tuples of (Breakpoint and the list of all its triggers)
    def populateFaults(self):
        self.faults = []
        for item in self.xmlFile.xml.fault:
            addr = item.addr['breakpointAddress']
            
            trig = []
            for masks in item.trigger.mask:
                newTrigger = trigger()
                newTrigger.reg = masks.rg['register'] 
                newTrigger.val = masks.mk['val']
                newTrigger.op = masks.mk['op']
                trig.append(newTrigger)

            self.faults.append((addr, trig))

    def connect(self):
        file = self.cFile
            
        launchServer(file, PORTNUMBER)
        
        self.pluginProcess = Popen('arm-none-eabi-gdb', stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=self.tempf)
        self.pluginProcess.stdin.write("file {0}-arm\n".format(file.split('.')[0]))
        self.pluginProcess.stdin.write("target remote localhost: " + str(PORTNUMBER) + "\n")
        self.pluginProcess.stdin.write("set pagination off\n")

        line = self.read()

        self.sendCommand("info R")



    '''
    Takes in line No of source code as argument 
    Adds a breakpoint at the line number to extract address in memory at that line
    '''
    def showAssemCode(self, lineNo):

        #clear listbox
        self.topLevel.machine_table.delete(0, END)
        
        #add breakpoint at line number
        self.pluginProcess.stdin.write("B " + str(lineNo + 1) + "\n")
        
        lines = self.read().split()
        

        #get breakpoint number and address to disassem
        if "(gdb)" in lines[0].lower():
            bpNum = lines[2]
            bpAddr = lines[4][:-1]
        else:
            bpNum = lines[1]
            bpAddr = lines[3][:-1]

        self.updateMachineCode(bpAddr)
        
        #delete Breakpoint
        self.pluginProcess.stdin.write("del " + str(bpNum) + "\n")

    '''
    Takes in a Memory Address and disassems the machine code at 
    the address and updates the listbox with the generated machine code.
    '''
    def updateMachineCode(self, bpAddr):

        #disassem code at given address
        self.topLevel.machine_table.delete(0, END)
        self.pluginProcess.stdin.write("disassemble " + bpAddr + "\n")
        asmCode = self.read()
        
        #add the machine code to liustbox line by line
        i = 0
        for line in asmCode.split("\n"):
            if "dump" in line.lower() or "(gdb)" in line: continue
            self.topLevel.machine_table.insert(END, line)
            
            #mark the position as highlighted text in machine code 
            if bpAddr[2:] in line.split()[0]:
                self.topLevel.machine_table.select_set(i)
            i = i + 1

        self.topLevel.machine_table.update()

    '''
    Gets the line number from machine code and adds a breakpoint at the trigger point address
    steps through the machine code while changing the registers as required
    '''
    def triggerFault(self):

        self.connect()
        line = self.topLevel.machine_table.get(self.topLevel.machine_table.curselection()[0])
        bpAddr = line.split()[0]


        # ADD BreakPOint
        self.sendCommand("B *" + bpAddr)

        # Continue Code
        self.sendCommand("continue")

        
        #Del Current BP
        self.sendCommand("del")

        #ADD FeedBack BreakPoint
        self.sendCommand("B " + self.feedbackLine)

        self.regList = []
        for item in self.choices:
            if self.choices[item].get() == "1":
                print item , self.choices[item].get()
                self.regList.append(item)

        #print self.regList
        for index in range(0,len(self.topLevel.machine_table.curselection())):
            #Update REG Values
            self.updateRegs()

            self.sendCommand("info R")

            self.readGDB()

            #singleStepping
            self.printOutput("Stepping to next instruction")
            self.pluginProcess.stdin.write("si\n")
            response = self.read()
            self.printOutput(response)
            if "Program Received" in response: 
                self.printOutput("Program Ended\n Exiting Single Stepping")
                break

        self.checkFeedback()

    '''
    checks whether the program stopped at the feedback line after the glitch or not 
    declares the trigger case success or fail as per the outcome
    '''
    def checkFeedback(self):
        #Continue for feedback 
        self.pluginProcess.stdin.write("c\n")

        response = self.read()
        self.printOutput(response)

        '''
        check if the program stopped at the feedback line breakpoint
        '''
        if "Breakpoint 2" in response:
            self.topLevel.trig_fault_progress.create_oval(1,1,20,20, outline=black,fill=green,width=1)
            self.printOutput("SUCCESS Reached Feedback Line")
            return True
        else:
            self.topLevel.trig_fault_progress.create_oval(1,1,20,20, outline=black,fill=pink,width=1)
            self.printOutput("FAILED to reach FeedBack")
            self.connect()
            return False

    '''
    Applies the mask to all registers in the regList and applies new values to the required regs
    '''
    def updateRegs(self):
        #print self.regList
        for reg in self.regList:
            #print reg
            self.pluginProcess.stdin.write("info R " + reg + "\n")
            val = self.read()
            regVal = val.split()[2]

            newVal = str(mask(MASK_TO_APPLY, regVal))
            self.sendCommand("set $" + reg + "=" + newVal)

    '''
    executes all the triggers from list Faults and provides feedback for each trigger point 
    '''
    def executeXMLpoints(self):

        index = 1
        for item in self.faults:



            #change the circular indicator to yellow while executing the trigger
            self.topLevel.trig_fault_progress.create_oval(1,1,20,20, outline=black,fill=yellow,width=1)
            
            bp = item[0]

            self.printOutput("\n\n\nExecuting Fault {0} from XML at {1}\n\n".format(index, bp))


            self.connect()

            #check if BP is hex or str
            if bp[0:2] == "0x":
                self.sendCommand("B *" + bp)
            else: self.sendCommand("B " + bp)
            
            # Continue Code
            self.sendCommand("continue")

            #Del Current BP
            self.sendCommand("del")

            #ADD FeedBack BreakPoint
            self.sendCommand("B " + self.feedbackLine)


            #exectues all the register changes to be made at the given XML Point
            for trigger in item[1]:
                reg = trigger.reg

                if trigger.op == "const":
                    newVal = trigger.val
                    self.sendCommand("set $" + reg + "=" + newVal)
                    continue

                self.pluginProcess.stdin.write("info R " + reg + "\n")
                val = self.read()
                regVal = val.split()[2]

                newVal = str(mask(trigger.op, regVal, trigger.val))
                self.sendCommand("set $" + reg + "=" + newVal)


            self.sendCommand("info R")

            self.readGDB()

            flag=self.checkFeedback()
            
            #highlight the XML point as green or pink depending on result
            if flag:
            	self.topLevel.xml_table.tag_configure(item[0], background=green)
            else:
            	self.topLevel.xml_table.tag_configure(item[0], background=pink)

            self.sendCommand("info R")
            index = index + 1

    #Refreshes the values of registers and formats and displays the gdb response 
    def readReg(self):
        self.topLevel.reg_table.delete(*self.topLevel.reg_table.get_children())
        line = self.read()
        self.log = self.log + line + "\n"
        for text in line.split('\n')[:-1]:
            row = ""
            for word in text.split():
                row = "{0}{1:15}".format(row, word)
            self.topLevel.reg_table.insert('', END, values=row, tags=('font'))

    #Sends the given command to GDB and writes the response in the correct frame 
    def sendCommand(self, line):
    	self.pluginProcess.stdin.write(line + "\n")

    	if line == "info R" or line == "info r":
            self.log = self.log + "Reading reagister Value\n"
            self.readReg()
        else:
            self.printOutput(line)
            self.readGDB()


    #Reads the temp file written by GDB for output
    def read(self):
        time.sleep(0.1)
        self.tempf.seek(self.pointer)
        line  = self.tempf.read()
        self.pointer = self.tempf.tell()
        return line


    #reads from gdb and adds output to the Console in app
    def readGDB(self):
    	data = self.read()
        for line in data.split('\n'):
            self.printOutput(line)
        

    #Import XML File and populate the faults list
    def importXML(self, fileName):
        self.xmlFile = untangle.parse(fileName)
        self.populateFaults()

    #Import Source File
    def importSourceFile(self,fileName):
        self.cFile = fileName
        self.topLevel.machine_check.menu.delete(0, END)
        for item in self.choices:
            self.choices[item] = Variable()
            self.topLevel.machine_check.menu.add_checkbutton(label=item.upper(), variable=self.choices[item])



    #return Faults list
    def getFaults(self):
        return self.faults

def initModel(top):
    model = Model(top)
    return model




