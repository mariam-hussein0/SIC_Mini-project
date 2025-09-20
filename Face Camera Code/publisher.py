import cv2
import paho.mqtt.client as mqtt

# MQTT settings
BROKER_IP = "localhost" 
TOPIC = "sensor/distance"

cap = None

def detect_and_draw_face(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    eq_frame = cv2.equalizeHist(gray_frame)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(eq_frame, scaleFactor=1.3, minNeighbors=5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(frame, 'Face Detected!', (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
    return frame

def on_message(client, userdata, msg):
    global cap
    try:
        distance = float(msg.payload.decode())
        print(f"Received distance: {distance:.1f} cm")

        if 2 <= distance <= 200:
            if cap is None:
                print("Opening camera...")
                cap = cv2.VideoCapture(0)

            ret, frame = cap.read()
            if ret:
                frame = detect_and_draw_face(frame)
                cv2.imshow("Face Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    client.disconnect()
        else:
            if cap is not None:
                print("Closing camera...")
                cap.release()
                cv2.destroyAllWindows()
                cap = None
    except Exception as e:
        print("Error:", e)

# Setup MQTT
client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER_IP, 1883, 60)
client.subscribe(TOPIC)

client.loop_forever()
