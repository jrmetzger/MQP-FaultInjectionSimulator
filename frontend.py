#################################################

__author__ 	= "Jon Metzger, Maryann O'Connell, Himanjal Sharma"
__date__ 	= "01/09/18 - 02/22/18"
__copyright__ 	= "Copyright 2018, Major Qualifying Project"
__credits__ 	= "Vincent Chen, Andrew Tran, Mark Claypool"
__department__ 	= "Software Security"
__company__ 	= "NVidia"
__version__ 	= "1.0"
__status__ 	= "Development"

#################################################

import sys
from Tkinter import *
from tkFileDialog import askopenfile
from tkFileDialog import askopenfilename
import tkMessageBox as messagebox
import untangle
from subprocess import *
import subprocess
import tempfile
import time
import ttk
import tkFont
from backend import initModel
import os
import inspect

# ***** Variables *****

entity = None
top = None
sourceSelectedLine = None
selectReg = None
importXML = False
basenameSource = ""

# ***** Colors *****

lgrey = '#d9d9d9'
black = '#000000'
white = '#ffffff'
green = '#98FB98'
yellow = '#ffff00'
pink ='#ffa797'

buttonHeight = 30
buttonWidth = 150

# ***** Fonts *****

# for presentations purposes, size +2
font_app_title = "-family {Bitstream Vera Serif} -size 25 -weight bold -slant roman -underline 0 -overstrike 0"
font_app_button = "-family {DejaVu Sans} -size 13 -weight normal -slant roman -underline 0 -overstrike 0"
font_table_title = "-family {DejaVu Sans} -size 15 -weight normal -slant roman -underline 1 -overstrike 0"
font_table_list = "-family {DejaVu Sans} -size 13 -weight normal -slant roman -underline 0 -overstrike 0"

# ***** Functions *****

#################################################

### Machine Code Functions ###

'''
Function to call the backend to trigger the fault. 
This function is called from machine_triggerFault button.
'''
def triggerFault():
    runAppButtons("disabled")
    checkXML('disabled')
    faultProgress(yellow)
    entity.triggerFault()
    top.trig_fault_progress.update()
    runAppButtons("normal")
    checkXML('normal')

#################################################

### Source Code Functions ###

'''
Function when updating feedback to be used to trigger faults 
or execute breakpoints. This can be accessed through the Get Feedback 
button
'''
def getFeedback():
    global importXML
    lineNo = top.source_feedback_entry.get()
    if lineNo.isdigit() and int(lineNo) <= top.source_table.size() and int(lineNo) >0:
        top.source_feedback_entry.config(background=green)
        top.source_feedback_entry.update()
        entity.printOutput("Feedback selected at line " + lineNo)
        top.machine_triggerFault.configure(state='normal')
        entity.setFeedback(lineNo)
        checkXML('normal')
    else:
        top.source_feedback_entry.config(background=pink)
        entity.printOutput("ERROR: Input Valid Line No. between 1 and " + str(top.source_table.size()))
        top.source_feedback_entry.update()

'''
Similar function to the prior but passes through the 
enter key when line number is present.
'''
def enterKey_Feedback(event):
    getFeedback()
'''
When a line on the source code is selected, it passes to be updated on 
the feedback line. The line then highlights green to confirm feedback 
selection
'''
def onClick_sourcecode(event):
    global sourceSelectedLine
    w = top.source_table
    if not  w.curselection():
        return
    index = int(w.curselection()[0])
    value = w.get(index)
    top.trig_fault_progress.update()
    faultProgress("black")
    top.source_feedback_entry.config(background=green)
    top.source_feedback_entry.delete(0,END)
    top.source_feedback_entry.insert(0,index+1)
    entity.showAssemCode(index)

'''Function when opening the source file to be displayed. This can be 
found by going to Open Files > Source File
'''
def open_sourcecode():
    filenameC = askopenfilename(initialdir = "./documents", title="Select Source file", filetypes = ( ("c files","*.c"),("all files","*.*") ))
    if not filenameC:
        top.gdb_table.delete(0,END) 
        top.gdb_table.insert(END,entity.printOutput("ERROR: Not correct file type selected. Please select a Source file."))
        return
    global basenameSource
    basenameSource = os.path.basename(filenameC)
    entity.importSourceFile(filenameC)
    top.source_title.configure(text="Source Code : {" + basenameSource + "}")
    top.gdb_table.delete(0,END) 
    entity.printOutput("Connected < {0} > Successfully ... ".format(basenameSource))
    top.source_table.delete(0,END)
    with open (filenameC, "r") as myfile:
        strF = myfile.read()
        index = 0
        for line in strF.split('\n'):
            index = index + 1
            top.source_table.insert(END, "{0:10}{1}".format(str(index), line))
        myfile.close()
    initializeButtons()
    connectGDB()

#################################################

### XML Table Functions ###

'''
Add breakpoints from the XML file to the registers to ran against.
'''
def executeBreakpoint():
    runAppButtons("disabled")
    checkXML('disabled')
    for item in entity.getFaults():
        top.xml_table.tag_configure(item[0], background=white)
    top.xml_addBreak.configure(state='disabled')
    entity.printOutput("Executing Breakpoints")
    entity.executeXMLpoints()
    entity.printOutput("Breakpoints Added Successfully")
    runAppButtons("normal")
    checkXML('normal')

def checkXML(status):
	if importXML is True:
		top.xml_addBreak.configure(state=status)

'''
Function when importing the XML file to the table. This can be 
found in Open Files > XML File.
'''
def open_xmlfile():
    global importXML
    filenameXML = askopenfilename(initialdir = "./documents",title = "Select XML file",filetypes = (("xml files","*.xml"),("all files","*.*")))
    if ".xml" not in filenameXML:
        top.gdb_table.delete(0,END) 
        top.gdb_table.insert(END,entity.printOutput("ERROR: Not correct file type selected. Please select an XML file."))
        return
    entity.importXML(filenameXML)
    importXML = True
    basenameXML = os.path.basename(filenameXML)
    top.xml_title.configure(text="XML Table : {" + basenameXML +"}")
    entity.printOutput("Connected < {0} > Successfully ... ".format(basenameXML))
    top.xml_table.delete(*top.xml_table.get_children())
    if entity.feedbackLine is not None:
        top.xml_addBreak.configure(state='normal')
        
    i = 1   
    for item in entity.getFaults():
        trig_list = (i,item[0])
        top.xml_table.insert('', END, values=trig_list, tags=(item[0],'row', 'font'))
        for masks in item[1]:
            mask_list = ("- -", "- - - - - - - - - -", masks.reg, masks.op, masks.val)
            top.xml_table.insert('', END, values=mask_list, tags=('font'))
        i = i + 1

#################################################

### Register Table Functions ###

'''
Sends a command to backend to refresh the registers.
'''
def refreshRegisters():
    entity.sendCommand("info R")
    entity.sendCommand("Registers Refreshed")

'''
Updates the selected register with the input value. It then 
refreshes the registers (using the prior function) to update the 
values in the table.
'''
def updateRegisters():
    reg = selectReg
    w = top.reg_entry
    val = w.get()
    w.delete(0,END)
    entity.sendCommand("set $" + reg + "=" + val)
    refreshRegisters()

'''
Updates the registers when the enter key is pressed after 
inputting the new register value.
'''
def enterKey_Registers(event):
    updateRegisters()

'''
When clicking on a register line, it updates the selectReg 
variable for the user to update the value.
'''
def onClick_Registers(event):
    global selectReg
    w = top.reg_table
    sel = w.selection()
    selectReg = w.item(sel)['values'][0]
    top.reg_label.configure(text="Register: " + selectReg + "\tValue: ")
    top.reg_update.configure(state='normal')
    top.reg_entry.configure(state='normal')

#################################################

### GNU Debugger Functions ###

'''
Connects to the GDB server through the backend. For now, we connect 
to QEMU, in future versions this will be changed in order to connect 
to the Synopsis VDK.
'''
def connectGDB():
    entity.connect()
    entity.printOutput("Connected to GDB Server")
    refreshRegisters()

'''
When the user wants to clear the debugger logging output to clean 
up the display.
'''
def clearGDB():
    top.gdb_table.delete(0,END) 
    entity.printOutput("Clearing Successfully")

'''
Sends command on GDB entry to backend to be displayed on logging output.
'''
def getGDB():
    entity.sendCommand(top.gdb_entry.get())
    top.gdb_entry.delete(0,END)

'''
Sends command on GDB entry to backend when pressing the Enter Key.
'''
def enterKey_GDB(event):
    getGDB()

#################################################

### GUI Core Functions ###

'''
Function to create the gui and initialize the frames to make the application.
'''
def create_mainwindow():
    global val, w, root, top, entity, sourceSelectedLine
    root = Tk()
    top = mainwindow(root)
    entity = initModel(top)
    root.protocol("WM_DELETE_WINDOW", destroy_mainwindow)
    root.mainloop()
    sourceSelectedLine = None

'''
Function to exit and shut down the application.
'''
def destroy_mainwindow():
    global root, entity
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        entity.onClose()
        root.destroy()
        root = None

'''
When receiving the line number when clicking on a table, does not return an 
error when clicking somewhere else.
'''
def handle_click(event):
	if top.machine_table:
		return "break"
	if top.xml_table.identify_region(event.x, event.y) == "separator":
		return "break"   
	if top.reg_table.identify_region(event.x, event.y) == "separator":
		return "break"
	if top.gdb_table:
		return "break"  

'''
When scrolling on the tables, syncs to the scrollbar.
'''
def mouseWheelEvent(event):
    top.scrollBar.yview('scroll',event.delta, 'units')

'''
This function initializes objects when starting the application and 
importing the source code file.
'''
def initializeButtons():
    top.reg_refresh.configure(state='normal')
    top.source_feedback_button.configure(state='normal')
    top.source_feedback_entry.configure(state='normal')
    top.gdb_connect.configure(state='normal')
    top.gdb_clear.configure(state='normal')
    top.gdb_enter.configure(state='normal')
    top.gdb_entry.configure(state='normal')
    top.machine_check.configure(state='normal')
    top.source_table.bind("<<ListboxSelect>>", onClick_sourcecode)
    top.reg_table.bind("<<TreeviewSelect>>", onClick_Registers)

'''
This function is a helper to set the status on certain objects while 
running the application.
'''
def runAppButtons(status):
    top.machine_triggerFault.configure(state=status)
    top.source_feedback_button.configure(state=status)
    top.source_feedback_entry.configure(state=status)
    top.gdb_connect.configure(state=status)
    top.gdb_clear.configure(state=status)
    top.gdb_enter.configure(state=status)
    top.gdb_entry.configure(state=status)

'''
Set the progress of the application being ran on Trigger Fault and Executing Breakpoints.
'''
def faultProgress(color):
    top.trig_fault_progress.create_oval(1,1,20,20, outline=black,fill=color,width=1)

#################################################

### GUI Core Display ###


class mainwindow:
    '''
    Initializes the application with the following frames.
    '''
    def __init__(self, top):
        top.geometry("1500x1000")
        top.title("Fault Injection Simulator")
        top.configure(highlightcolor=black, background=white)

        self.title(top)
        self.menu(top)
        self.xml(top)
        self.machine(top)
        self.source(top)
        self.reg(top)
        self.gdb(top)

    '''
	Frame for the title and top frame.
    '''
    def title(self, top):

        self.title_frame = Frame(top)
        self.title_frame.configure(relief=GROOVE, borderwidth="1")
        self.title_frame.place(relx=0, rely=0, relheight=0.075, relwidth=1.00)
        
        self.title_label = Label(self.title_frame)
        self.title_label.configure(text="Fault Injection Simulator", font=font_app_title, anchor="center")
        self.title_label.place(relx=0, rely=0, relheight=1.00, relwidth=1.00)

        # self.hover_icon = Label(self.title_frame, text="HOVER")
        # self.hover_label = HoverInfo(self.title_frame, "author: Jon Metzger")

    '''
	Frame for the machine code table. This is where the user will 
	trigger faults and set registers to run against.
    '''
    def machine(self, top):

        self.machine_frame = Frame(top)
        self.machine_frame.configure(relief=GROOVE, borderwidth="1")
        self.machine_frame.place(relx=0, rely=0.075, relheight=0.4, relwidth=0.45)

        self.machine_title = Label(self.machine_frame)
        self.machine_title.configure(text="Machine Code", font=font_table_title, anchor=NW)
        self.machine_title.place(relx=0.01, rely=0.02, relheight=0.2, relwidth=0.75)

        self.machine_check = Menubutton(self.machine_frame, text="Select Registers", font=font_app_button, relief=RAISED, state='disabled')
        self.machine_check.menu = Menu(self.machine_check, tearoff=0)
        self.machine_check["menu"]=self.machine_check.menu
        self.machine_check.place(relx=0.75, rely=0.01, height=buttonHeight, width=buttonWidth, anchor=NE)

        self.machine_triggerFault = Button(self.machine_frame)
        self.machine_triggerFault.configure(text="Trigger Fault", font=font_app_button, state='disabled', command=triggerFault)
        self.machine_triggerFault.place(relx=0.99, rely=0.01, height=buttonHeight, width=buttonWidth, anchor=NE)

        self.machine_table = Listbox(self.machine_frame)
        self.machine_table.configure(relief=RIDGE, font=font_table_list, selectmode=EXTENDED)
        self.machine_table.place(relx=0.01, rely=0.09, relheight=0.89, relwidth=0.98)
        self.machine_table.insert(END,"Select a Source Line to View Machine Code")
        self.machine_table_scrollBar = ttk.Scrollbar(self.machine_table, orient="vertical")
        self.machine_table_scrollBar.config(command=self.machine_table.yview)
        self.machine_table_scrollBar.pack(side="right", fill="y")
        self.machine_table.config(yscrollcommand=self.machine_table_scrollBar.set)
        self.machine_table.bind("<MouseWheel>", mouseWheelEvent)

    '''
	Frame for the source code table. This is where the user will 
	select the feedback for the trigger to end at.
    '''
    def source(self, top):

        self.source_frame = Frame(top)
        self.source_frame.configure(relief=GROOVE, borderwidth="1")
        self.source_frame.place(relx=0, rely=0.475, relheight=0.525, relwidth=0.45)

        self.source_title = Label(self.source_frame)
        self.source_title.configure(text="Source Code", font=font_table_title, anchor=NW)
        self.source_title.place(relx=0.01, rely=0.02, relheight=0.2, relwidth=0.75)

        self.source_feedback_label = Label(self.source_frame)
        self.source_feedback_label.configure(text="Line No.", font=font_app_button)
        self.source_feedback_label.place(relx=0.5, rely=0.01, height=30, width=150)

        self.source_feedback_entry = Entry(self.source_frame)
        self.source_feedback_entry.configure(relief=RIDGE, font=font_table_list, background=white, state='disabled')
        self.source_feedback_entry.bind('<Return>', enterKey_Feedback)
        self.source_feedback_entry.place(relx=0.66, rely=0.01, height=30, width=60)
        
        self.source_feedback_button = Button(self.source_frame)
        self.source_feedback_button.configure(text="Update Feedback", font=font_app_button, state='disabled', command=getFeedback)
        self.source_feedback_button.place(relx=0.99, rely=0.01, height=buttonHeight, width=buttonWidth+10, anchor=NE)
        
        self.source_table = Listbox(self.source_frame)
        self.source_table.configure(relief=RIDGE, font=font_table_list, selectbackground=lgrey)
        self.source_table.place(relx=0.01, rely=0.075, relheight=0.91, relwidth=0.98)
        self.source_table.insert(END,"Select { Import Files > Source } to view")
        self.source_table_scrollBar = ttk.Scrollbar(self.source_table, orient="vertical")
        self.source_table_scrollBar.config(command=self.source_table.yview)
        self.source_table_scrollBar.pack(side="right", fill="y")
        self.source_table.config(yscrollcommand=self.source_table_scrollBar.set)
        self.source_table.bind("<MouseWheel>", mouseWheelEvent)
    
    '''
    Frame for the xml table. This where the user will execute the breakpoints 
    to run against the trigger of faults to test for glitches in the system.
    '''
    def xml(self, top):

        self.xml_frame = Frame(top)
        self.xml_frame.configure(relief=GROOVE, borderwidth="1")
        self.xml_frame.place(relx=0.45, rely=0.075, relheight=0.4, relwidth=0.32)

        self.xml_title = Label(self.xml_frame)
        self.xml_title.configure(text="XML Table", font=font_table_title, anchor=NW)
        self.xml_title.place(relx=0.01, rely=0.02, relheight=0.2, relwidth=0.75)

        self.xml_addBreak = Button(self.xml_frame)
        self.xml_addBreak.configure(text="Execute Breakpoints", font=font_app_button, state='disabled', command=executeBreakpoint)
        self.xml_addBreak.place(relx=0.99, rely=0.01, height=buttonHeight, width=buttonWidth+50, anchor=NE)

        header = ["#","Address","Register","Operation","Value"]
       	self.xml_table = ttk.Treeview(self.xml_frame,columns=header, show="headings", selectmode='none')
       	self.xml_table.place(relx=0.01, rely=0.09, relheight=0.89, relwidth=0.98)
        self.xml_table.tag_configure('font', font=font_table_list)
        self.xml_table_scrollBar = ttk.Scrollbar(self.xml_table, orient="vertical", command=self.xml_table.yview)
        self.xml_table_scrollBar.pack(side="right", fill="y")
       	self.xml_table.configure(yscrollcommand=self.xml_table_scrollBar.set)
        #self.xml_table.bind('<Button-1>', handle_click)
       	self.xml_table.column('#1', width=10)
        self.xml_table.column('#2', width=100)
        self.xml_table.column('#3', width=75)
        self.xml_table.column('#4', width=75)
        self.xml_table.column('#5', width=100)
       	for col in header:
       		self.xml_table.heading(col, text=col.title())
		
    '''
	Frame to hold the registers. This is updated when imported the source file, 
	executing the breakpoints, or updating and refreshing the registers manually.
    '''
    def reg(self, top):

        self.reg_frame = Frame(top)
        self.reg_frame.configure(relief=GROOVE, borderwidth="1")
        self.reg_frame.place(relx=0.77, rely=0.075, relheight=0.4, relwidth=0.23)

        self.reg_title = Label(self.reg_frame)
        self.reg_title.configure(text="Register Table", font=font_table_title, anchor=NW)
        self.reg_title.place(relx=0.01, rely=0.02, relheight=0.2, relwidth=0.5)

        self.reg_refresh = Button(self.reg_frame)
        self.reg_refresh.configure(text="Refresh", font=font_app_button, state='disabled', command=refreshRegisters)
        self.reg_refresh.place(relx=0.99, rely=0.01, height=buttonHeight, width=buttonWidth/2, anchor=NE)

        header = ["Name","Address","Value"]
       	self.reg_table = ttk.Treeview(self.reg_frame, columns=header, show="headings")
       	self.reg_table.place(relx=0.01, rely=0.0925, relheight=0.8, relwidth=0.98)
        self.reg_table.tag_configure('font', font=font_table_list)
        self.reg_table_scrollBar = ttk.Scrollbar(self.reg_table, orient="vertical", command=self.reg_table.yview)
        self.reg_table_scrollBar.pack(side="right", fill="y")
       	self.reg_table.configure(yscrollcommand=self.reg_table_scrollBar.set)
        #self.reg_table.bind('<Button-1>', handle_click)
        self.reg_table.column('#1', width=10)
        self.reg_table.column('#2', width=100)
        self.reg_table.column('#3', width=100)
       	for col in header:
       		self.reg_table.heading(col, text=col.title())
       	
        self.reg_label = Label(self.reg_frame)
        self.reg_label.configure(text="Select a Register:", font=font_app_button, anchor=NW)
        self.reg_label.place(relx=0.01, rely=0.925, relheight=0.05, width=250)
        
        self.reg_entry = Entry(self.reg_frame)
        self.reg_entry.configure(relief=RIDGE, font=font_table_list, background=white, state='disabled')
        self.reg_entry.place(relx=0.75, rely=0.9125, relheight=0.075, width=75, anchor=NE)
        self.reg_entry.bind('<Return>', enterKey_Registers)

        self.reg_update = Button(self.reg_frame)
        self.reg_update.configure(text="Update", font=font_app_button, state='disabled', command=updateRegisters)
        self.reg_update.place(relx=0.99, rely=0.9125, height=buttonHeight, width=buttonWidth/2, anchor=NE)

    '''
	Frame for the GNU Debugger Output. The user can clear the GDB output, 
	reconnect (or initially connect) to the GDB Server, and manually input commands.
    '''
    def gdb(self, top):

        self.gdb_frame = Frame(top)
        self.gdb_frame.configure(relief=GROOVE, borderwidth="1")
        self.gdb_frame.place(relx=0.45, rely=0.475, relheight=0.525, relwidth=0.55)

        self.gdb_title = Label(self.gdb_frame)
        self.gdb_title.configure(text="GNU Debugger", font=font_table_title, anchor=NW)
        self.gdb_title.place(relx=0.01, rely=0.02, relheight=0.2, relwidth=0.2)

        self.trig_fault_progress = Canvas(self.gdb_frame)
        self.trig_fault_progress.create_oval(1,1,20,20, outline=black,fill=black,width=2)
        self.trig_fault_progress.place(relx=0.2, rely=0.02, relheight=0.075, relwidth=0.05)

        self.gdb_clear = Button(self.gdb_frame)
        self.gdb_clear.configure(text="Clear GDB", font=font_app_button, state='disabled', command=clearGDB)
        self.gdb_clear.place(relx=0.73, rely=0.01, height=buttonHeight, width=buttonWidth, anchor=NE)

        self.gdb_connect = Button(self.gdb_frame)
        self.gdb_connect.configure(text="Connect to GDB Server", font=font_app_button, state='disabled', command=connectGDB)
        self.gdb_connect.place(relx=0.99, rely=0.01, height=buttonHeight, width=buttonWidth+75, anchor=NE)

        self.gdb_table = Listbox(self.gdb_frame)
        self.gdb_table.configure(relief=RIDGE, font=font_table_list, selectmode='none')
        self.gdb_table.exportselection = False
        self.gdb_table.place(relx=0.01, rely=0.075, relheight=0.85, relwidth=0.98)
        self.gdb_table.insert(END,"Connect to Server to Debug")
        self.gdb_table_scrollBar = ttk.Scrollbar(self.gdb_table, orient="vertical")
        self.gdb_table_scrollBar.config(command=self.gdb_table.yview)
        self.gdb_table_scrollBar.pack(side="right", fill="y")
        self.gdb_table.config(yscrollcommand=self.gdb_table_scrollBar.set)
        self.gdb_table.bind('<Button-1>', handle_click)
        self.gdb_table.bind("<MouseWheel>", mouseWheelEvent)

        self.gdb_label = Label(self.gdb_frame)
        self.gdb_label.configure(text="(gdb)", font=font_table_list, anchor=NW)
        self.gdb_label.place(relx=0.01, rely=0.94, relheight=0.05, relwidth=0.1)

        self.gdb_entry = Entry(self.gdb_frame)
        self.gdb_entry.configure(relief=RIDGE, font=font_table_list, background=white, state='disabled')
        self.gdb_entry.bind('<Return>', enterKey_GDB)
        self.gdb_entry.place(relx=0.075, rely=0.94, relheight=0.05, relwidth=0.8)

        self.gdb_enter = Button(self.gdb_frame)
        self.gdb_enter.configure(text="Enter", font=font_app_button, state="disabled", command=getGDB)
        self.gdb_enter.place(relx=0.99, rely=0.935, height=buttonHeight, width=buttonWidth/2, anchor=NE)

    '''
	Menu bar on the top to Open Files (Source and XML) and Exit the Application.
    '''
    def menu(self, top):
    	self.menuBar = Menu(top)
        
        self.filemenu = Menu(self.menuBar)
        self.menuBar.add_cascade(label="Import Files", menu=self.filemenu)
    	self.filemenu.add_command(label="Source",command=open_sourcecode)
    	self.filemenu.add_command(label="XML",command=open_xmlfile)
    	
    	# self.logmenu = Menu(self.menuBar)
    	# self.menuBar.add_cascade(label="Log Files", menu=self.logmenu)

    	self.menuBar.add_command(label="Exit",command=destroy_mainwindow)
    	top.config(menu=self.menuBar)

if __name__ == '__main__':
    create_mainwindow()


# ***** EOF *****
