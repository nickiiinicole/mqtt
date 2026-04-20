import paho.mqtt.client as mqtt

bombilla_acendida = False
IP_DA_VM = "10.0.2.7" 

def conectar_mqtt(client, userdata, flags, rc):
    print("Conectado ao servidor MQTT:D")
    client.subscribe("/oficina/luz1")
    print("Esperando topic '/oficina/luz1'...")

def recibir_mensaje(client, userdata, msg):
    global bombilla_acendida
    msg.topic
    mensaje = msg.payload.decode("utf-8").strip()
    
    if mensaje == "On":
        if not bombilla_acendida:
            bombilla_acendida = True
            print("Encendiendo bombilla")
        else: 
            print("Bombilla ya esta encendida")
    elif mensaje == "Off":
        if bombilla_acendida:
            bombilla_acendida = False
            print("Apagando bombilla")
        else: 
            print("Bombilla ya esta apagada")
    else:
        print(f"(Mensaje ignorada: {mensaje})")

cliente = mqtt.Client()
cliente.on_connect = conectar_mqtt
cliente.on_message = recibir_mensaje


cliente.connect(IP_DA_VM, 1883, 60)

cliente.loop_forever()
