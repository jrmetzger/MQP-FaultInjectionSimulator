import sys 


'''
Recieves integer value of a register
The values are changed by the algorithm in the mask function 
and returned to the backend.py to set new register value

'''





def mask(operation, registerValue, opValue = None):

	
	resultVal = None

	flag = False
	val = None
	if registerValue[0:2] == "0x":
		val = int(registerValue,16)
		flag = True
	else:
		val = int(registerValue)

	#print "oldVal" , val
	#print operation, opValue
	if operation == "flipAlt": 
		resultVal = flipAlternateBit(val)
	elif operation == "add": 
		resultVal = addVal(val,int(opValue))
	elif operation == "sub": 
		resultVal = subVal(val,int(opValue))


	#print "newVal" , resultVal
	if flag:
		return hex(resultVal)

	return resultVal





def addVal(registerValue, opValue):
	return registerValue + opValue


def subVal(registerValue, opValue):
	return registerValue - opValue



def flipAlternateBit(val):

	newVal = []
	bnum = bin(val)
	#print bnum ,
	for i in range(bnum.find('b') + 1,len(bnum)):
		if i%2 == 0:
			newVal.append(bnum[i])
			continue

		if bnum[i] == '1':
			newVal.append('0')
		else:
			newVal.append('1')

	flipped = bnum[0:bnum.find('b') + 1] + ''.join(newVal)
	#print flipped
	return int(flipped, 2)