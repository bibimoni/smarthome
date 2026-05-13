
import json
import logging
import threading
import time
from typing import Optional, Callable, Dict
import paho.mqtt.client as mqtt
from flask import current_app

logger = logging.getLogger(__name__)


class MQTTService:


    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, username: str = None, api_key: str = None, flask_app=None):


        if hasattr(self, '_initialized') and self._initialized:
            return

        self.username = username
        self.api_key = api_key
        self.flask_app = flask_app
        self.client = None
        self.connected = False
        self._callbacks = {}
        self._command_queue = []
        self._initialized = False

        if username and api_key:
            self.connect()

    @classmethod
    def get_instance(cls):

        return cls._instance

    @classmethod
    def init_app(cls, app):

        username = app.config.get('ADAFRUIT_IO_USERNAME')
        api_key = app.config.get('ADAFRUIT_IO_KEY')

        if username and api_key:
            service = cls(username, api_key, flask_app=app)
            app.mqtt_service = service
            return service
        return None

    def is_connected(self) -> bool:

        return self.connected

    def connect(self):

        if self.client:
            return

        self.client = mqtt.Client()

        self.client.username_pw_set(self.username, self.api_key)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        try:
            logger.info(f"Connecting to Adafruit IO as {self.username}...")
            self.client.connect("io.adafruit.com", 1883, 60)
            self.client.loop_start()
            self._initialized = True
            logger.info("MQTT loop started in background thread")
        except Exception as e:
            logger.error(f"MQTT connection error: {e}")

    def disconnect(self):

        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            self._initialized = False

    def _on_connect(self, client, userdata, flags, rc):

        if rc == 0:
            self.connected = True
            logger.info("✅ Connected to Adafruit IO MQTT broker successfully!")
            self._subscribe_to_feeds()
        else:
            logger.error(f"❌ MQTT connection failed with code: {rc}")

    def _on_disconnect(self, client, userdata, rc):

        self.connected = False
        logger.warning(f"⚠️ Disconnected from Adafruit IO (rc: {rc})")

    def _on_message(self, client, userdata, msg):

        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')

            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                data = payload

            if topic in self._callbacks:
                self._callbacks[topic](data)

            self._process_sensor_data(topic, data)

        except Exception as e:
            print(f"Error processing message: {e}")

    def _subscribe_to_feeds(self):

        from app.models.device import Sensor, Actuator

        app = self.flask_app
        if app is None:
            try:
                from flask import current_app
                app = current_app._get_current_object()
            except RuntimeError:
                pass

        if app is None:
            logger.warning("MQTT: No Flask app available, skipping sensor subscription")
            return

        try:
            with app.app_context():
                sensors = Sensor.query.filter_by(is_active=True).all()
                logger.info("📡 Subscribing to sensor feeds...")
                for sensor in sensors:
                    topic = f"{self.username}/feeds/{sensor.feed_key}"
                    self.client.subscribe(topic)
                    logger.info(f"  ✅ Subscribed to sensor: {sensor.feed_key}")

                actuators = Actuator.query.filter_by(is_active=True).all()
                if actuators:
                    logger.info("🎮 Available actuators (control via API):")
                    for actuator in actuators:
                        logger.info(f"  📤 {actuator.name} -> {self.username}/feeds/{actuator.feed_key}")
                    test_cmd = 'curl -X POST http://localhost:5001/api/actuators/1/control -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d \'{"action": "ON"}\''
                    logger.info(f"  💡 Test with: {test_cmd}")
        except Exception as e:
            logger.warning(f"MQTT: Could not subscribe to feeds: {e}")

    def _process_sensor_data(self, topic: str, data):

        from app.extensions import db
        from app.models.device import Sensor, Actuator
        from app.models.data import SensorData, EventLog

        app = self.flask_app
        if app is None:
            try:
                from flask import current_app
                app = current_app._get_current_object()
            except RuntimeError:
                pass

        if app is None:
            logger.warning("MQTT: No Flask app available, skipping sensor data processing")
            return

        with app.app_context():
            parts = topic.split('/')
            if len(parts) >= 3:
                feed_key = parts[2]
            else:
                return

            sensor = Sensor.query.filter_by(feed_key=feed_key).first()
            if not sensor:
                return

            try:
                if isinstance(data, dict):
                    value = float(data.get('value', data.get('last_value', 0)))
                else:
                    value = float(data)
            except (ValueError, TypeError):
                value = 0

            sensor_data = SensorData(
                sensor_id=sensor.id,
                value=value
            )
            db.session.add(sensor_data)
            db.session.commit()

            self._check_threshold_rules(sensor, value)

    def _check_threshold_rules(self, sensor, value: float):

        from app.models.automation import ThresholdRule
        from app.models.data import EventLog
        from app.models.device import Actuator

        rules = ThresholdRule.query.filter_by(
            sensor_id=sensor.id,
            is_active=True
        ).all()

        for rule in rules:
            actuator = rule.actuator

            if actuator.mode == Actuator.MODE_MANUAL:
                continue

            if rule.evaluate(value):
                self.publish_actuator_command(actuator.feed_key, rule.action_value)

                actuator.current_value = rule.action_value

                EventLog.log_event(
                    event_type=EventLog.TYPE_AUTO,
                    description=f"{rule.get_condition_string()}: {actuator.name} set to {rule.action_value}",
                    actuator_id=actuator.id,
                    device_name=actuator.name,
                    metadata={
                        'rule_id': rule.id,
                        'sensor_value': value,
                        'action_value': rule.action_value
                    }
                )

    def subscribe(self, feed_key: str, callback: Callable = None):


        topic = f"{self.username}/feeds/{feed_key}"

        if callback:
            self._callbacks[topic] = callback

        if self.client and self.connected:
            self.client.subscribe(topic)

    def publish_actuator_command(self, feed_key: str, value: str):


        if not self.client or not self.connected:
            logger.warning("MQTT not connected, cannot publish")
            return False

        topic = f"{self.username}/feeds/{feed_key}"
        logger.info(f"Publishing to MQTT topic: {topic}, value: {value}")

        try:
            result = self.client.publish(topic, value)
            success = result.rc == mqtt.MQTT_ERR_SUCCESS
            logger.info(f"MQTT publish result: rc={result.rc}, success={success}")
            return success
        except Exception as e:
            logger.error(f"Error publishing to {topic}: {e}")
            return False

    def queue_command(self, feed_key: str, value: str):


        command_map = {
            'fan': 'FAN',
            'led': 'LED'
        }
        cmd_name = command_map.get(feed_key, feed_key.upper())
        command = f"{cmd_name}_{value}"

        self._command_queue.append({
            'command': command,
            'value': value,
            'feed_key': feed_key,
            'timestamp': time.time()
        })
        logger.info(f"Queued command: {command} (feed: {feed_key})")

        self.publish_actuator_command(feed_key, value)

    def get_commands(self) -> list:


        commands = self._command_queue.copy()
        self._command_queue.clear()
        return commands

    def get_latest_command(self) -> dict:

        if self._command_queue:
            cmd = self._command_queue[-1]
            self._command_queue.clear()
            return cmd
        return {'command': '', 'value': ''}

    def send_sensor_data(self, feed_key: str, value: float):


        if not self.client or not self.connected:
            print("MQTT not connected, cannot send sensor data")
            return False

        topic = f"{self.username}/feeds/{feed_key}"

        try:
            result = self.client.publish(topic, str(value))
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"Error sending sensor data to {topic}: {e}")
            return False


mqtt_service = None


def init_mqtt(app):

    global mqtt_service
    mqtt_service = MQTTService.init_app(app)
    return mqtt_service
