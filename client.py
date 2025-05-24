import socket

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

nome = input("Inserisci il tuo nome: ")

# Invia il nome al server per registrarsi
my_socket.sendto(nome.encode("utf-8"), ("127.0.0.1", 5007))

for i in range(4):
    # Ricevi la domanda dal server
    domanda, _ = my_socket.recvfrom(1024)
    print("\nDomanda:")
    print(domanda.decode("utf-8"))

    # Ricevi risposta dall'utente
    risposta = input("Scrivi la tua risposta (1-4): ")

    # Invia risposta al server
    my_socket.sendto(risposta.encode("utf-8"), ("127.0.0.1", 5007))

print("Risposte inviate. Attendi i risultati.")
my_socket.close()
