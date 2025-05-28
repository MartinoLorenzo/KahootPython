import socket
import time

MAX_CLIENT = 4
WAIT_SECONDS = 30
RESPONSE_TIMEOUT = 10

domande = [
    ("Quanto fa 2 + 2?", ["1", "2", "4", "5"], "3"),
    ("In che linguaggio è scritto questo server?", ["Java", "Python", "C#", "HTML"], "2"),
    ("Colore del cielo?", ["Rosso", "Blu", "Verde", "Giallo"], "2"),
    ("Giorni della settimana?", ["5", "6", "7", "8"], "3")
]

def start_quiz():
    while True:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(("127.0.0.1", 5007))
        server.settimeout(1)

        clienti = {}
        punteggi = {}
        nomi_usati = set()

        print(f"\n[SERVER] In attesa di massimo {MAX_CLIENT} giocatori per {WAIT_SECONDS} secondi...")

        start = time.time()
        while len(clienti) < MAX_CLIENT and (time.time() - start) < WAIT_SECONDS:
            try:
                msg, addr = server.recvfrom(1024)
                nome = msg.decode().strip()

                if not nome:
                    continue  # ignora nomi vuoti
                if nome in nomi_usati:
                    server.sendto(b"ERRORE_NOME", addr)
                    continue

                if addr not in clienti:
                    clienti[addr] = nome
                    nomi_usati.add(nome)
                    punteggi[nome] = 0
                    print(f"[SERVER] {nome} connesso da {addr}")

                    elenco = "GIOCATORI:\n" + "\n".join(clienti.values())
                    for a in clienti:
                        server.sendto(elenco.encode(), a)

            except socket.timeout:
                continue

        if not clienti:
            print("[SERVER] Nessun giocatore connesso.")
            server.close()
            continue

        for addr in clienti:
            server.sendto(b"INIZIO", addr)

        for domanda, opzioni, corretta in domande:
            for addr in list(clienti.keys()):
                try:
                    server.sendto(f"{domanda}|{'|'.join(opzioni)}".encode(), addr)
                except:
                    nome = clienti[addr]
                    print(f"[SERVER] Disconnesso: {nome}")
                    nomi_usati.remove(nome)
                    del punteggi[nome]
                    del clienti[addr]

            ricevuti = set()
            start_time = time.time()

            while len(ricevuti) < len(clienti) and (time.time() - start_time) < RESPONSE_TIMEOUT:
                try:
                    msg, addr = server.recvfrom(1024)
                    if addr in clienti and addr not in ricevuti:
                        risposta = msg.decode().strip()
                        nome = clienti[addr]
                        if risposta == corretta:
                            punteggi[nome] += 1
                        ricevuti.add(addr)
                except socket.timeout:
                    continue
                except:
                    if addr in clienti:
                        nome = clienti[addr]
                        print(f"[SERVER] Disconnesso: {nome}")
                        nomi_usati.remove(nome)
                        del punteggi[nome]
                        del clienti[addr]

        classifica = "--- Classifica Finale ---\n"
        for nome, punti in sorted(punteggi.items(), key=lambda x: x[1], reverse=True):
            classifica += f"{nome}: {punti} punti\n"

        for addr in clienti:
            server.sendto(classifica.encode(), addr)

        server.close()
        print("[SERVER] Partita conclusa. In attesa di nuova partita...\n")

start_quiz()
