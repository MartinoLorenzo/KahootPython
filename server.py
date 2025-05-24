import socket
import time

MAX_CLIENT = 4
WAIT_SECONDS = 30

domande = [
    ("Quanto fa 2 + 2?\n1) 1\n2) 2\n3) 4\n4) 5", "3"),
    ("In che linguaggio è scritto questo server?\n1) Java\n2) Python\n3) C#\n4) HTML", "2"),
    ("Qual è il colore del cielo?\n1) Rosso\n2) Blu\n3) Verde\n4) Giallo", "2"),
    ("Quanti giorni ha una settimana?\n1) 5\n2) 6\n3) 7\n4) 8", "3")
]

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('127.0.0.1', 5007))
server.settimeout(1)

clienti = {}
punteggi = {}

print(f"Aspetto massimo {MAX_CLIENT} giocatori per {WAIT_SECONDS} secondi...")
start = time.time()

# Attesa client
while len(clienti) < MAX_CLIENT and (time.time() - start) < WAIT_SECONDS:
    try:
        msg, addr = server.recvfrom(1024)
        nome = msg.decode().strip()
        if addr not in clienti:
            clienti[addr] = nome
            punteggi[nome] = 0
            print(f"{nome} connesso da {addr}")
    except socket.timeout:
        pass

num_giocatori = len(clienti)
if num_giocatori == 0:
    print("Nessun giocatore connesso.")
    server.close()
    exit()

print(f"\nInizio quiz con {num_giocatori} giocatori.")

# Invia messaggio di inizio
for addr in clienti:
    server.sendto(b"INIZIO", addr)

# Domande
for idx, (testo, corretta) in enumerate(domande, start=1):
    print(f"\nDomanda {idx}:")
    print(testo)

    for addr in clienti:
        server.sendto(testo.encode(), addr)

    ricevuti = set()
    risposte_domanda = {}

    while len(ricevuti) < num_giocatori:
        try:
            msg, addr = server.recvfrom(1024)
            if addr in clienti and addr not in ricevuti:
                risposta = msg.decode().strip()
                nome = clienti[addr]
                risposte_domanda[nome] = risposta
                if risposta == corretta:
                    punteggi[nome] += 1
                ricevuti.add(addr)
        except socket.timeout:
            continue

    print("Risposte ricevute:")
    for nome, risposta in risposte_domanda.items():
        stato = "corretta" if risposta == corretta else "sbagliata"
        print(f"{nome} ha risposto: {risposta} ({stato})")

# Classifica finale
classifica = "--- Classifica Finale ---\n"
for nome, punti in punteggi.items():
    classifica += f"{nome}: {punti} punti\n"

print("\n" + classifica.strip())

# Invia classifica ai client
for addr in clienti:
    server.sendto(classifica.encode(), addr)

server.close()
