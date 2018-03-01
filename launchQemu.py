from subprocess import *
import subprocess






def launchServer(file, portNo):
	subprocess.call("arm-linux-gnueabi-gcc -g {0} -o {1}-arm -static".format(file, file.split('.')[0]) , shell=True, stdout=subprocess.PIPE)
	subprocess.call("fuser -n tcp -k {0}".format(portNo), shell=True,stdout=subprocess.PIPE)
	qemuProcess = Popen("qemu-arm -singlestep -g {0} {1}-arm".format(portNo, file.split('.')[0]), shell=True)