import socket
import threading
import json
import os

class Client:
    def __init__(self, host='127.0.0.1', port=65431):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.name = input("Adınızı giriniz: ")
        self.client.send(self.name.encode())
    

        #user message history, group names history and, person contacts information are stored in json file
        self.history_file = f"{self.name}_history.json"
        self.groups_file = f"{self.name}_groups.json"
        self.contacts_file = f"{self.name}_contacts.json"
        
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = []

        if os.path.exists(self.groups_file):
            with open(self.groups_file, 'r') as f:
                self.groups = json.load(f)
        else:
            self.groups = {}

        if os.path.exists(self.contacts_file):
            with open(self.contacts_file, 'r') as f:
                self.contacts = json.load(f)
        else:
            self.contacts = []

        threading.Thread(target=self.receive_messages).start()
        self.main_menu()

    def receive_messages(self):
        while True:
            try:
                msg = self.client.recv(1024).decode()
                self.history.append(msg)
                print(msg)
                with open(self.history_file, 'w') as f:
                    json.dump(self.history, f)
            except ConnectionResetError:
                print("Sunucu ile bağlantı kesildi.")
                break

    def main_menu(self):
        while True:
            command = input("işlem seçin: (mesaj için=1/baglanti ekle=2/grup ekle=3/grup_goruntule=4/arama=5/çıkmak için =quit): ")
            if command == '1':
                self.send_messages()
            elif command == '2':
                self.add_contact()
            elif command == '3':
                self.add_group()
            elif command == '4':
                self.view_groups()
            elif command == '5':
                self.search_messages()
            elif command == 'quit':
                self.client.send('{quit}'.encode())
                self.client.close()
                break

    def send_messages(self):
        print("Mesaj gönderme moduna girdiniz. Ana menüye dönmek için 'exit' yazın.")
        while True:
            msg = input()
            if msg.lower() == 'exit':
                break
            self.client.send(msg.encode())

    def add_contact(self):
        print("Bağlantı ekleme moduna girdiniz. Ana menüye dönmek için 'exit' yazın.")
        while True:
            contact_name = input("Eklemek istediğiniz kullanıcının ismi: ")
            if contact_name.lower() == 'exit':
                break
            if contact_name not in self.contacts:
                self.contacts.append(contact_name)
                with open(self.contacts_file, 'w') as f:
                    json.dump(self.contacts, f)
                print(f"{contact_name} bağlantı listenize eklendi.")
            else:
                print(f"{contact_name} zaten bağlantı listenizde.")

    def add_group(self):
        group_name = input("Grup ismi: ")
        if group_name not in self.groups:
            self.groups[group_name] = []
        else:
            print(f"{group_name} zaten mevcut. Kullanıcı eklemeye devam edin.")
        
        print("Gruba eklemek istediğiniz kullanıcı isimlerini girin. Ekleme işlemi bittiğinde 'exit' yazın.")
        while True:
            user_name = input("Gruba eklemek istediğiniz kullanıcı ismi: ")
            if user_name.lower() == 'exit':
                break
            if user_name in self.contacts:
                if user_name not in self.groups[group_name]:
                    self.groups[group_name].append(user_name)
                    with open(self.groups_file, 'w') as f:
                        json.dump(self.groups, f)
                    print(f"{user_name}, {group_name} grubuna eklendi.")
                else:
                    print(f"{user_name} zaten {group_name} grubunda.")
            else:
                print(f"{user_name} bağlantı listenizde değil. Önce bağlantı listenize ekleyin.")


    def view_groups(self):
        for group, users in self.groups.items():
            print(f"{group}: {', '.join(users)}")

    def search_messages(self):
        keyword = input("Aranacak kelime: ")
        results = [msg for msg in self.history if keyword in msg]
        print("Arama sonuçları:")
        for result in results:
            print(result)

if __name__ == "__main__":
    Client()
