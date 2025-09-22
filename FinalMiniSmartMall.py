import threading
from time import sleep
from gpiozero import DigitalInputDevice, PWMOutputDevice, DigitalOutputDevice, DistanceSensor
import board
import adafruit_dht
import BlynkLib
import signal
import sys

BLYNK_AUTH = "GELgjXwSmWjTLIT9seEj22PwwA2DvH47"
blynk = BlynkLib.Blynk(BLYNK_AUTH, server="blynk.cloud", port=80)

running = True

def signal_handler(sig, frame):
    global running
    running = False
    print("\n[INFO] Stopping program...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Smoke sensor thread
def smoke_sensor_thread():
    smoke_sensor = DigitalInputDevice(26)
    buzzer = PWMOutputDevice(12)
    buzzer.frequency = 500
    while running:
        if smoke_sensor.value == 1:
            buzzer.value = 0.8
            blynk.virtual_write(10, 500)
        else:
            buzzer.off()
            blynk.virtual_write(10, 0)
        sleep(1)

# DHT11 + relay thread
def dht11_thread():
    dhtDevice = adafruit_dht.DHT11(board.D25)
    relay = DigitalOutputDevice(17)
    while running:
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        if temperature_c is not None and humidity is not None:
            blynk.virtual_write(7, temperature_c)
            blynk.virtual_write(6, humidity)
            if temperature_c > 20:
                relay.on()
                blynk.virtual_write(12, "ON")
            else:
                relay.off()
                blynk.virtual_write(12, "OFF")
        sleep(2)

# Ultrasonic sensor thread
def ultrasonic_thread():
    sensor = DistanceSensor(echo=24, trigger=23)
    while running:
        distance = sensor.distance * 100
        if 2 <= distance <= 400:
            blynk.virtual_write(5, distance)
        sleep(1)

if __name__ == "__main__":
    t1 = threading.Thread(target=smoke_sensor_thread)
    t2 = threading.Thread(target=dht11_thread)
    t3 = threading.Thread(target=ultrasonic_thread)

    t1.start()
    t2.start()
    t3.start()

    # Main loop for Blynk
    while running:
        blynk.run()
        sleep(0.1)

    t1.join()
    t2.join()
    t3.join()
