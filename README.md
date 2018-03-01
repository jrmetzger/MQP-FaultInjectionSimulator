# Fault Injection Simulator

For our Major Qualifying Project at WPI, we created an application to automate fault injection when there is a glitch. to collect information on a low level. This enabled us to then see if glitching would occur and the registers stay the same.

## Authors
* Jon Metzger
* Maryann O'Connell
* Himanjal Sharma

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Files
* run.sh
  * script to run program
* frontend.py
  * design of the application
* backend.py
  * functionality of the application
* mask.py
  * masking the values of registers
* launchQemu.py
  * connect to the server (can be later changed to Synopsis VDK)
* documents
  * files to import

### Running the Application
```
$ bash run.py
```

### Running the Fault Injection Simulator

1. Open the Fault Injection Simulator
2. Open Files > Source File. Select your file (test.c) to test for glitching.
3. Open FIles > XML File. Select your file (breakpoint_data.xml) to set up breakpoints.
4. XML Table - (optional) Click on Execute Breakpoints to see if the given address are valid or invalid. The progress is given in the GNU Debugger.
5. Register Table - (optional) 
 a. Click on a Register line to update the value manually
 b. Refresh the Registers manually
6. Source Code - Click on a line (line 31) or input on the Line No. field and Update Feedback.
7. Machine Code - (optional) Click on Machine Code line(s) to test the trigger. The progress is given in the GNU Debugger.
8. Select Registers that you wish to test on
9. Trigger Fault to start the test


## Built With

* [PAGE]() - gui development
* [Sublime 2]() - text editor
* [Ubuntu]() - operating system
* [ChipWhisperer]() - information from chips to feed into the application

## History

## Version 1.0
* Final Submission for Project
* Colors
* Select which registers to trigger on
* Trigger Fault and Execute Breakpoints Progress

### Version 0.6
* Update Registers manually
* Feedback
* mask register values
* listbox columns

### Version 0.5
* Highlight source code and mirror on machine code
* Trigger Fault goes through lines (TODO)
* Refresh button for registers
* Redesign

### Version 0.4
* View Machine Code
* Print selected Program lines
* Trigger Fault Button
* Command Line Enter Key/Button. Disable until Connected to server

### Version 0.3
* Disable buttons before step is needed
* Set registers
* info R and info B
* Registers read on GUI

### Version 0.2
* Upload C file
* Seperated GUI and Backend
* Output on GDB from C file
* Update User Interface

### Version 0.1
* User Interface
* Title, Open Buttons
* XML Table, Registers, GDB Output, Breakpoints
* Open XML insert into table and prints file name

## License

This project was completed under WPI and NVIDIA and cannot be used without permission from the authors.

## Acknowledgments

* NVIDIA - Vincent Chen and Andrew Tran
* WPI - Professor Claypool
* Oakwood Apartments
