import zmq
import time

ctx = zmq.Context()
sock = ctx.socket(zmq.SUB)
sock.connect("tcp://127.0.0.1:58334")
sock.setsockopt_string(zmq.SUBSCRIBE,"rawblock")

print("Monitorando eventos de blocos...")

while True:
    topic, msg, seq = sock.recv_multipart()
    print(f"[{time.strftime('%H:%M:%S')}] novo bloco recebido")
