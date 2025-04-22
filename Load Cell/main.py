from hx711.hx711_pio import HX711
from machine import Pin
import math
import time
import utime
import select
import sys

# Create an instance of a polling object 
poll_obj = select.poll()
# Register sys.stdin (standard input) for monitoring read events with priority 1
poll_obj.register(sys.stdin,1)
   
###  Record Button Variables  ###
recLED = machine.Pin(10, machine.Pin.OUT)
recBtn = machine.Pin(11, machine.Pin.IN, machine.Pin.PULL_UP)

###  Load Cell Variables  ###
pin_OUT = Pin(12, Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin(13, Pin.OUT)
tareBtn = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)
hx711 = HX711(pin_SCK, pin_OUT, state_machine=0)

value = 0

# Record Button Variables
isRecording = True


def display_digit(digit):
    # Get the pattern for the digit
    pattern = patterns[digit]
    
    # Set each segment to the correct state
    for i in range(8):
        pins[i].value(pattern[i])
    
    # Turn on the display
    display.value(0)
    
    # Turn off the display
    display.value(1)
    


def main():
    
    # File Variables 
    fileCnt = 0
    
    # Load Cell Variables
    tareVal = 0
    resolution = 1
    
    # Record Button Variables
    global isRecording
    
    
    lastDebounceTime = 0  ## the last time the output pin was toggled
    debounceDelay = 50    ## the debounce time; increase if the output flickers
    ledState = 0        ## the current state of the output pin
    buttonState = 0            ## the current reading from the input pin
    lastButtonState = 0  ## the previous reading from the input pin
    recLED.value(ledState) 
 

    # Initial Tare
    hx711.tare()
    tareVal = hx711.read()
    # print("Scale Zeroed")
    
    fileName = "filename0"
    file = open(str(fileName) + ".csv","a")

    # Weighing Loop
    while(True):
        valueSum = 0
        valueAvg = 0
        
    ### Get Commands From GUI ###
        if poll_obj.poll(0):
            # Read one character from sys.stdin
            command = sys.stdin.read(1)
            command = command.strip()
            print(command)
            if command:
                if command == "r":
                    # Implement your command logic here, e.g., turn on an LED
                    ledState = not ledState
                    isRecording = not isRecording
                    recLED.value(True)
                    fileCnt = fileCnt + 1
                    fileName = "filename" + str(fileCnt)
                    file.close()
                    file = open(str(fileName) + ".csv","a")
                        
                elif command == "t":
                    hx711.tare()
                    tareVal = hx711.read()
                    
           
    ### Check Record Button ###
        
        # read the state of the switch into a local variable:
        reading = recBtn.value()

        # check to see if you just pressed the button
        # (i.e. the input went from LOW to HIGH), and you've waited long enough
        # since the last press to ignore any noise:

        # If the switch changed, due to noise or pressing:
        if (reading != lastButtonState):
            # reset the debouncing timer
            lastDebounceTime = time.ticks_ms()
        

        if ((time.ticks_ms() - lastDebounceTime) > debounceDelay):
            # whatever the reading is at, it's been there for longer than the debounce
            # delay, so take it as the actual current state:

            # if the button state has changed:
            if (reading != buttonState):
                buttonState = reading

                # only toggle the LED if the new button state is HIGH
                if (buttonState == 1):
                    ledState = ~ledState
                    if (isRecording == False):
                        isRecording = True
                        recLED.value(True)
                        # print("Start Recording")
                        
                    else:
                        isRecording = False
                        recLED.value(False)
                        fileCnt = fileCnt + 1
                        fileName = "filename" + str(fileCnt)
                        file.close()
                        file = open(str(fileName) + ".csv","a")  
                        # print("Stop Recording " + str(fileCnt))
                

        # set the LED:
        recLED.value(ledState)

        # save the reading. Next time through the loop, it'll be the lastButtonState:
        lastButtonState = reading
                
        
    ### Check Tare Button ###
        if (tareBtn.value() == 0):
            hx711.tare()
            tareVal = hx711.read()
            # print("Scale Zeroed")
            
        
    ### Fing Average for resolution window; Used for data smoothing ###
        for i in range(resolution):
            valueRaw = 0
            valueRaw = hx711.read()
            valueSum = valueSum + valueRaw
             
        valueAvg = valueSum / resolution
        value = (valueAvg - tareVal)/18000
         
    ### Format and Print ###
        value = math.floor(value*100)/100
        print('{} g'.format(value))
        
    
        if (isRecording == True):
            file.write(str(value)+"\n")


try:
    main()
except KeyboardInterrupt:
    print("Exiting...")

        