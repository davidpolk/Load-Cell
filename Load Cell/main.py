from hx711.hx711_pio import HX711
from machine import Pin
import math
import time
import utime
import select
import sys
import sdcard
import uos

startTimeMs = time.ticks_ms()

# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(13, machine.Pin.OUT)

# Intialize SPI peripheral (start with 1 MHz)
spi = machine.SPI(1,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(10),
                  mosi=machine.Pin(11),
                  miso=machine.Pin(12))


# Initialize SD card
try:
    sd = sdcard.SDCard(spi, cs)
    isSDconnected = True
except Exception as e:
    print("SD card not found or failed to initialize:", e)
    isSDconnected = False

# Mount filesystem
if isSDconnected:
    vfs = uos.VfsFat(sd)
    uos.mount(vfs, "/sd")



# uos.mkdir(datetime)

# Create an instance of a polling object 
poll_obj = select.poll()
# Register sys.stdin (standard input) for monitoring read events with priority 1
poll_obj.register(sys.stdin,1)
   
###  Record Button Variables  ###
# recLED = machine.Pin(10, machine.Pin.OUT)
# recBtn = machine.Pin(11, machine.Pin.IN, machine.Pin.PULL_UP)
# tareBtn = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)

###  Load Cell Variables  ###
pin_OUT = Pin(15, Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin(14, Pin.OUT)

hx711 = HX711(pin_SCK, pin_OUT, state_machine=0)

value = 0


# Record Button Variables
isRecording = False
# ledState = 1

#Get the current time
current_time = utime.localtime()
#Format the current time as "dd/mm/yyyy HH:MM"
datetime = "{}-{:02d}-{:02d}_{:02d}-{:02d}-{:02d}".format(current_time[0], current_time[1], current_time[2], current_time[3], current_time[4], current_time[5])
print(datetime)
fileCnt = 0
fileName = "/sd/" + str(datetime) + "/" + str(fileCnt)
file = None


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
    
def toggleRec():
    global ledState
    global isRecording
    global fileCnt
    global file
    global datetime
    
    # ledState = not ledState
    isRecording = not isRecording
    # recLED.value(ledState)
    
    if (isRecording and isSDconnected):
        fileCnt = fileCnt + 1
        fileName = "/sd/" + str(datetime) + "/" + str(fileCnt)
        file = open(str(fileName) + ".csv","a")
        print("Start Recording GUI " + str(fileCnt))
    
    elif (isRecording and isSDconnected == False):
        print("Start Recording GUI " + str(fileCnt))
        
    elif (isRecording == False and isSDconnected):
        file.close()
        print("Stop Recording GUI " + str(fileCnt))
    
    elif (isRecording == False and isSDconnected == False):
        print("Stop Recording GUI " + str(fileCnt))
    


def main():
    unit = 'g'
    isAcquiring = False
    
    
    # Load Cell Variables
    tareVal = 0
    resolution = 1
    
    # Record Button Variables
    global isRecordingstartTimeMs
    global ledState
    global file
    global datetime
    
    
    lastDebounceTime = 0  ## the last time the output pin was toggled
    debounceDelay = 50    ## the debounce time; increase if the output flickers
           ## the current state of the output pin
    buttonState = 0            ## the current reading from the input pin
    lastButtonState = 0  ## the previous reading from the input pin
    #recLED.value(ledState) 
 

    # Initial Tare
    hx711.tare()
    tareVal = hx711.read()
    # print("Scale Zeroed")
    

    # Weighing Loop
    while(True):
        valueSum = 0
        valueAvg = 0
        
    ### Get Commands From GUI ###
        if poll_obj.poll(0):
            # Read one character from sys.stdin
            command = sys.stdin.read(1)
            command = command.strip()
            print(command)  # Used as a confirmation response to GUI commands
            if command:
                if command == "r":
                    # Implement your command logic here, e.g., turn on an LED
                    toggleRec()
                        
                elif command == "t":
                    hx711.tare()
                    tareVal = hx711.read()
                    
                elif command == "u":
                    
                    if unit == 'g':
                        unit = 'N'
                        
                    elif unit == 'N':
                        unit = 'g'
                        
                elif command == "a":
                    isAcquiring = True
                    
                    while poll_obj.poll(0) == 0:
                        continue
                        # time.sleep_ms(1)
                        
                    datetime = sys.stdin.read(19)
                    datetime = datetime.strip()
                    #Get the current time
                    # current_time = utime.localtime()
                    #Format the current time as "dd/mm/yyyy HH:MM"
                    # datetime = "{}-{:02d}-{:02d}_{:02d}-{:02d}-{:02d}".format(current_time[0], current_time[1], current_time[2], current_time[3], current_time[4], current_time[5])
                    print(datetime)
                    
                    if isSDconnected:
                        uos.mkdir("/sd/" + datetime)
                    
                elif command == "x":
                    isAcquiring = False
                    
           
#     ### Check Record Button ###
#         
#         # read the state of the switch into a local variable:
#         reading = recBtn.value()
# 
#         # check to see if you just pressed the button
#         # (i.e. the input went from LOW to HIGH), and you've waited long enough
#         # since the last press to ignore any noise:
# 
#         # If the switch changed, due to noise or pressing:
#         if (reading != lastButtonState):
#             # reset the debouncing timer
#             lastDebounceTime = time.ticks_ms()
#         
# 
#         if ((time.ticks_ms() - lastDebounceTime) > debounceDelay):
#             # whatever the reading is at, it's been there for longer than the debounce
#             # delay, so take it as the actual current state:
# 
#             # if the button state has changed:
#             if (reading != buttonState):
#                 buttonState = reading
# 
#                 # only toggle the LED if the new button state is HIGH
#                 if (buttonState == 1):
#                     ledState =  not ledState
#                     isRecording = not isRecording
#                     #recLED.value(ledState)
#                     
#                     if (isRecording == True):
#                         fileCnt = fileCnt + 1
#                         fileName = "filename" + str(fileCnt)
#                         file.close()
#                         file = open(str(fileName) + ".csv","a")  
#                         print("Start Recording BTN " + str(fileCnt))
#                         
#                     else:
#                         file.close()
#                         print("Stop Recording BTN " + str(fileCnt))
                

        # set the LED:
        # recLED.value(ledState)

        # save the reading. Next time through the loop, it'll be the lastButtonState:
        #lastButtonState = reading
                
        
    ### Check Tare Button ###
#         if (tareBtn.value() == 0):
#             hx711.tare()
#             tareVal = hx711.read()
            # print("Scale Zeroed")
            
        
        if isAcquiring:
            ### Fing Average for resolution window; Used for data smoothing ###
            for i in range(resolution):
                valueRaw = 0
                valueRaw = hx711.read()
                valueSum = valueSum + valueRaw
                 
            valueAvg = valueSum / resolution
            value = (valueAvg - tareVal)/27000

            
            
            if unit == 'N':
                value = value * 0.00981
             
            timeMs = time.ticks_ms() - startTimeMs
            
            ### Format and Print ###
            value = math.floor(value*100000)/100000
            print('{},{}{}'.format(timeMs, value, unit))
        
            
            ### Write to File if recording  ###
            if (isRecording == True and isSDconnected):
                file.write(str(timeMs)+","+str(value)+","+str(unit)+"\n")


try:
    main()
except KeyboardInterrupt:
    print("Exiting...")

        

