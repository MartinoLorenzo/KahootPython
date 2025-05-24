import socket

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.bind(('127.0.0.1', 5007))
print("Server in ascolto...")

# Domande: (testo, risposta corretta)
domande = [
    ("Quanto fa 2 + 2?\n1) 1\n2) 2\n3) 4\n4) 5", "3"),
    ("In che linguaggio è scritto questo server?\n1) Java\n2) Python\n3) C#\n4) HTML", "2"),
    ("Qual è il colore del cielo?\n1) Rosso\n2) Blu\n3) Verde\n4) Giallo", "2"),
    ("Quanti giorni ha una settimana?\n1) 5\n2) 6\n3) 7\n4) 8", "3")
]

punteggi = {}

# Aspettiamo i messaggi dal client per conoscere il suo indirizzo (nome)
print("Aspetto giocatore...")
messaggio, addr = my_socket.recvfrom(1024)
nome_giocatore = messaggio.decode("utf-8")
print(f"Giocatore {nome_giocatore} con indirizzo {addr} connesso!")

for i, (testo, corretta) in enumerate(domande):
    # Invia la domanda al client
    my_socket.sendto(testo.encode("utf-8"), addr)

    # Ricevi la risposta dal client
    messaggio, addr_risposta = my_socket.recvfrom(1024)
    risposta = messaggio.decode("utf-8").strip()
    print(f"Risposta da {nome_giocatore}: {risposta}")

    # Aggiorna punteggio
    if nome_giocatore not in punteggi:
        punteggi[nome_giocatore] = 0
    if risposta == corretta:
        punteggi[nome_giocatore] += 1

# Stampa risultati
print("\n--- Risultati ---")
for nome, punti in punteggi.items():
    print(f"{nome}: {punti} punti")
