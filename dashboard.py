import tkinter as tk
import paho.mqtt.client as mqtt
from utils import *
import json

class Dash:
    def __init__(self, name):
        self.name = name
        self.client = mqtt.Client(self.name)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        
        self.root = tk.Tk()
        self.root.title("Estoque de Peças")

        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=20, pady=20)

        self.cols_per_row = 5  # Quantidade de colunas por linha

        self.estoque_data = [
            [100, 75, 80, 50, 70, 60, 50],
            [50, 25, 35, 10, 4, 8, 30],
            ['green', 'yellow', 'green', 'red', 'red', 'red', 'green']
        ]

    def on_connect(self, client, userdata, flags, rc):
        print(f"{self.name} conectado ao broker")
        self.client.subscribe(topic_dashboard)


    # Função de callback para quando uma mensagem for recebida
    def on_message(self, client, userdata, msg):
        data_json = msg.payload.decode("utf-8")
        self.estoque_data = json.loads(data_json)
        #print(self.estoque_data)


    def update_window(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        for i in range(len(self.estoque_data[0])):
            row = i // self.cols_per_row
            col = i % self.cols_per_row

            max_qty = self.estoque_data[0][i]
            current_qty = self.estoque_data[1][i]
            label = self.estoque_data[2][i]
            
            cell_text = f"Peça {i + 1}\nEstoque: {current_qty}"
            color = label.lower()

            cell = tk.Label(self.frame, text=cell_text, bg=color)
            cell.grid(row=row, column=col, padx=10, pady=5, sticky="w")

        # atualiza a janela a cada 5 segundos
        self.root.after(2000, self.update_window)

    
    def start(self):
        self.update_window()
        
        try:
            self.client.loop_start()
            self.root.mainloop()
        except KeyboardInterrupt:
            self.client.loop_stop()
            self.client.disconnect()
            self.root.destroy()
            print(f"\nconexão {self.name} encerrada!")


#
# Inicializa objeto do fornecedor
dashboard = Dash("dashboard")
dashboard.start()


