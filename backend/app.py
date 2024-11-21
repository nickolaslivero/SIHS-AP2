from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

@app.route('/command', methods=['POST'])
def handle_command():
    """
    Endpoint para lidar com comandos enviados pela Alexa Skill.
    """
    app.logger.debug(f"Headers: {request.headers}")
    app.logger.debug(f"Body: {request.get_data(as_text=True)}")

    try:
        data = request.json
        if not data:
            raise ValueError("Nenhum JSON enviado no corpo da requisição.")

        app.logger.debug(f"JSON recebido: {data}")

        intent_name = data['request']['intent']['name']

        if intent_name == "LiberarRacaoIntent":
            app.logger.debug("Intent reconhecido: LiberarRacaoIntent")
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
        else:
            app.logger.debug("Intent desconhecido.")
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
        app.logger.error(f"Erro ao processar a requisição: {e}")
        return jsonify({"error": "Erro ao processar a requisição.", "message": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

