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
MQTT_TOPIC_AMBIENTE_STATUS = "petmonitor/ambiente/status"
MQTT_TOPIC_ALIMENTACAO_STATUS = "petmonitor/alimentacao/status"

mqtt_client = mqtt.Client()
last_ambiente_status = {}
last_alimentacao_status = {}

# Conectar ao broker MQTT
def connect_mqtt():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.loop_start()

# Callback para receber mensagens MQTT
def on_message(client, userdata, msg):
    global last_ambiente_status, last_alimentacao_status
    payload = msg.payload.decode("utf-8")
    topic = msg.topic
    if topic == MQTT_TOPIC_AMBIENTE_STATUS:
        logging.info(f"Atualizando status do ambiente: {payload}")
        last_ambiente_status = eval(payload)  # Considera JSON como dicionário
    elif topic == MQTT_TOPIC_ALIMENTACAO_STATUS:
        logging.info(f"Atualizando status da alimentação: {payload}")
        last_alimentacao_status = eval(payload)  # Considera JSON como dicionário

mqtt_client.on_message = on_message
connect_mqtt()

# Subscreve aos tópicos relevantes
mqtt_client.subscribe(MQTT_TOPIC_AMBIENTE_STATUS)
mqtt_client.subscribe(MQTT_TOPIC_ALIMENTACAO_STATUS)

@app.route('/command', methods=['POST'])
def handle_command():
    """
    Endpoint para lidar com comandos enviados pela Alexa Skill.
    """
    try:
        data = request.json
        if not data or 'request' not in data or 'intent' not in data['request']:
            raise KeyError("Estrutura de JSON inválida ou campo 'intent' ausente.")

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

        elif intent_name == "StatusAmbienteIntent":
            # Pega os últimos dados do ambiente
            if last_ambiente_status:
                temperatura = last_ambiente_status.get("temperatura", "desconhecida")
                umidade = last_ambiente_status.get("umidade", "desconhecida")
                return jsonify({
                    "version": "1.0",
                    "response": {
                        "outputSpeech": {
                            "type": "PlainText",
                            "text": f"A temperatura do ambiente é de {temperatura} graus e a umidade é de {umidade}%."
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
                            "text": "Ainda não há dados disponíveis sobre o ambiente."
                        },
                        "shouldEndSession": True
                    }
                }), 200

        elif intent_name == "StatusAlimentacaoIntent":
            # Pega os últimos dados da alimentação
            if last_alimentacao_status:
                quantidade_restante = last_alimentacao_status.get("quantidade_restante", "desconhecida")
                ultima_alimentacao = last_alimentacao_status.get("ultima_alimentacao", "desconhecida")
                return jsonify({
                    "version": "1.0",
                    "response": {
                        "outputSpeech": {
                            "type": "PlainText",
                            "text": f"Ainda há {quantidade_restante} gramas de ração disponíveis. A última alimentação foi às {ultima_alimentacao}."
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
                            "text": "Ainda não há dados disponíveis sobre a alimentação."
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
    except KeyError as e:
        app.logger.error(f"Erro: {e}")
        return jsonify({"error": f"Chave ausente no JSON: {e}"}), 400
    except Exception as e:
        app.logger.error(f"Erro: {e}")
        return jsonify({"error": "Erro ao processar a requisição."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
