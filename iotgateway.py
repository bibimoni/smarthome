from flask import Flask, request, jsonify
import threading
import paho.mqtt.client as mqtt
import time

# ===== ADAFRUIT CONFIG =====
ADAFRUIT_AIO_USERNAME = "quanghung2405"
ADAFRUIT_AIO_KEY      = "aio_xWRU45vsUZKmCwgIJaTGqnnHgrmQ"

FEED_FAN  = ADAFRUIT_AIO_USERNAME + "/feeds/fan"
FEED_LED  = ADAFRUIT_AIO_USERNAME + "/feeds/led"
FEED_TEMP  = ADAFRUIT_AIO_USERNAME + "/feeds/temperature"
FEED_HUMID = ADAFRUIT_AIO_USERNAME + "/feeds/humid"
FEED_LIGHT = ADAFRUIT_AIO_USERNAME + "/feeds/light"

app = Flask(__name__)
latest_command = ""

# ===== MQTT CALLBACK =====
def on_connect(client, userdata, flags, rc):
    client.subscribe(FEED_FAN)
    client.subscribe(FEED_LED)

def on_message(client, userdata, msg):
    global latest_command

    data = msg.payload.decode("utf-8").strip()

    if msg.topic == FEED_FAN:
        latest_command = "FAN_ON" if data == "1" else "FAN_OFF"

    elif msg.topic == FEED_LED:
        latest_command = "LED_ON" if data == "1" else "LED_OFF"

# ===== RECEIVE SENSOR FROM YOLO =====
@app.route('/update', methods=['POST'])
def update():
    data = request.json

    temp  = data.get("temp")
    humi  = data.get("humi")
    light = data.get("light")

    # Only print required info
    print(
        "T:" + str(temp) +
        ",H:" + str(humi) +
        ",L:" + str(light)
    )

    client.publish(FEED_TEMP, temp)
    time.sleep(0.2)

    client.publish(FEED_HUMID, humi)
    time.sleep(0.2)

    client.publish(FEED_LIGHT, light)

    return "OK"

# ===== YOLO GET COMMAND =====
@app.route('/api/get-commands', methods=['GET'])
def get_command():
    global latest_command
    cmd = latest_command
    latest_command = ""
    return jsonify({"command": cmd})

# ===== MQTT THREAD =====
def mqtt_loop():
    global client
    client = mqtt.Client()
    client.username_pw_set(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("io.adafruit.com", 1883, 60)
    client.loop_forever()

# ===== MAIN =====
if __name__ == "__main__":
    threading.Thread(target=mqtt_loop).start()
    app.run(host="0.0.0.0", port=5000)
