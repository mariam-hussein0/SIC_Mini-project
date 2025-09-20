import paho.mqtt.client as mqtt
import json
import time
import random  # simulating data to test the mobile application

# --- MQTT Broker Details ---
BROKER = "test.mosquitto.org"   # public broker
PORT = 1883
TOPIC = "mall/sensors/data"
CLIENT_ID = "PiPublisher01"

# --- Connect to Broker ---
client = mqtt.Client(client_id=CLIENT_ID)
client.connect(BROKER, PORT, 60)

# --- Counter for number of people detected ---
people_count = 0

while True:
    # Simulate face detection (random for now)
    face_detected = random.choice([True, False])

    if face_detected:
        people_count += 1  # increase counter when a new person is detected

    # Example data packet
    data = {
        "people_count": people_count,
        "distance": random.randint(50, 150),
        "face_detected": "YES" if face_detected else "NO"
    }

    # Convert to JSON string
    payload = json.dumps(data)

    # Publish to topic
    client.publish(TOPIC, payload)
    print("Published:", payload)

    time.sleep(5)  # wait 5 seconds before sending again

