#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h> // Biblioteca ArduinoJson

// WiFi
const char* ssid = "Wokwi-GUEST";
const char* password = ""; // Sem senha

// MQTT
const char* mqttServer = "0.tcp.sa.ngrok.io";
const int mqttPort = 11868;  
const char* mqttUser = "";
const char* mqttPassword = "";

WiFiClient espClient;
PubSubClient client(espClient);

// DHT (Temperatura e Umidade)
#define DHTPIN 4       // Pino DATA do DHT22 conectado ao GPIO 4
#define DHTTYPE DHT22  // Tipo do sensor
DHT dht(DHTPIN, DHTTYPE);

// PIR (Sensor de Movimento)
#define PIRPIN 13 // Pino do sensor PIR
bool movimentoDetectado = false;

// Servo (Dispenser de Ração)
#include <ESP32Servo.h>
Servo servoDispenser;
#define SERVO_PIN 23 // Pino do servo motor

// Tópicos MQTT
#define TOPICO_AMBIENTE_STATUS "petmonitor/ambiente/status"
#define TOPICO_AMBIENTE_CONTROLE "petmonitor/ambiente/controle"
#define TOPICO_ALIMENTACAO_STATUS "petmonitor/alimentacao/status"
#define TOPICO_ALIMENTACAO_CONTROLE "petmonitor/alimentacao/controle"
#define TOPICO_NOTIFICACOES "petmonitor/notificacoes"

// Função para configurar a conexão Wi-Fi
void setupWiFi() {
  delay(10);
  Serial.println("Iniciando conexão Wi-Fi...");
  WiFi.begin(ssid, password);
  
  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 20) {
    delay(500);
    Serial.print(".");
    tentativas++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi-Fi conectado com sucesso!");
    Serial.print("Endereço IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFalha ao conectar no Wi-Fi.");
    Serial.println("Certifique-se de que o SSID e senha estão corretos.");
  }
}

int quantidadeRacaoRestante = 500; // Inicialmente 500 gramas

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Mensagem recebida no tópico: ");
  Serial.println(topic);

  String mensagemRecebida;
  for (int i = 0; i < length; i++) {
    mensagemRecebida += (char)message[i];
  }
  Serial.println("Mensagem: " + mensagemRecebida);

  // Parse JSON usando ArduinoJson
  DynamicJsonDocument doc(1024);
  DeserializationError error = deserializeJson(doc, mensagemRecebida);

  if (error) {
    Serial.print("Erro ao parsear JSON: ");
    Serial.println(error.c_str());
    return;
  }

  // Comando para liberar ração
  if (String(topic) == TOPICO_ALIMENTACAO_CONTROLE && doc.containsKey("liberar_racao")) {
    int quantidade = doc["liberar_racao"];
    Serial.printf("Liberando %d gramas de ração\n", quantidade);

    // Verifica se há ração suficiente antes de liberar
    if (quantidadeRacaoRestante >= quantidade) {
      // Movimenta o servo motor para liberar ração
      servoDispenser.write(90); // Gira para liberar
      delay(quantidade * 100);  // Duração proporcional à quantidade
      servoDispenser.write(0);  // Retorna à posição inicial

      // Atualiza a quantidade de ração restante
      quantidadeRacaoRestante -= quantidade;
      Serial.printf("Ração restante: %d gramas\n", quantidadeRacaoRestante);
    } else {
      Serial.println("Ração insuficiente para liberar a quantidade solicitada.");
    }
  }
}

// Função para enviar status do ambiente
void enviarStatusAmbiente() {
  float temperatura = dht.readTemperature();
  float umidade = dht.readHumidity();

  if (isnan(temperatura) || isnan(umidade)) {
    Serial.println("Falha ao ler o sensor DHT! Verifique o circuito.");
    return;
  }

  String mensagem = String("{\"temperatura\":") + String(temperatura) +
                    ",\"umidade\":" + String(umidade) +
                    ",\"timestamp\":\"2024-11-27T10:10:00\"}";
  client.publish(TOPICO_AMBIENTE_STATUS, mensagem.c_str());
  Serial.println("Status do ambiente enviado: " + mensagem);
}

// Função para enviar status da alimentação
void enviarStatusAlimentacao() {
  String mensagem = String("{\"quantidade_restante\":") + String(quantidadeRacaoRestante) +
                    ",\"ultima_alimentacao\":\"2024-11-27T10:00:00\"}";
  client.publish(TOPICO_ALIMENTACAO_STATUS, mensagem.c_str());
  Serial.println("Status da alimentação enviado: " + mensagem);

  // Notificação de ração acabando
  if (quantidadeRacaoRestante < 200) {
    String notificacao = String("{\"tipo_notificacao\":\"racao_baixa\",") +
                         "\"mensagem\":\"A quantidade de ração disponível é menor que 200g. Reabasteça o dispenser!\"," +
                         "\"timestamp\":\"2024-11-27T09:20:00\"}";
    client.publish(TOPICO_NOTIFICACOES, notificacao.c_str());
    Serial.println("Notificação enviada: " + notificacao);
  }
}

// Reconecta ao MQTT caso a conexão caia
void reconnect() {
  while (!client.connected()) {
    Serial.println("Conectando ao MQTT...");
    if (client.connect("ESP32Client", mqttUser, mqttPassword)) {
      Serial.println("Conectado ao MQTT!");
      client.subscribe(TOPICO_ALIMENTACAO_CONTROLE);
      client.subscribe(TOPICO_AMBIENTE_CONTROLE);
    } else {
      Serial.print("Falha ao conectar. Tentando novamente em 5 segundos...");
      delay(5000);
    }
  }
}

// Configuração inicial
void setup() {
  Serial.begin(115200);
  setupWiFi();
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);

  // Inicializa o DHT
  dht.begin();

  // Configura os pinos
  pinMode(PIRPIN, INPUT);
  servoDispenser.attach(SERVO_PIN);
}

// Loop principal
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  static unsigned long lastPublishTime = 0;
  unsigned long currentMillis = millis();

  // Publica status a cada 10 segundos
  if (currentMillis - lastPublishTime >= 10000) {
    enviarStatusAmbiente();
    enviarStatusAlimentacao();
    lastPublishTime = currentMillis;
  }

  // Verifica movimento
  movimentoDetectado = digitalRead(PIRPIN);
  if (movimentoDetectado) {
    Serial.println("Movimento detectado!");
    delay(5000);
  }
}
