import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

nome = input("Inserisci il tuo nome: ")
client.sendto(nome.encode(), ("127.0.0.1", 5007))

for _ in range(4):
    domanda, _ = client.recvfrom(1024)
    print("\nDomanda:")
    print(domanda.decode())

    risposta = input("Scrivi la tua risposta (1-4): ")
    client.sendto(risposta.encode(), ("127.0.0.1", 5007))

print("In attesa della classifica...")
classifica, _ = client.recvfrom(1024)
print("\n" + classifica.decode())

client.close()
