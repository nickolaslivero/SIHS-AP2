import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, broker_url, broker_port, topic=""):
        self.client = mqtt.Client()
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.topic = topic

    def connect(self):
        self.client.connect(self.broker_url, self.broker_port)

    def publish(self, message):
        if not self.topic:
            raise ValueError("Nenhum tópico configurado.")
        self.client.publish(self.topic, message)
