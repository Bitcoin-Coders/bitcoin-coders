import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.connect("tcp://127.0.0.1:58334")
socket.setsockopt_string(zmq.SUBSCRIBE,"rawblock")

print("Aguardando blocos...")

while True:
    topic, payload, sequence = socket.recv_multipart()
    print("Novo bloco recebido!")
    print(" - Tópico:", topic.decode())
    print(" - Tamanho do bloco:",len(payload),"bytes")
    print(" - Sequência:",int.from_bytes(sequence,"little"))
