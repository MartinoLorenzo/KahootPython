import socket
import time

# Parametri
MAX_CLIENT = 4
WAIT_SECONDS = 30

# Domande (testo, risposta corretta)
domande = [
    ("Quanto fa 2 + 2?\n1) 1\n2) 2\n3) 4\n4) 5", "3"),
    ("In che linguaggio è scritto questo server?\n1) Java\n2) Python\n3) C#\n4) HTML", "2"),
    ("Qual è il colore del cielo?\n1) Rosso\n2) Blu\n3) Verde\n4) Giallo", "2"),
    ("Quanti giorni ha una settimana?\n1) 5\n2) 6\n3) 7\n4) 8", "3")
]

# Socket UDP
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('127.0.0.1', 5007))
server.settimeout(1)

clienti = {}
punteggi = {}

print(f"Aspetto massimo {MAX_CLIENT} giocatori per {WAIT_SECONDS} secondi...")
start = time.time()

# Attendi client
while len(clienti) < MAX_CLIENT and time.time() - start < WAIT_SECONDS:
    try:
        msg, addr = server.recvfrom(1024)
        nome = msg.decode().strip()
        if addr not in clienti:
            clienti[addr] = nome
            punteggi[nome] = 0
            print(f"{nome} connesso da {addr}")
    except socket.timeout:
        pass

if not clienti:
    print("Nessun giocatore connesso.")
    server.close()
    exit()

print(f"\nInizio quiz con {len(clienti)} giocatori!")

# Rimuovi il timeout per il quiz
server.settimeout(None)

# Invia domande e ricevi risposte
for testo, corretta in domande:
    for addr in clienti:
        server.sendto(testo.encode(), addr)

    ricevuti = set()

    while len(ricevuti) < len(clienti):
        msg, addr = server.recvfrom(1024)
        if addr in clienti and addr not in ricevuti:
            risposta = msg.decode().strip()
            nome = clienti[addr]
            if risposta == corretta:
                punteggi[nome] += 1
            ricevuti.add(addr)

# Classifica finale
classifica = "--- Classifica Finale ---\n"
for nome, punti in punteggi.items():
    classifica += f"{nome}: {punti} punti\n"

print(classifica.strip())

for addr in clienti:
    server.sendto(classifica.encode(), addr)

server.close()
