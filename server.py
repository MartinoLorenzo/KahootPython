import socket
import threading
import json
import time

class KahootServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.clients = {}  # {socket: {'name': str, 'score': int}}
        self.game_state = 'waiting'  # waiting, question, results, finished
        self.current_question = 0
        self.question_start_time = 0
        self.auto_start_timer = None
        self.countdown_active = False
        
        # Domande del quiz
        self.questions = [
            {
                "question": "Qual è la capitale d'Italia?",
                "options": ["Milano", "Roma", "Napoli", "Torino"],
                "correct": 1,
                "time_limit": 10
            },
            {
                "question": "Chi ha dipinto la Gioconda?",
                "options": ["Michelangelo", "Leonardo da Vinci", "Raffaello", "Caravaggio"],
                "correct": 1,
                "time_limit": 10
            },
            {
                "question": "Quale pianeta è più vicino al Sole?",
                "options": ["Venere", "Terra", "Mercurio", "Marte"],
                "correct": 2,
                "time_limit": 10
            },
            {
                "question": "In che anno è caduto il Muro di Berlino?",
                "options": ["1987", "1989", "1991", "1993"],
                "correct": 1,
                "time_limit": 10
            },
            {
                "question": "Qual è l'elemento chimico con simbolo 'O'?",
                "options": ["Oro", "Ossigeno", "Osmio", "Ozono"],
                "correct": 1,
                "time_limit": 10
            }
        ]
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def is_name_taken(self, name):
        """Controlla se il nome è già in uso"""
        existing_names = [client['name'].lower() for client in self.clients.values()]
        return name.lower() in existing_names
        
    def start_server(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(10)
            print(f"🎮 Server Kahoot avviato su {self.host}:{self.port}")
            print("In attesa di giocatori...")
            
            while True:
                client_socket, address = self.socket.accept()
                print(f"Nuovo giocatore connesso da {address}")
                
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except Exception as e:
            print(f"Errore server: {e}")
        finally:
            self.socket.close()
    
    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                message = json.loads(data)
                self.process_message(client_socket, message)
                
        except Exception as e:
            print(f"Errore con client: {e}")
        finally:
            self.remove_client(client_socket)
    
    def process_message(self, client_socket, message):
        msg_type = message.get('type')
        
        if msg_type == 'join':
            name = message.get('name', 'Anonimo')
            
            # Controlla se il nome è già in uso
            if self.is_name_taken(name):
                self.send_to_client(client_socket, {
                    'type': 'name_taken',
                    'message': f'Il nome "{name}" è già in uso. Scegli un altro nome.'
                })
                return
            
            self.clients[client_socket] = {'name': name, 'score': 0}
            print(f"👤 {name} si è unito al gioco")
            
            # Invia stato attuale
            self.send_to_client(client_socket, {
                'type': 'joined',
                'players': [client['name'] for client in self.clients.values()],
                'game_state': self.game_state
            })
            
            # Notifica altri giocatori
            self.broadcast_except(client_socket, {
                'type': 'player_joined',
                'name': name,
                'players': [client['name'] for client in self.clients.values()]
            })
            
            # Avvia countdown automatico se è il primo giocatore
            if len(self.clients) == 1 and not self.countdown_active:
                self.start_auto_countdown()
            
        elif msg_type == 'start_game':
            if len(self.clients) >= 1:
                self.cancel_auto_start()
                self.start_game()
            
        elif msg_type == 'answer':
            self.handle_answer(client_socket, message)
    
    def start_auto_countdown(self):
        """Avvia il countdown automatico di 30 secondi"""
        self.countdown_active = True
        print("⏰ Countdown automatico iniziato: 30 secondi")
        
        def countdown():
            for i in range(30, 0, -1):
                if not self.countdown_active:
                    return
                
                # Invia aggiornamento countdown a tutti i client
                self.broadcast({
                    'type': 'countdown',
                    'seconds': i
                })
                
                if i <= 10:
                    print(f"⏰ Avvio automatico in {i} secondi...")
                elif i % 5 == 0:
                    print(f"⏰ Avvio automatico in {i} secondi...")
                
                time.sleep(1)
            
            if self.countdown_active and len(self.clients) >= 1:
                print("🚀 Avvio automatico del gioco!")
                self.start_game()
        
        self.auto_start_timer = threading.Thread(target=countdown)
        self.auto_start_timer.daemon = True
        self.auto_start_timer.start()
    
    def cancel_auto_start(self):
        """Cancella il countdown automatico"""
        self.countdown_active = False
        self.broadcast({
            'type': 'countdown_cancelled'
        })
    
    def start_game(self):
        self.cancel_auto_start()
        self.game_state = 'question'
        self.current_question = 0
        print("🎯 Gioco iniziato!")
        
        # Reset punteggi
        for client_data in self.clients.values():
            client_data['score'] = 0
            
        self.send_question()
    
    def send_question(self):
        if self.current_question >= len(self.questions):
            self.end_game()
            return
            
        question_data = self.questions[self.current_question]
        self.question_start_time = time.time()
        
        message = {
            'type': 'question',
            'question_num': self.current_question + 1,
            'total_questions': len(self.questions),
            'question': question_data['question'],
            'options': question_data['options'],
            'time_limit': question_data['time_limit']
        }
        
        self.broadcast(message)
        print(f"📝 Domanda {self.current_question + 1}: {question_data['question']}")
        
        # Timer per la domanda - SOLO IL TIMER DECIDE QUANDO FINISCE
        timer_thread = threading.Thread(target=self.question_timer, args=(question_data['time_limit'],))
        timer_thread.daemon = True
        timer_thread.start()
    
    def question_timer(self, time_limit):
        """Timer che aspetta il tempo limite e poi mostra i risultati"""
        time.sleep(time_limit)
        if self.game_state == 'question':
            print("⏰ Tempo scaduto! Mostrando risultati...")
            self.show_results()
    
    def handle_answer(self, client_socket, message):
        if self.game_state != 'question':
            return
            
        answer = message.get('answer')
        response_time = time.time() - self.question_start_time
        
        # Calcola punteggio
        question_data = self.questions[self.current_question]
        points_earned = 0
        
        if answer == question_data['correct']:
            # Sistema di punteggio semplice
            base_points = 500  # Punti base per risposta corretta
            time_limit = question_data['time_limit']
            
            # Bonus velocità: da 0 a 500 punti extra
            time_bonus = max(0, int((time_limit - response_time) / time_limit * 500))
            
            points_earned = base_points + time_bonus
            self.clients[client_socket]['score'] += points_earned
            
            player_name = self.clients[client_socket]['name']
            print(f"✅ {player_name} ha risposto correttamente in {response_time:.1f}s! (+{points_earned} punti)")
        else:
            player_name = self.clients[client_socket]['name']
            print(f"❌ {player_name} ha risposto sbagliato in {response_time:.1f}s")
        
        # Invia conferma risposta al client
        self.send_to_client(client_socket, {
            'type': 'answer_received',
            'points_earned': points_earned,
            'correct': answer == question_data['correct']
        })
    
    def show_results(self):
        if self.game_state != 'question':
            return
            
        self.game_state = 'results'
        question_data = self.questions[self.current_question]
        
        # Prepara classifica
        leaderboard = []
        for client_socket, client_data in self.clients.items():
            leaderboard.append({
                'name': client_data['name'],
                'score': client_data['score']
            })
        
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        
        message = {
            'type': 'results',
            'correct_answer': question_data['correct'],
            'explanation': f"La risposta corretta era: {question_data['options'][question_data['correct']]}",
            'leaderboard': leaderboard
        }
        
        self.broadcast(message)
        
        # Prossima domanda dopo 4 secondi
        threading.Timer(4.0, self.next_question).start()
    
    def next_question(self):
        self.current_question += 1
        if self.current_question < len(self.questions):
            self.game_state = 'question'
            self.send_question()
        else:
            self.end_game()
    
    def end_game(self):
        self.game_state = 'finished'
        
        # Classifica finale
        leaderboard = []
        for client_data in self.clients.values():
            leaderboard.append({
                'name': client_data['name'],
                'score': client_data['score']
            })
        
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        
        message = {
            'type': 'game_finished',
            'leaderboard': leaderboard,
            'winner': leaderboard[0]['name'] if leaderboard else 'Nessuno'
        }
        
        self.broadcast(message)
        print("🏆 Gioco terminato!")
        print("Classifica finale:")
        for i, player in enumerate(leaderboard, 1):
            print(f"{i}. {player['name']}: {player['score']} punti")
        
        # Reset dello stato del server per permettere un nuovo gioco
        self.game_state = 'waiting'
        self.current_question = 0
        
        # Reset punteggi di tutti i client
        for client_data in self.clients.values():
            client_data['score'] = 0
    
    def send_to_client(self, client_socket, message):
        try:
            client_socket.send(json.dumps(message).encode('utf-8'))
        except:
            self.remove_client(client_socket)
    
    def broadcast(self, message):
        for client_socket in list(self.clients.keys()):
            self.send_to_client(client_socket, message)
    
    def broadcast_except(self, except_socket, message):
        for client_socket in list(self.clients.keys()):
            if client_socket != except_socket:
                self.send_to_client(client_socket, message)
    
    def remove_client(self, client_socket):
        if client_socket in self.clients:
            name = self.clients[client_socket]['name']
            del self.clients[client_socket]
            print(f"👋 {name} ha lasciato il gioco")
            
            # Notifica altri giocatori
            self.broadcast({
                'type': 'player_left',
                'name': name,
                'players': [client['name'] for client in self.clients.values()]
            })
            
            # Se non ci sono più giocatori, ferma il countdown
            if len(self.clients) == 0:
                self.cancel_auto_start()
        
        try:
            client_socket.close()
        except:
            pass

if __name__ == "__main__":
    server = KahootServer()
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server fermato")