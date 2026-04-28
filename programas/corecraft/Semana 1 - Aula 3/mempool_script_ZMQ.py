import zmq
import time

ctx = zmq.Context()
sock = ctx.socket(zmq.SUB)
sock.connect("tcp://127.0.0.1:58331")
sock.setsockopt_string(zmq.SUBSCRIBE,"rawtx")

print("Monitorando eventos de mempool...")

while True:
    topic, msg, seq = sock.recv_multipart()
    print(f"[{time.strftime('%H:%M:%S')}] evento de mempool")
