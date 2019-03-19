from serial import Serial

serial = Serial('/dev/serial0', 9600)

while True:
    try:
        print(serial.readline())
    finally:
        pass
