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
        self.selected_category = None
        
        # Domande del quiz organizzate per categoria
        self.question_categories = {
            "Geografia": [
                {
                    "question": "Qual è la capitale d'Italia?",
                    "options": ["Milano", "Roma", "Napoli", "Torino"],
                    "correct": 1,
                    "time_limit": 10
                },
                {
                    "question": "Quale fiume attraversa Parigi?",
                    "options": ["Tamigi", "Senna", "Reno", "Danubio"],
                    "correct": 1,
                    "time_limit": 10
                },
                {
                    "question": "Qual è il continente più grande?",
                    "options": ["Africa", "Europa", "Asia", "America"],
                    "correct": 2,
                    "time_limit": 10
                },
                {
                    "question": "Quale paese ha più fusi orari?",
                    "options": ["Russia", "USA", "Cina", "Canada"],
                    "correct": 0,
                    "time_limit": 12
                },
                {
                    "question": "Qual è la montagna più alta del mondo?",
                    "options": ["K2", "Monte Bianco", "Everest", "Kilimanjaro"],
                    "correct": 2,
                    "time_limit": 10
                },
                {
                    "question": "Quale oceano bagna l'Australia a est?",
                    "options": ["Atlantico", "Indiano", "Pacifico", "Artico"],
                    "correct": 2,
                    "time_limit": 10
                }
            ],
            "Storia": [
                {
                    "question": "In che anno è caduto il Muro di Berlino?",
                    "options": ["1987", "1989", "1991", "1993"],
                    "correct": 1,
                    "time_limit": 10
                },
                {
                    "question": "Chi ha scoperto l'America?",
                    "options": ["Vasco da Gama", "Cristoforo Colombo", "Marco Polo", "Amerigo Vespucci"],
                    "correct": 1,
                    "time_limit": 10
                },
                {
                    "question": "Quando è iniziata la Prima Guerra Mondiale?",
                    "options": ["1912", "1914", "1916", "1918"],
                    "correct": 1,
                    "time_limit": 12
                },
                {
                    "question": "Chi era l'imperatore romano durante la nascita di Cristo?",
                    "options": ["Giulio Cesare", "Augusto", "Nerone", "Traiano"],
                    "correct": 1,
                    "time_limit": 12
                },
                {
                    "question": "In che anno è finita la Seconda Guerra Mondiale?",
                    "options": ["1943", "1944", "1945", "1946"],
                    "correct": 2,
                    "time_limit": 10
                },
                {
                    "question": "Quale civiltà costruì Machu Picchu?",
                    "options": ["Maya", "Aztechi", "Inca", "Olmeca"],
                    "correct": 2,
                    "time_limit": 10
                }
            ],
            "Scienza": [
                {
                    "question": "Qual è l'elemento chimico con simbolo 'O'?",
                    "options": ["Oro", "Ossigeno", "Osmio", "Ozono"],
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
                    "question": "Chi ha formulato la teoria della relatività?",
                    "options": ["Newton", "Einstein", "Galileo", "Darwin"],
                    "correct": 1,
                    "time_limit": 10
                },
                {
                    "question": "Qual è la velocità della luce nel vuoto?",
                    "options": ["300.000 km/s", "150.000 km/s", "450.000 km/s", "600.000 km/s"],
                    "correct": 0,
                    "time_limit": 12
                },
                {
                    "question": "Quanti cromosomi ha l'essere umano?",
                    "options": ["44", "46", "48", "50"],
                    "correct": 1,
                    "time_limit": 12
                },
                {
                    "question": "Qual è il gas più abbondante nell'atmosfera terrestre?",
                    "options": ["Ossigeno", "Azoto", "Anidride carbonica", "Argon"],
                    "correct": 1,
                    "time_limit": 10
                }
            ],
            "Arte e Cultura": [
                {
                    "question": "Chi ha dipinto la Gioconda?",
                    "options": ["Michelangelo", "Leonardo da Vinci", "Raffaello", "Caravaggio"],
                    "correct": 1,
                    "time_limit": 10
                },
                {
                    "question": "Chi ha scritto 'I Promessi Sposi'?",
                    "options": ["Dante", "Manzoni", "Leopardi", "Petrarca"],
                    "correct": 1,
                    "time_limit": 10
                },
                {
                    "question": "In quale città si trova il museo del Louvre?",
                    "options": ["Londra", "Roma", "Parigi", "Madrid"],
                    "correct": 2,
                    "time_limit": 10
                },
                {
                    "question": "Chi ha composto 'La Nona Sinfonia'?",
                    "options": ["Mozart", "Bach", "Beethoven", "Chopin"],
                    "correct": 2,
                    "time_limit": 10
                },
                {
                    "question": "Quale artista ha dipinto 'La Notte Stellata'?",
                    "options": ["Picasso", "Van Gogh", "Monet", "Renoir"],
                    "correct": 1,
                    "time_limit": 10
                },
                {
                    "question": "Chi ha scritto 'Romeo e Giulietta'?",
                    "options": ["Dante", "Shakespeare", "Molière", "Goethe"],
                    "correct": 1,
                    "time_limit": 10
                }
            ],
            "Sport": [
                {
                    "question": "Ogni quanti anni si svolgono le Olimpiadi estive?",
                    "options": ["2 anni", "3 anni", "4 anni", "5 anni"],
                    "correct": 2,
                    "time_limit": 10
                },
                {
                    "question": "Quanti giocatori ci sono in una squadra di calcio in campo?",
                    "options": ["10", "11", "12", "13"],
                    "correct": 1,
                    "time_limit": 8
                },
                {
                    "question": "In quale sport si usa una racchetta?",
                    "options": ["Calcio", "Tennis", "Nuoto", "Atletica"],
                    "correct": 1,
                    "time_limit": 8
                },
                {
                    "question": "Quale paese ha vinto più Mondiali di calcio?",
                    "options": ["Germania", "Argentina", "Brasile", "Italia"],
                    "correct": 2,
                    "time_limit": 10
                },
                {
                    "question": "Quanti set si giocano in una partita di tennis maschile al Roland Garros?",
                    "options": ["3", "5", "7", "Dipende"],
                    "correct": 1,
                    "time_limit": 12
                },
                {
                    "question": "In quale sport si usa il termine 'slam dunk'?",
                    "options": ["Pallavolo", "Tennis", "Basketball", "Rugby"],
                    "correct": 2,
                    "time_limit": 10
                }
            ]
        }
        
        self.questions = []  # Sarà popolato con la categoria scelta
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    def select_category(self):
        """Permette di scegliere la categoria delle domande"""
        print("\n🎯 SELEZIONE CATEGORIA QUIZ")
        print("=" * 40)
        categories = list(self.question_categories.keys())
        
        for i, category in enumerate(categories, 1):
            question_count = len(self.question_categories[category])
            print(f"{i}. {category} ({question_count} domande)")
        
        while True:
            try:
                choice = input(f"\nScegli una categoria (1-{len(categories)}): ").strip()
                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(categories):
                        self.selected_category = categories[choice_num - 1]
                        self.questions = self.question_categories[self.selected_category].copy()
                        print(f"\n✅ Categoria selezionata: {self.selected_category}")
                        print(f"📚 Domande caricate: {len(self.questions)}")
                        break
                
                print("❌ Scelta non valida. Riprova.")
            except (ValueError, KeyboardInterrupt):
                print("❌ Input non valido. Riprova.")
    
    def start_server(self):
        # Selezione categoria prima di avviare il server
        self.select_category()
        
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(10)
            print(f"\n🚀 Server Kahoot avviato su {self.host}:{self.port}")
            print(f"🎮 Categoria: {self.selected_category}")
            print("⏳ In attesa di giocatori...")
            
            while True:
                client_socket, address = self.socket.accept()
                print(f"👤 Nuovo giocatore connesso da {address}")
                
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except Exception as e:
            print(f"❌ Errore server: {e}")
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
            print(f"❌ Errore con client: {e}")
        finally:
            self.remove_client(client_socket)
    
    def process_message(self, client_socket, message):
        msg_type = message.get('type')
        
        if msg_type == 'join':
            name = message.get('name', 'Anonimo')
            self.clients[client_socket] = {'name': name, 'score': 0}
            print(f"👤 {name} si è unito al gioco")
            
            # Invia stato attuale
            self.send_to_client(client_socket, {
                'type': 'joined',
                'players': [client['name'] for client in self.clients.values()],
                'game_state': self.game_state,
                'category': self.selected_category
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
                
        elif msg_type == 'restart_game':
            if self.game_state == 'finished':
                self.restart_game()
            
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
                    print(f"🚀 Avvio automatico in {i} secondi...")
                elif i % 5 == 0:
                    print(f"⏰ Avvio automatico in {i} secondi...")
                
                time.sleep(1)
            
            if self.countdown_active and len(self.clients) >= 1:
                print("🎮 Avvio automatico del gioco!")
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
        print(f"🎮 Gioco iniziato! Categoria: {self.selected_category}")
        
        # Reset punteggi
        for client_data in self.clients.values():
            client_data['score'] = 0
            
        self.send_question()
    
    def restart_game(self):
        """Riavvia il gioco con le stesse domande"""
        print("🔄 Riavvio del gioco...")
        self.game_state = 'question'
        self.current_question = 0
        
        # Reset punteggi
        for client_data in self.clients.values():
            client_data['score'] = 0
        
        # Notifica tutti i client del riavvio
        self.broadcast({
            'type': 'game_restarted',
            'category': self.selected_category
        })
        
        # Avvia nuova partita dopo 2 secondi
        threading.Timer(2.0, self.send_question).start()
    
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
            'time_limit': question_data['time_limit'],
            'category': self.selected_category
        }
        
        self.broadcast(message)
        print(f"❓ Domanda {self.current_question + 1}: {question_data['question']}")
        
        # Timer per la domanda
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
            'winner': leaderboard[0]['name'] if leaderboard else 'Nessuno',
            'category': self.selected_category
        }
        
        self.broadcast(message)
        print("🏁 Gioco terminato!")
        print(f"🎯 Categoria: {self.selected_category}")
        print("🏆 Classifica finale:")
        for i, player in enumerate(leaderboard, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
            print(f"{medal} {i}. {player['name']}: {player['score']} punti")
    
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
    print("🎮 KAHOOT SERVER")
    print("=" * 30)
    host = input("Inserisci l'host (default: localhost): ").strip() or 'localhost'
    
    server = KahootServer(host=host)
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server fermato")
