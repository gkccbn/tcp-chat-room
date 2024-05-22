import socket
import threading
import json
import os

class Server:
    def __init__(self, host='127.0.0.1', port=65431):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket connection
        self.server.bind((host, port))
        self.server.listen()
        self.clients = {}
        self.addresses = {} #store addresses
        self.messages = {}  # store user messages
        
        if not os.path.exists('messages.json'):
            with open('messages.json', 'w') as f:
                json.dump({}, f)
        else:
            with open('messages.json', 'r') as f:
                self.messages = json.load(f)
    
    def handle_client(self, client, address):
        name = client.recv(1024).decode()
        self.clients[client] = name
        self.addresses[client] = address
        if name not in self.messages:
            self.messages[name] = []
        
        while True:
            try:
                msg = client.recv(1024).decode()
                if msg == '{quit}':
                    client.send('Goodbye!'.encode())
                    client.close()
                    del self.clients[client]
                    break
                else:
                    self.messages[name].append(msg)
                    self.broadcast(msg, name)
                    with open('messages.json', 'w') as f:
                        json.dump(self.messages, f)
            except ConnectionResetError:
                client.close()
                del self.clients[client]
                break

    def broadcast(self, msg, prefix=""):
        for client in self.clients:
            client.send(f"{prefix}: {msg}".encode())

    def start(self):
        print("Sunucu başlatıldı ve bağlantılar bekleniyor...")
        while True:
            client, address = self.server.accept()
            print(f"{address} ile bağlantı kuruldu.")
            threading.Thread(target=self.handle_client, args=(client, address)).start()

if __name__ == "__main__":
    server = Server()
    server.start()
