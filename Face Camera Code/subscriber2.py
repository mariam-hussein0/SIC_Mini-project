import cv2
import time
import json
import paho.mqtt.client as mqtt

# --- Local Broker (laptop) to receive Pi distance data ---
LOCAL_BROKER = "192.168.137.202"   # your laptop IP
LOCAL_TOPIC = "sensor/distance"

# --- Public Broker (to send data to your friend) ---
PUBLIC_BROKER = "test.mosquitto.org"
PUBLIC_PORT = 1883
PUBLIC_TOPIC = "mall/sensors/data"

cap = None          # camera object
recording = False   # state flag
people_count = 0    # total number of detected faces

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# ✅ Face detection function
def detect_and_draw_face(frame):
    global people_count
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    eq_frame = cv2.equalizeHist(gray_frame)
    faces = face_cascade.detectMultiScale(eq_frame, scaleFactor=1.3, minNeighbors=5)

    face_detected = False
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(frame, 'Face Detected!', (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
        face_detected = True

    if face_detected:
        people_count += 1

    return frame, face_detected

# ✅ Public MQTT client (publisher)
pub_client = mqtt.Client(client_id="LaptopPublisher01")
pub_client.connect(PUBLIC_BROKER, PUBLIC_PORT, 60)

# ✅ Local MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to local broker")
        client.subscribe(LOCAL_TOPIC)
        print(f"📡 Subscribed to topic: {LOCAL_TOPIC}")
    else:
        print("❌ Failed to connect to local broker, return code", rc)

def on_message(client, userdata, msg):
    global cap, recording, last_distance
    try:
        distance = float(msg.payload.decode())
        last_distance = distance
        print(f"📏 Distance received: {distance:.2f} cm")

        if distance < 100:  # OPEN camera
            if not recording:
                print("🎥 Starting camera...")
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    print("❌ Error opening camera")
                    return
                recording = True

        elif distance > 100:  # CLOSE camera immediately
            if recording:
                print("🛑 Stopping camera (distance > 100)...")
                cap.release()
                cv2.destroyAllWindows()
                recording = False

        # Always publish distance (even if no camera open)
        data = {
            "people_count": people_count,
            "distance": distance,
            "face_detected": "UNKNOWN"  # updated later if camera is running
        }
        pub_client.publish(PUBLIC_TOPIC, json.dumps(data))
        print(f"📤 Published initial data: {data}")

    except Exception as e:
        print("⚠️ Error in on_message:", e)

# ✅ Local MQTT setup (subscriber for Pi data)
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message
client.connect(LOCAL_BROKER, 1883, 60)

print("🚀 Waiting for messages... (Press Ctrl+C to stop)")
client.loop_start()

# ✅ Main loop for camera frames
try:
    while True:
        if recording and cap is not None:
            ret, frame = cap.read()
            if ret:
                frame, face_detected = detect_and_draw_face(frame)
                cv2.imshow("Face Detection", frame)

                # Publish with face detection info
                data = {
                    "people_count": people_count,
                    "distance": last_distance,
                    "face_detected": "YES" if face_detected else "NO"
                }
                pub_client.publish(PUBLIC_TOPIC, json.dumps(data))
                print(f"📤 Published live data: {data}")

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        else:
            time.sleep(0.1)
except KeyboardInterrupt:
    print("\n🛑 Interrupted by user")

# ✅ Cleanup
if cap:
    cap.release()
cv2.destroyAllWindows()
client.loop_stop()
client.disconnect()
pub_client.disconnect()
