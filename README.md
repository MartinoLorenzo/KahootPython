# 🎮 Kahoot Game - Progetto Quiz Multiplayer

**Sviluppatori:** Martino Lorenzo, Simone Virano, Beltramo Francesco

## 📋 Descrizione del Progetto

Questo progetto implementa un sistema di quiz multiplayer ispirato a Kahoot, sviluppato in Python utilizzando socket TCP per la comunicazione client-server e Tkinter per l'interfaccia grafica. Il sistema permette a più giocatori di partecipare simultaneamente a quiz organizzati per categorie con domande a risposta multipla.

## 🏗️ Architettura del Sistema

### Server (server.py)

- **Gestione connessioni:** Utilizza threading per gestire multiple connessioni client simultanee
- **Sistema di categorie:** 5 categorie disponibili (Geografia, Storia, Scienza, Arte e Cultura, Sport)
- **Countdown automatico:** Avvio automatico del gioco dopo 30 secondi dal primo giocatore
- **Sistema di punteggi:** Punteggio basato su correttezza della risposta e velocità
- **Gestione stati:** Stati del gioco (waiting, question, results, finished)

### Client (client.py)

- **Interfaccia grafica:** GUI moderna con Tkinter e design scuro
- **Connessione real-time:** Comunicazione in tempo reale con il server
- **Visualizzazione dinamica:** Timer, punteggi, classifiche e feedback visivo
- **Gestione errori:** Controllo nomi duplicati e partite in corso

## 🚀 Come Utilizzare il Progetto

### 1. Avvio del Server

```bash
python server.py
```

- Inserire l'host (default: localhost)
- Selezionare una categoria dal menu:
  - Geografia (6 domande)
  - Storia (6 domande)
  - Scienza (6 domande)
  - Arte e Cultura (6 domande)
  - Sport (6 domande)

Il server si avvierà sulla porta 12345

### 2. Connessione dei Client

```bash
python client.py
```

1. Inserire l'indirizzo del server (localhost per connessioni locali)
2. Cliccare "🚀 Connetti"
3. Inserire un nome giocatore unico
4. Attendere l'avvio automatico del gioco (30 secondi dal primo giocatore)

### 3. Gameplay

- **Countdown:** 30 secondi di attesa automatica dall'arrivo del primo giocatore
- **Domande:** Ogni domanda ha 4 opzioni di risposta con simboli geometrici
- **Timer:** Tempo limite variabile per ogni domanda (8-12 secondi)
- **Punteggio:** 500 punti base + bonus velocità (fino a 500 punti extra)
- **Risultati:** Visualizzazione risposta corretta e classifica aggiornata
- **Classifica finale:** Podium con medaglie e opzione di rigiocare

## 🔧 Funzionalità Principali

### Sistema di Punteggi

- **Punti base:** 500 punti per risposta corretta
- **Bonus velocità:** Calcolato in base al tempo di risposta
- **Formula:** Punteggio = 500 + (tempo_rimanente/tempo_totale * 500)

### Gestione Multiplayer

- **Controllo nomi:** Impedisce nomi duplicati
- **Stato partite:** Blocca nuovi ingressi durante le partite
- **Sincronizzazione:** Tutti i client ricevono aggiornamenti simultanei
- **Disconnessioni:** Gestione automatica delle disconnessioni

### Interfaccia Utente

- **Design moderno:** Tema scuro con colori vivaci
- **Feedback visivo:** Colori per risposte corrette/sbagliate
- **Responsive:** Adattamento automatico della finestra
- **Animazioni:** Effetti hover sui pulsanti

## 🛠️ Problemi Riscontrati e Soluzioni

### 1. Connessioni da Client Esterni

**Problema:** Inizialmente il sistema funzionava solo in locale (localhost), impedendo connessioni da dispositivi diversi sulla stessa rete.

**Soluzione:**
- Modificato il server per accettare host personalizzabili
- Implementato controllo dell'indirizzo IP del server
- Aggiunta gestione errori per connessioni remote
- Test su rete locale con indirizzi IP specifici

### 2. Sincronizzazione dei Timer

**Problema:** I timer dei client si desincronizzavano rispetto al server, causando incongruenze nei tempi di risposta.

**Soluzione:**
- Implementato timer lato server che controlla la durata delle domande
- I client ricevono il tempo limite ma il controllo finale resta al server
- Aggiunta gestione del timeout automatico

### 3. Gestione delle Disconnessioni Impreviste

**Problema:** Disconnessioni improvvise dei client causavano crash del server o stati inconsistenti.

**Soluzione:**
- Implementato sistema di exception handling robusto
- Thread daemon per gestire le connessioni
- Pulizia automatica dei client disconnessi
- Notifiche agli altri giocatori

### 4. Conflitti di Nomi Utente

**Problema:** Più utenti potevano registrarsi con lo stesso nome, causando confusione nelle classifiche.

**Soluzione:**
- Controllo unicità nomi al momento della registrazione
- Messaggio di errore specifico per nomi duplicati
- Disconnessione automatica in caso di nome già utilizzato

### 5. Gestione degli Stati del Gioco

**Problema:** Complessità nella gestione dei diversi stati (attesa, domanda, risultati, fine gioco) e transizioni tra essi.

**Soluzione:**
- Implementato state machine con stati chiaramente definiti
- Controlli di validità per ogni transizione di stato
- Messaggi specifici per ogni stato verso i client

## 📁 Struttura dei File

```
kahoot-project/
├── server.py          # Server principale con logica di gioco
├── client.py          # Client con interfaccia grafica
└── README.md          # Questo file
```

## 🔮 Possibili Miglioramenti Futuri

- **Database:** Salvataggio statistiche giocatori e punteggi
- **Domande personalizzate:** Caricamento domande da file JSON esterni
- **Modalità tornei:** Sistema di eliminazione a più round
- **Suoni ed effetti:** Feedback audio per risposte e fine gioco
- **Admin panel:** Interfaccia web per gestione server
- **Sicurezza:** Crittografia delle comunicazioni

## 🏃‍♂️ Test e Debugging

Per testare il sistema:

1. Avviare il server su una macchina
2. Connettere multiple istanze del client (anche da macchine diverse)
3. Verificare sincronizzazione timer e punteggi
4. Testare disconnessioni improvvise
5. Controllare gestione errori e stati inconsistenti