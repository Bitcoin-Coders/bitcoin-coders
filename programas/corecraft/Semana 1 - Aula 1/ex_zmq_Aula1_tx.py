import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.connect("tcp://127.0.0.1:58331")
socket.setsockopt_string(zmq.SUBSCRIBE,"rawtx")

print("Aguardando transações...")

while True:
    topic, payload, sequence = socket.recv_multipart()
    print("Nova transação recebida!")
    print(" - Tópico:", topic.decode())
    print(" - Tamanho do payload:",len(payload),"bytes")
    print(" - Payload em Hex:",payload.hex())
