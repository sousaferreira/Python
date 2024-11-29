import json  # Para enviar dados em formato JSON
import time

import dht  # Importando o módulo para o sensor DHT
import network
import urequests  # Para realizar requisições HTTP
from machine import ADC, Pin

# Configurações da rede Wi-Fi
SSID = 'SALA-PRF'
PASSWORD = 'xYzW-628496'

# Configuração dos sensores
luminosity_sensor = ADC(Pin(32))  # Pino ADC para o sensor de luminosidade
rain_sensor = ADC(Pin(35))  # Pino ADC para o sensor de chuva

# Configuração do sensor DHT22 (temperatura e umidade)
dht_sensor = dht.DHT22(Pin(4))  # Pino GPIO para o DHT22

# Configura a conexão Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

# Aguarda a conexão com a rede Wi-Fi
while not wlan.isconnected():
    print('Aguardando conexão...')
    time.sleep(1)

print('Conectado à rede Wi-Fi')

# Função para ler os sensores
def read_sensors():
    # Leitura dos sensores
    luminosity_value = luminosity_sensor.read()
    rain_value = rain_sensor.read()

    # Invertendo a lógica para luminosidade e chuva
    luminosity_percentage = (1 - (luminosity_value / 4095)) * 100  # 0% com luz e 100% sem luz
    rain_percentage = (1 - (rain_value / 4095)) * 100  # 0% sem água e 100% com água

    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()  # Temperatura em Celsius
        humidity = dht_sensor.humidity()  # Umidade em porcentagem
    except OSError as e:
        print(f"Erro na leitura do sensor DHT: {e}")
        temperature = None
        humidity = None

    return luminosity_percentage, rain_percentage, temperature, humidity

# Função para enviar os dados via API
def send_data_to_api(luminosity, rain, temperature, humidity):
    api_url = 'http://10.0.0.48:8000/api/sensor-data'  # Substitua com seu IP local ou IP público
    data = {
        'luminosity': luminosity,
        'rain': rain,
        'temperature': temperature,
        'humidity': humidity
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = urequests.post(api_url, json=data, headers=headers)
        if response.status_code == 200:
            print('Dados enviados com sucesso!')
        else:
            print(f'Erro ao enviar dados. Status: {response.status_code}, Mensagem: {response.text}')
        response.close()
    except Exception as e:
        print(f'Erro ao enviar dados: {e}')


# Loop principal
while True:
    # Leitura dos sensores
    luminosity_percentage, rain_percentage, temperature, humidity = read_sensors()

    # Verifica se os dados foram lidos corretamente antes de enviar
    if temperature is not None and humidity is not None:
        # Enviar os dados para a API
        send_data_to_api(luminosity_percentage, rain_percentage, temperature, humidity)
    else:
        print("Falha na leitura do sensor DHT, dados não enviados.")

    # Aguardar um intervalo antes da próxima leitura
    time.sleep(10)  # Aguarda 10 segundos antes de enviar novamente
