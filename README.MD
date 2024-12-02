Trabalho AP2 de SIHS

EQUIPE COMPOSTA POR:

CASSIEL STAVROS DE MELO DUTRA
MANUELA CRISTINA PEREIRA BASTOS
NICKOLAS JAVIER SANTOS LIVERO
VICTOR ALBARADO BRAGA


PetMonitor: Sistema Inteligente para Monitoramento e Alimentação de Pets
Este projeto consiste em um sistema completo para monitorar e gerenciar as condições ambientais de um pet, além de controlar a liberação de ração automaticamente. O sistema integra hardware, MQTT, Node-RED, Flask, e uma Skill da Alexa.

Descrição Geral
O PetMonitor permite que os donos de pets:

Visualizem temperatura, umidade e status da alimentação em tempo real.
Liberem ração manualmente ou de forma programada.
Consultem informações sobre o ambiente e alimentação diretamente pela Alexa.
O sistema utiliza um ESP32 para coletar dados e um backend com MQTT para gerenciar comunicação em tempo real. O Node-RED fornece uma interface visual, enquanto a Alexa oferece comandos de voz.

Componentes do Projeto
Hardware:

ESP32 (microcontrolador principal).
Sensor DHT22 (temperatura e umidade).
Servo motor (para liberação de ração).
Sensor PIR (movimento, opcional).
Software:

ESP32 com Arduino IDE (para controle de hardware e envio de dados via MQTT).
MQTT Broker (via ngrok para tunneling).
Flask (servidor que conecta Alexa com o MQTT).
Node-RED (dashboard interativo).
Alexa Skill (para comandos por voz).

Configuração e Execução
Pré-requisitos
Hardware:
ESP32, DHT22, Servo Motor, Jumpers.
Protoboard para prototipagem.
Software:
Arduino IDE.
Python 3.11+.
Node-RED instalado.
Conta na Alexa Developer Console.

Módulos do Sistema
Hardware
O hardware do projeto inclui:

ESP32: Controla sensores e atuadores.
Sensor DHT22: Mede temperatura e umidade.
Servo Motor: Libera a quantidade de ração configurada.

Conexões:
Sensor DHT22:
VCC → 3.3V ESP32
GND → GND ESP32
DATA → GPIO 4 ESP32
Servo Motor:
Sinal → GPIO 23 ESP32
VCC → 5V
GND → GND ESP32
Código ESP32
O código ESP32 gerencia os sensores e publica os dados no broker MQTT. Ele também recebe comandos para liberar ração.

Tópicos MQTT:
petmonitor/ambiente/status → Envia temperatura e umidade.
petmonitor/alimentacao/status → Envia status do dispenser.
petmonitor/alimentacao/controle → Recebe comandos para liberar ração.

Servidor Flask com MQTT
O servidor Flask serve como intermediário entre a Alexa e o broker MQTT.

Principais Intents:

LiberarRacaoIntent: Publica comando no tópico de controle da alimentação.
StatusAmbienteIntent: Responde com os últimos valores de temperatura e umidade.
StatusAlimentacaoIntent: Responde com a quantidade de ração restante.

Dashboard Node-RED
O Node-RED fornece um painel interativo para monitoramento e controle: