import cv2
import socket
import pickle
import struct
import argparse

def send_video():
    cap = cv2.VideoCapture(0)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8080))

    while True:
        ret, frame = cap.read()

        data = pickle.dumps(frame)

        message = struct.pack('Q', len(data)) + data

        client_socket.sendall(message)

        cv2.imshow('Sender', frame)
        cv2.waitKey(1)

    cap.release()

def receive_video():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8080)) 
    server_socket.listen(5)

    print("Server listening...")

    connection, addr = server_socket.accept()
    print(f"Connection from {addr}")

    data = b""
    payload_size = struct.calcsize("Q")

    while True:
        while len(data) < payload_size:
            packet = connection.recv(4 * 1024)  # 4K buffer size
            if not packet:
                break
            data += packet

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        while len(data) < msg_size:
            data += connection.recv(4 * 1024)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        
        frame = pickle.loads(frame_data)

        cv2.imshow('Receiver', frame)
        cv2.waitKey(1)


if __name__ == "__main__":
    # Start sender and receiver in separate threads or processes

    import threading

    parser = argparse.ArgumentParser()
    parser.add_argument('-sender', action='store_true', help='Activate the sender')
    parser.add_argument('-receiver', action='store_true', help='Activate the receiver')

    args = parser.parse_args()

    if args.sender:
        sender_thread = threading.Thread(target=send_video)
        sender_thread.start()
        
    if args.receiver:
        receiver_thread = threading.Thread(target=receive_video)
        receiver_thread.start()
