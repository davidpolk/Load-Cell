import serial
import threading
import time
import random
import tkinter as tk
from itertools import count

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# open a serial connection
serialPico = serial.Serial("COM3", 115200)

# Command to send
command = "led_on"

plt.style.use('fivethirtyeight')
# values for first graph
x_vals = []
y_vals = []

index = count()
unit = 'g'
new_unit = 'g'

latest_serial_value = None

isRecording = True



def read_serial_data():
    global latest_serial_value
    while True:
        if serialPico.in_waiting > 0:
            try:
                # Read a line from the serial port
                latest_serial_value = serialPico.readline().decode('utf-8').strip()
                # Update the latest value if data was read successfully
                latest_serial_value = serialPico
            except Exception as e:
                print(f"Error reading serial data: {e}")
        time.sleep(0.01)  # Small delay to prevent busy-waiting

# Create a thread to continuously read serial data in the background
serial_thread = threading.Thread(target=read_serial_data, daemon=True)
serial_thread.start()

def animate(i):
    serialPico.flush()
    data = serialPico.readline()

    if latest_serial_value is not None:
        data = data.decode('utf-8').strip()
        value_str = data[:-1]  # Optional: adjust this based on your data
        try:
            value = float(value_str)
        except ValueError:
            return  # Ignore bad data

        measurment_label.config(text=value_str)

        x_vals.append(next(index))
        y_vals.append(value)

        if len(x_vals) > 100:
            x_vals.pop(0)
            y_vals.pop(0)

        # Update the plot line instead of clearing
        line.set_data(x_vals, y_vals)

        # Dynamically adjust x-axis if needed
        ax1.set_xlim(max(0, x_vals[0]), x_vals[-1])


    
def recordBtn_click():
    global isRecording
    print(f"Record {isRecording}")
    isRecording = not isRecording
    command = "r"
    serialPico.write(command.encode('utf-8'))

def tareBtn_click():
    print(f"Tare")
    command = "t"
    serialPico.write(command.encode('utf-8'))

def unitBtn_click():
    print(f"Unit")

# Create GUI
root = tk.Tk()
label = tk.Label(root, text="Realtime Animated Graphs").grid(column=0, row=0)


# Create Plot
canvas = FigureCanvasTkAgg(plt.gcf(), master=root)
canvas.get_tk_widget().grid(row=1, column=0)
ax1 = plt.gcf().subplots(1, 1)
line, = ax1.plot([], [], lw=2)
ax1.set_ylim(-1, 100)
ax1.set_xlim(0, 100) 

# Variables used to populate plot
x_vals = []
y_vals = []
index = count()

# Create Frames for bottom portion of gui
bottom_frame = tk.Frame(root)
right_frame = tk.Frame(root)

# Create Label to show current measurment
measurment_label = tk.Label(right_frame, text="0.0")
unit_label = tk.Label(right_frame, text=unit)

# Create three buttons
record_button = tk.Button(bottom_frame, text="Record", command=recordBtn_click)
tare_button = tk.Button(bottom_frame, text="Tare", command=tareBtn_click)
unit_button = tk.Button(bottom_frame, text="Unit", command=unitBtn_click)

## Layout ##
bottom_frame.grid(row=2, column=0)
right_frame.grid(row=1, column=1)

# Pack the labels in bottom-right frame
measurment_label.grid(row=0, column=0)
unit_label.grid(row=0, column=1)

# Pack the buttons horizontally in bottom-left frame
record_button.grid(row=0, column=0)
tare_button.grid(row=0, column=1)
unit_button.grid(row=0, column=2)

# Handles Plot Animation
ani = FuncAnimation(plt.gcf(), animate, interval=0.5, blit=False)

tk.mainloop()

