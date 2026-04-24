import paho.mqtt.client as mqtt
from abc import ABC, abstractmethod

class Handler(ABC):
    @abstractmethod
    def set_next(self, handler):
        pass

    @abstractmethod
    def handle(self, request, bombilla):
        pass

class AbstractHandler(Handler):
    _next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request, bombilla):
        if self._next_handler:
            return self._next_handler.handle(request, bombilla)
        return None

class OnHandler(AbstractHandler):
    def handle(self, request, bombilla):
        if request == "on":
            if not bombilla.is_on:
                bombilla.is_on = True
                print("Encendendo bombilla")
            return True
        else:
            return super().handle(request, bombilla) 

class OffHandler(AbstractHandler):
    def handle(self, request, bombilla):
        if request == "off":
            if bombilla.is_on:
                bombilla.is_on = False
                print("Apagando bombilla")
            return True
        else:
            return super().handle(request, bombilla)

class StatusHandler(AbstractHandler):
    def handle(self, request, bombilla):
        if request == "status":
            estado_str = "on" if bombilla.is_on else "off"
            bombilla.client.publish("/oficina/luz1/state", estado_str)
            print(f"--> Solicitud de status recibida. Publicando: {estado_str}")
            return True
        else:
            return super().handle(request, bombilla)

class SmartBulb:
    def __init__(self, client):
        self.is_on = False
        self.client = client

cliente = mqtt.Client()
bombilla_contexto = SmartBulb(cliente)

manexador_on = OnHandler()
manexador_off = OffHandler()
manexador_status = StatusHandler()

manexador_on.set_next(manexador_off).set_next(manexador_status)

def ao_conectar(client, userdata, flags, rc):
    print("Bombilla conectada ao broker MQTT!")
    client.subscribe("/oficina/luz1/command")
    print("Á escoita de comandos en '/oficina/luz1/command'...")

def ao_recibir_mensaxe(client, userdata, msg):
    comando = msg.payload.decode("utf-8").strip().lower()
    resultado = manexador_on.handle(comando, bombilla_contexto)
    
    if not resultado:
        print(f"Comando descoñecido ignorado: {comando}")

IP_DA_VM = "10.0.2.7"

cliente.on_connect = ao_conectar
cliente.on_message = ao_recibir_mensaxe

cliente.connect(IP_DA_VM, 1883, 60)
cliente.loop_forever()