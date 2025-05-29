import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import socket
import json
import threading
import time


class KahootClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.player_name = ""
        self.has_answered = False
        self.game_started = False

        # Finestra principale
        self.root = tk.Tk()
        self.root.title("🎮 Kahoot Client")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(True, True)

        # Variabili
        self.current_question = tk.StringVar()
        self.time_left = tk.StringVar()
        self.score = tk.StringVar(value="Punteggio: 0")
        self.countdown_text = tk.StringVar()
        self.answer_status = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        # Frame principale
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Titolo
        title_frame = tk.Frame(main_frame, bg='#1a1a2e')
        title_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = tk.Label(
            title_frame,
            text="🎮 KAHOOT",
            font=('Arial', 28, 'bold'),
            fg='#ff6b6b',
            bg='#1a1a2e'
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Quiz Game",
            font=('Arial', 14),
            fg='#4ecdc4',
            bg='#1a1a2e'
        )
        subtitle_label.pack()

        # Frame connessione
        self.connection_frame = tk.Frame(main_frame, bg='#16213e', relief=tk.RAISED, bd=2)
        self.connection_frame.pack(fill=tk.X, pady=(0, 20), padx=10, ipady=10)

        conn_title = tk.Label(
            self.connection_frame,
            text="🔗 Connessione Server",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#16213e'
        )
        conn_title.pack(pady=(5, 10))

        conn_input_frame = tk.Frame(self.connection_frame, bg='#16213e')
        conn_input_frame.pack()

        tk.Label(
            conn_input_frame,
            text="Server:",
            font=('Arial', 11),
            fg='#ffffff',
            bg='#16213e'
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.server_entry = tk.Entry(
            conn_input_frame,
            font=('Arial', 11),
            width=15,
            bg='#2c3e50',
            fg='#ffffff',
            insertbackground='#ffffff'
        )
        self.server_entry.insert(0, "localhost")
        self.server_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.connect_btn = tk.Button(
            conn_input_frame,
            text="🚀 Connetti",
            font=('Arial', 11, 'bold'),
            bg='#4CAF50',
            fg='white',
            command=self.connect_to_server,
            cursor='hand2',
            relief=tk.FLAT,
            padx=20
        )
        self.connect_btn.pack(side=tk.LEFT)

        # Status
        self.status_label = tk.Label(
            main_frame,
            text="❌ Non connesso",
            font=('Arial', 12, 'bold'),
            fg='#ff6b6b',
            bg='#1a1a2e'
        )
        self.status_label.pack(pady=(0, 10))

        # Countdown automatico
        self.countdown_frame = tk.Frame(main_frame, bg='#1a1a2e')

        self.countdown_label = tk.Label(
            self.countdown_frame,
            textvariable=self.countdown_text,
            font=('Arial', 16, 'bold'),
            fg='#f39c12',
            bg='#1a1a2e'
        )
        self.countdown_label.pack(pady=10)

        # Frame gioco - INIZIALMENTE NASCOSTO
        self.game_frame = tk.Frame(main_frame, bg='#1a1a2e')

        # Header gioco
        game_header = tk.Frame(self.game_frame, bg='#16213e', relief=tk.RAISED, bd=2)
        game_header.pack(fill=tk.X, pady=(0, 20), padx=5, ipady=10)

        self.score_label = tk.Label(
            game_header,
            textvariable=self.score,
            font=('Arial', 16, 'bold'),
            fg='#4ecdc4',
            bg='#16213e'
        )
        self.score_label.pack(side=tk.LEFT, padx=20)

        self.time_label = tk.Label(
            game_header,
            textvariable=self.time_left,
            font=('Arial', 16, 'bold'),
            fg='#ff6b6b',
            bg='#16213e'
        )
        self.time_label.pack(side=tk.RIGHT, padx=20)

        # Status risposta
        self.answer_status_label = tk.Label(
            game_header,
            textvariable=self.answer_status,
            font=('Arial', 14, 'bold'),
            fg='#f39c12',
            bg='#16213e'
        )
        self.answer_status_label.pack()

        # Domanda
        question_frame = tk.Frame(self.game_frame, bg='#2c3e50', relief=tk.RAISED, bd=3)
        question_frame.pack(fill=tk.X, pady=(0, 30), padx=10, ipady=20)

        self.question_label = tk.Label(
            question_frame,
            textvariable=self.current_question,
            font=('Arial', 18, 'bold'),
            fg='#ffffff',
            bg='#2c3e50',
            wraplength=800,
            justify=tk.CENTER
        )
        self.question_label.pack(pady=10)

        # Frame risposte con griglia 2x2
        self.answers_frame = tk.Frame(self.game_frame, bg='#1a1a2e')
        self.answers_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # Configura griglia
        self.answers_frame.grid_columnconfigure(0, weight=1)
        self.answers_frame.grid_columnconfigure(1, weight=1)
        self.answers_frame.grid_rowconfigure(0, weight=1)
        self.answers_frame.grid_rowconfigure(1, weight=1)

        # Bottoni risposta
        self.answer_buttons = []
        colors = ['#e74c3c', '#3498db', '#f39c12', '#2ecc71']  # Rosso, Blu, Arancione, Verde
        hover_colors = ['#c0392b', '#2980b9', '#e67e22', '#27ae60']
        symbols = ['△', '◇', '○', '□']  # Simboli geometrici

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

        for i, (row, col) in enumerate(positions):
            btn_frame = tk.Frame(self.answers_frame, bg='#1a1a2e')
            btn_frame.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')

            btn = tk.Button(
                btn_frame,
                text="",
                font=('Arial', 14, 'bold'),
                bg=colors[i],
                fg='white',
                relief=tk.FLAT,
                bd=0,
                command=lambda x=i: self.answer_question(x),
                cursor='hand2',
                state=tk.DISABLED,
                wraplength=300
            )
            btn.pack(fill=tk.BOTH, expand=True, ipadx=10, ipady=30)

            # Effetti hover
            def on_enter(event, button=btn, color=hover_colors[i]):
                if button['state'] != tk.DISABLED and not self.has_answered:
                    button.config(bg=color)

            def on_leave(event, button=btn, color=colors[i]):
                if button['state'] != tk.DISABLED and button['bg'] != '#34495e' and not self.has_answered:
                    button.config(bg=color)

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

            self.answer_buttons.append(btn)

        # Frame giocatori
        self.players_frame = tk.LabelFrame(
            main_frame,
            text="👥 Giocatori Online",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#1a1a2e',
            labelanchor='n'
        )
        self.players_frame.pack(fill=tk.X, pady=(20, 0))

        # Lista giocatori
        players_container = tk.Frame(self.players_frame, bg='#16213e')
        players_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.players_listbox = tk.Listbox(
            players_container,
            font=('Arial', 11),
            height=3,
            bg='#16213e',
            fg='#ffffff',
            selectbackground='#4ecdc4',
            selectforeground='#000000',
            relief=tk.FLAT,
            bd=0
        )
        self.players_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        players_scrollbar = tk.Scrollbar(players_container, orient=tk.VERTICAL)
        players_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.players_listbox.config(yscrollcommand=players_scrollbar.set)
        players_scrollbar.config(command=self.players_listbox.yview)

        # RIMOSSO COMPLETAMENTE IL BOTTONE START

    def connect_to_server(self):
        server_host = self.server_entry.get() or "localhost"

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((server_host, 12345))
            self.connected = True

            # Chiedi nome giocatore
            self.player_name = simpledialog.askstring(
                "👤 Nome Giocatore",
                "Inserisci il tuo nome:",
                parent=self.root
            )

            if not self.player_name:
                self.player_name = f"Giocatore{int(time.time()) % 1000}"

            # Invia richiesta di join
            self.send_message({
                'type': 'join',
                'name': self.player_name
            })

            # Avvia thread per ricevere messaggi
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()

            self.status_label.config(text=f"✅ Connesso come {self.player_name}", fg='#4CAF50')
            self.connect_btn.config(state=tk.DISABLED, text="Connesso", bg='#95a5a6')

        except Exception as e:
            messagebox.showerror("❌ Errore", f"Impossibile connettersi al server:\n{e}")
            self.connected = False

    def receive_messages(self):
        try:
            while self.connected:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break

                message = json.loads(data)
                self.handle_message(message)

        except Exception as e:
            if self.connected:
                messagebox.showerror("❌ Errore", f"Connessione persa:\n{e}")
                self.connected = False

    def handle_message(self, message):
        msg_type = message.get('type')

        if msg_type == 'joined':
            # Mostra solo la lista giocatori, NESSUN bottone start
            self.update_players_list(message.get('players', []))

        elif msg_type == 'player_joined' or msg_type == 'player_left':
            self.update_players_list(message.get('players', []))

        elif msg_type == 'countdown':
            # Mostra SOLO countdown e lista giocatori
            seconds = message.get('seconds', 0)
            self.countdown_text.set(f"⏰ Avvio automatico in {seconds} secondi...")
            self.countdown_frame.pack(pady=10)

        elif msg_type == 'countdown_cancelled':
            self.countdown_frame.pack_forget()

        elif msg_type == 'question':
            # Il gioco è iniziato! Nascondi countdown, mostra game_frame
            self.countdown_frame.pack_forget()
            if not self.game_started:
                self.game_frame.pack(fill=tk.BOTH, expand=True)
                self.game_started = True
            self.show_question(message)

        elif msg_type == 'answer_received':
            self.handle_answer_feedback(message)

        elif msg_type == 'results':
            self.show_results(message)

        elif msg_type == 'game_finished':
            self.show_final_results(message)
            # Reset per eventuale nuovo gioco
            self.game_started = False

    def update_players_list(self, players):
        self.players_listbox.delete(0, tk.END)
        for i, player in enumerate(players, 1):
            self.players_listbox.insert(tk.END, f"{i}. 👤 {player}")

    def show_question(self, message):
        question_num = message.get('question_num', 1)
        total_questions = message.get('total_questions', 1)
        question = message.get('question', '')
        options = message.get('options', [])
        time_limit = message.get('time_limit', 10)

        # Reset stato risposta
        self.has_answered = False
        self.answer_status.set("")

        self.current_question.set(f"Domanda {question_num}/{total_questions}: {question}")

        # Simboli per i bottoni
        symbols = ['△', '◇', '○', '□']
        colors = ['#e74c3c', '#3498db', '#f39c12', '#2ecc71']

        # Aggiorna bottoni risposta
        for i, (btn, option) in enumerate(zip(self.answer_buttons, options)):
            btn.config(
                text=f"{symbols[i]}\n{option}",
                state=tk.NORMAL,
                bg=colors[i]
            )

        # Avvia timer
        self.start_timer(time_limit)

    def start_timer(self, time_limit):
        def countdown():
            for i in range(time_limit, -1, -1):
                if not self.connected:
                    break

                if i <= 3:
                    self.time_label.config(fg='#ff4757')  # Rosso per ultimi 3 secondi
                elif i <= 5:
                    self.time_label.config(fg='#ffa502')  # Arancione per ultimi 5 secondi
                else:
                    self.time_label.config(fg='#ff6b6b')

                self.time_left.set(f"⏱️ {i}s")
                time.sleep(1)

            # Disabilita bottoni quando il tempo scade
            if not self.has_answered:
                for btn in self.answer_buttons:
                    btn.config(state=tk.DISABLED)
                self.answer_status.set("⏰ Tempo scaduto!")

        timer_thread = threading.Thread(target=countdown)
        timer_thread.daemon = True
        timer_thread.start()

    def answer_question(self, answer_index):
        if not self.connected or self.has_answered:
            return

        self.has_answered = True

        # Disabilita tutti i bottoni dopo la risposta
        for i, btn in enumerate(self.answer_buttons):
            if i == answer_index:
                btn.config(state=tk.DISABLED, bg='#34495e')  # Evidenzia scelta
            else:
                btn.config(state=tk.DISABLED)

        self.answer_status.set("✓ Risposta inviata! Aspetta il tempo...")

        self.send_message({
            'type': 'answer',
            'answer': answer_index
        })

    def handle_answer_feedback(self, message):
        points_earned = message.get('points_earned', 0)
        is_correct = message.get('correct', False)

        if is_correct and points_earned > 0:
            self.answer_status.set(f"✅ Corretto! +{points_earned} punti")
            self.answer_status_label.config(fg='#27ae60')
        elif is_correct:
            self.answer_status.set("✅ Corretto!")
            self.answer_status_label.config(fg='#27ae60')
        else:
            self.answer_status.set("❌ Sbagliato!")
            self.answer_status_label.config(fg='#e74c3c')

    def show_results(self, message):
        correct_answer = message.get('correct_answer', 0)
        explanation = message.get('explanation', '')
        leaderboard = message.get('leaderboard', [])

        # Evidenzia risposta corretta
        self.answer_buttons[correct_answer].config(bg='#27ae60')

        # Aggiorna punteggio
        for player in leaderboard:
            if player['name'] == self.player_name:
                self.score.set(f"💰 Punteggio: {player['score']}")
                break

        # Mostra spiegazione
        self.current_question.set(f"✅ {explanation}")
        self.time_left.set("📊 Risultati")

    def show_final_results(self, message):
        leaderboard = message.get('leaderboard', [])
        winner = message.get('winner', 'Nessuno')

        # Crea finestra risultati
        results_window = tk.Toplevel(self.root)
        results_window.title("🏆 Risultati Finali")
        results_window.geometry("500x600")
        results_window.configure(bg='#1a1a2e')
        results_window.resizable(False, False)

        # Centra la finestra
        results_window.transient(self.root)
        results_window.grab_set()

        # Header
        header_frame = tk.Frame(results_window, bg='#2c3e50', height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="🏆 CLASSIFICA FINALE",
            font=('Arial', 20, 'bold'),
            fg='#f39c12',
            bg='#2c3e50'
        ).pack(expand=True)

        # Vincitore
        winner_frame = tk.Frame(results_window, bg='#1a1a2e')
        winner_frame.pack(fill=tk.X, pady=20)

        tk.Label(
            winner_frame,
            text=f"👑 Vincitore: {winner}",
            font=('Arial', 16, 'bold'),
            fg='#4CAF50',
            bg='#1a1a2e'
        ).pack()

        # Classifica
        leaderboard_frame = tk.Frame(results_window, bg='#1a1a2e')
        leaderboard_frame.pack(fill=tk.BOTH, expand=True, padx=30)

        for i, player in enumerate(leaderboard, 1):
            color = '#f39c12' if i == 1 else '#c0392b' if i == 2 else '#16a085' if i == 3 else '#ffffff'
            medal = '🥇' if i == 1 else '🥈' if i == 2 else '🥉' if i == 3 else '🏅'

            player_frame = tk.Frame(leaderboard_frame, bg='#2c3e50', relief=tk.RAISED, bd=1)
            player_frame.pack(fill=tk.X, pady=5)

            tk.Label(
                player_frame,
                text=f"{medal} {i}°",
                font=('Arial', 14, 'bold'),
                fg=color,
                bg='#2c3e50',
                width=8
            ).pack(side=tk.LEFT, padx=10, pady=10)

            tk.Label(
                player_frame,
                text=player['name'],
                font=('Arial', 12, 'bold'),
                fg='#ffffff',
                bg='#2c3e50'
            ).pack(side=tk.LEFT, padx=10, pady=10)

            tk.Label(
                player_frame,
                text=f"{player['score']} punti",
                font=('Arial', 12),
                fg=color,
                bg='#2c3e50'
            ).pack(side=tk.RIGHT, padx=10, pady=10)

        # Bottone chiudi
        tk.Button(
            results_window,
            text="🚪 Chiudi",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            command=results_window.destroy,
            relief=tk.FLAT,
            padx=30,
            pady=10
        ).pack(pady=20)

    def send_message(self, message):
        if self.connected and self.socket:
            try:
                self.socket.send(json.dumps(message).encode('utf-8'))
            except:
                self.connected = False

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        if self.connected and self.socket:
            self.socket.close()
        self.root.destroy()


if __name__ == "__main__":
    client = KahootClient()
    client.run()
