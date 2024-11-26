import socket
import threading
import time

clients = []
addresses = []
cities_used = []
current_turn = 0
game_started = False


def broadcast(message):
    for client in clients:
        client.send(message.encode())


def handle_client(client, client_address):
    global current_turn, game_started
    client_index = clients.index(client)
    player_name = f"Игрок {client_index + 1}"

    # Уведомляем всех об участнике
    broadcast(f"{player_name} присоединился к игре.")

    while True:
        if game_started:
            # Уведомляем текущего игрока о его ходе
            if client_index == current_turn:
                client.send(f"Ваш ход, {player_name}. ".encode())
                if len(cities_used) > 0:
                    last_city = cities_used[-1]
                    client.send(f"Введите город, начинающийся на '{last_city[-1].upper()}': ".encode())
                else:
                    client.send("Введите город: ".encode())

                start_time = time.time()
                time_limit = 10  # Таймаут на ход

                while True:
                    try:
                        # Получаем город от клиента
                        msg = client.recv(1024).decode()
                        if not msg:
                            break
                    except:
                        break

                    # Проверяем время
                    elapsed_time = time.time() - start_time
                    if elapsed_time > time_limit:  # 10 секунд на ход
                        winner_index = (current_turn + 1) % 2
                        broadcast(f"{player_name} не успел ввести город. Победитель: Игрок {winner_index + 1}.")
                        reset_game()
                        return

                    # Проверка на выход из игры
                    if msg.lower() == "exit":
                        broadcast(f"{player_name} вышел из игры.")
                        print(f"{player_name} ({client_address[0]}:{client_address[1]}) вышел из игры.")
                        reset_game()
                        return

                    # Проверяем, что город не использовался и начинается на нужную букву
                    if validate_city(msg):
                        cities_used.append(msg.lower())  # Сохраняем город в нижнем регистре
                        broadcast(f"{player_name}: {msg}")
                        current_turn = (current_turn + 1) % 2  # Меняем ход
                        break
                    else:
                        if msg.lower() in cities_used:
                            client.send("Этот город уже назывался. Попробуйте снова: ".encode())
                        else:
                            client.send("Неверный ввод. Попробуйте снова: ".encode())



def validate_city(city):
    city = city.lower()
    if city in cities_used:
        return False
    if len(cities_used) > 0:
        last_city = cities_used[-1]
        if not city.startswith(last_city[-1]):
            return False
    return True


def reset_game():
    global cities_used, current_turn, game_started
    # Выводим информацию об отключении игроков
    for i, client in enumerate(clients):
        client_address = addresses[i]
        print(f"Игрок {i + 1} ({client_address[0]}:{client_address[1]}) отключен.")

    cities_used.clear()
    current_turn = 0
    game_started = False
    # Отключаем всех клиентов
    for client in clients:
        client.close()
    clients.clear()  # Очищаем список клиентов
    addresses.clear()  # Очищаем список адресов


def accept_incoming_connections(sock):
    while True:
        client, client_address = sock.accept()
        if len(clients) < 2:  # Ограничиваем количество подключений до 2
            clients.append(client)
            addresses.append(client_address)

            print(f"Подключен {client_address[0]}:{client_address[1]}")  # Сообщение о подключении

            if len(clients) == 2:
                global game_started
                game_started = True
                broadcast("Игра началась! Первый ход у Игрока 1.")
                for client in clients:
                    threading.Thread(target=handle_client, args=(client, client_address)).start()
        else:
            client.send("Извините, игра уже заполнена. Подключение отклонено.".encode())
            client.close()  # Закрываем соединение, если больше 2 клиентов


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 10001))  # Указываем адрес и порт для сервера
    sock.listen(2)  # Слушаем до 2 клиентов
    print("Сервер запущен и ожидает подключения...")
    accept_incoming_connections(sock)


if __name__ == "__main__":
    main()