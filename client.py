import socket
import threading

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if msg:
                print(msg)
            else:
                break
        except:
            print("Ошибка при получении сообщения.")
            break

def send_message(sock):
    while True:
        msg = input()
        sock.send(msg.encode())

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 10001))

    # Запускаем поток для получения сообщений
    receive_thread = threading.Thread(target=receive_messages, args=(sock,))
    receive_thread.start()

    # Запускаем поток для отправки сообщений
    send_thread = threading.Thread(target=send_message, args=(sock,))
    send_thread.start()

if __name__ == "__main__":
    main()