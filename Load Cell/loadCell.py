from hx711.hx711_pio import HX711
from machine import Pin
import math

fileCnt = 0
tareVal = 0
resolution = 1
isRecording = False
measurments = []

recLED = machine.Pin(10, machine.Pin.OUT)
recBtn = machine.Pin(11, machine.Pin.IN, machine.Pin.PULL_UP)
pin_OUT = Pin(12, Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin(13, Pin.OUT)
tareBtn = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)

hx711 = HX711(pin_SCK, pin_OUT, state_machine=0)


    
### MAIN ###

# Initial Tare
hx711.tare()
tareVal = hx711.read()
print("Scale Zeroed")

# Weighing Loop
while(True):
    valueSum = 0
    valueAvg = 0
    
    if (recBtn.value() == 0):
        if (isRecording == False):
            isRecording = True
            recLED.value(True)
            print("Start Recording")
            
        else:
            isRecording = False
            recLED.value(False)
            fileCnt = fileCnt + 1
            fileName = "filename" + str(fileCnt)
            
            file = open(str(fileName) + ".csv","w")
            for j in measurments:
                file.write(str(j)+"\n")
                
            measurments = []
            print("Stop Recording " + str(fileCnt))
            
    
    
    if (tareBtn.value() == 0):
        hx711.tare()
        tareVal = hx711.read()
        print("Scale Zeroed")
        
    
    ## Fing Average for resolution window; Used for data smoothing
    for i in range(resolution):
        valueRaw = 0
        valueRaw = hx711.read()
        valueSum = valueSum + valueRaw
        
    valueAvg = valueSum / resolution
    value = (valueAvg - tareVal)/213.25
    
    ## Format and Print
    value = math.floor(value*100)/100
    print('{} g'.format(value))
    
    if (isRecording == True):
        measurments.append(value)
        
