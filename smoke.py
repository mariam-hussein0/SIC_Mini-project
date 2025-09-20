  GNU nano 7.2                                                                                    test_smoke.py                                                                                             
from gpiozero import DigitalInputDevice, PWMOutputDevice
from time import sleep

smoke_sensor = DigitalInputDevice(26)
buzzer = PWMOutputDevice(12)

freq = 200
step = 100

try:
    while True:
        if smoke_sensor.value == 1:
            print(f"Smoke detected! freq={freq} Hz")
            buzzer.frequency = freq
            buzzer.value = 0.9
            sleep(2)
            if freq <= 1000:
                freq += step
        else:
            print("No smoke")
            buzzer.off()
            freq = 200
            sleep(0.5)
except KeyboardInterrupt:
    buzzer.off()
    print("Program stopped")



