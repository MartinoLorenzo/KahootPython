import socket
import threading
import tkinter as tk
from tkinter import messagebox

SERVER_ADDR = ("127.0.0.1", 5007)

class QuizClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Game")
        self.setup_socket()
        self.domande_ricevute = 0
        self.build_start_screen()

    def setup_socket(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.settimeout(60)

    def build_start_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Benvenuto al Quiz Game!", font=("Arial", 16, "bold")).pack(pady=20)
        self.build_button("Gioca", self.build_login_screen)
        self.build_button("Esci", self.root.quit)

    def build_login_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Inserisci il tuo nome:", font=("Arial", 14)).pack(pady=10)
        self.name_entry = tk.Entry(self.root, font=("Arial", 12))
        self.name_entry.pack(pady=5)
        self.build_button("Entra nel gioco", self.send_name)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def build_button(self, text, command):
        tk.Button(self.root, text=text, font=("Arial", 12), command=command, width=20).pack(pady=5)

    def send_name(self):
        self.nome = self.name_entry.get().strip()
        if not self.nome:
            messagebox.showerror("Errore", "Devi inserire un nome.")
            return
        try:
            self.client.sendto(self.nome.encode(), SERVER_ADDR)
            self.clear_screen()
            tk.Label(self.root, text="In attesa che tutti i giocatori si colleghino...", font=("Arial", 14)).pack(pady=10)
            self.status_label = tk.Label(self.root, text="", font=("Arial", 12))
            self.status_label.pack(pady=10)
            threading.Thread(target=self.listen_start).start()
        except Exception as e:
            self.show_connection_error(f"Errore di connessione: {e}")

    def listen_start(self):
        try:
            while True:
                msg, _ = self.client.recvfrom(2048)
                content = msg.decode()
                if content == "INIZIO":
                    self.show_question()
                    break
                elif content == "ERRORE_NOME":
                    messagebox.showerror("Errore", "Nome già in uso.")
                    self.build_login_screen()
                    break
                elif content.startswith("GIOCATORI:"):
                    self.status_label.config(text=content)
        except Exception:
            self.show_connection_error("Errore durante l'attesa dell'inizio del quiz.")

    def show_question(self):
        if self.domande_ricevute >= 4:
            self.wait_for_results()
            return
        self.clear_screen()
        try:
            data, _ = self.client.recvfrom(2048)
            domanda_data = data.decode().split("|")
            domanda_text = domanda_data[0]
            opzioni = domanda_data[1:]

            tk.Label(self.root, text=f"Domanda {self.domande_ricevute + 1}:", font=("Arial", 16, "bold")).pack(pady=10)
            tk.Label(self.root, text=domanda_text, font=("Arial", 12), wraplength=500).pack(pady=10)

            for i, opzione in enumerate(opzioni, start=1):
                tk.Button(self.root, text=opzione, font=("Arial", 12), width=30,
                          command=lambda i=i: self.send_answer(str(i))).pack(pady=4)

        except Exception:
            self.show_connection_error("Errore durante la ricezione della domanda.")

    def send_answer(self, risposta):
        try:
            self.client.sendto(risposta.encode(), SERVER_ADDR)
            self.domande_ricevute += 1
            self.clear_screen()
            tk.Label(self.root, text="Risposta inviata. Attendi...", font=("Arial", 14)).pack(pady=20)
            self.root.after(1000, self.show_question)
        except Exception:
            self.show_connection_error("Errore durante l'invio della risposta.")

    def wait_for_results(self):
        self.clear_screen()
        tk.Label(self.root, text="In attesa della classifica finale...", font=("Arial", 14)).pack(pady=20)
        threading.Thread(target=self.receive_results).start()

    def receive_results(self):
        try:
            classifica, _ = self.client.recvfrom(2048)
            self.clear_screen()
            tk.Label(self.root, text="Classifica Finale", font=("Arial", 16, "bold")).pack(pady=10)
            tk.Label(self.root, text=classifica.decode(), font=("Arial", 12), justify="left", wraplength=500).pack(pady=10)
            self.build_button("Rigioca", self.restart_quiz)
            self.build_button("Esci", self.root.quit)
        except Exception:
            self.show_connection_error("Errore durante la ricezione della classifica.")

    def show_connection_error(self, message):
        self.clear_screen()
        tk.Label(self.root, text="Errore di Connessione", font=("Arial", 16, "bold"), fg="red").pack(pady=10)
        tk.Label(self.root, text=message, font=("Arial", 12)).pack(pady=10)
        self.build_button("Riprova", self.restart_quiz)
        self.build_button("Esci", self.root.quit)

    def restart_quiz(self):
        try:
            self.client.close()
        except:
            pass
        self.setup_socket()
        self.domande_ricevute = 0
        self.build_login_screen()

root = tk.Tk()
root.geometry("600x450")
app = QuizClient(root)
root.mainloop()
