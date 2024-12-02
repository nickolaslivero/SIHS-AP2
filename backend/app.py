from flask import Flask, request, jsonify
import logging
import paho.mqtt.client as mqtt

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Configurações do MQTT
MQTT_BROKER = "0.tcp.sa.ngrok.io"
MQTT_PORT = 11868
MQTT_TOPIC_RACAO = "petmonitor/alimentacao/controle"
MQTT_TOPIC_AR = "petmonitor/ambiente/controle"

mqtt_client = mqtt.Client()

# Conectar ao broker MQTT
def connect_mqtt():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.loop_start()

connect_mqtt()

@app.route('/command', methods=['POST'])
def handle_command():
    """
    Endpoint para lidar com comandos enviados pela Alexa Skill.
    """
    try:
        data = request.json
        intent_name = data['request']['intent']['name']

        if intent_name == "LiberarRacaoIntent":
            # Publicar comando para liberar ração
            mqtt_client.publish(MQTT_TOPIC_RACAO, '{"liberar_racao": "10"}')
            return jsonify({
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": "Ração liberada com sucesso!"
                    },
                    "shouldEndSession": True
                }
            }), 200

        elif intent_name == "AjustarTemperaturaIntent":
            # Publicar comando para ajustar o ar-condicionado
            mqtt_client.publish(MQTT_TOPIC_AR, '{"ajustar_ar_condicionado": "25"}')
            return jsonify({
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": "Temperatura ajustada com sucesso!"
                    },
                    "shouldEndSession": True
                }
            }), 200

        else:
            return jsonify({
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": "Comando não reconhecido."
                    },
                    "shouldEndSession": True
                }
            }), 400
    except Exception as e:
        app.logger.error(f"Erro: {e}")
        return jsonify({"error": "Erro ao processar a requisição."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
