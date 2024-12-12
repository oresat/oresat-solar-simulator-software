import serial

port = 'COM4'  # Your port may vary (e.g., /dev/ttyUSB0 on Linux)
baudrate = 115200

ser = serial.Serial(port, baudrate, timeout=1)

while True:
    # Send data to Pico
    ser.write(b"Set light intensity to 50\n")

    # Read data from Pico
    line = ser.readline().decode().strip()
    if line:
        print(f"Received from Pico: {line}")
