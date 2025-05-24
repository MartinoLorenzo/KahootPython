import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(60)

nome = input("Inserisci il tuo nome: ")
client.sendto(nome.encode(), ("127.0.0.1", 5007))

# Attesa che il server avvii il quiz
print("In attesa che tutti i giocatori si colleghino...")

while True:
    try:
        msg, _ = client.recvfrom(1024)
        if msg.decode() == "INIZIO":
            print("Tutti i giocatori sono pronti. Inizia il quiz!")
            break
    except socket.timeout:
        print("Timeout durante l'attesa dell'inizio del quiz.")
        client.close()
        exit()

# Ricevi domande
for _ in range(4):
    domanda, _ = client.recvfrom(1024)
    print("\nDomanda:")
    print(domanda.decode())

    risposta = input("Scrivi la tua risposta (1-4): ")
    client.sendto(risposta.encode(), ("127.0.0.1", 5007))

    print("Risposta inviata. In attesa degli altri giocatori...")

# Classifica
print("\nIn attesa della classifica finale...")
try:
    classifica, _ = client.recvfrom(1024)
    print("\n" + classifica.decode())
except socket.timeout:
    print("imeout durante la ricezione della classifica.")

client.close()
