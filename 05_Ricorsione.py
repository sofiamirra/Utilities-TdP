# ============================================================
# 06_RICORSIONE_v2.py
# ============================================================
# Questo file raccoglie le casistiche principali per impostare la ricorsione negli esercizi di TdP.
# Non è pensato per essere eseguito direttamente.
# Ogni blocco va copiato nel file corretto del progetto, di solito nel Model e nel Controller.
#
# Regola generale:
# - Il metodo pubblico del Model è il MANAGER: inizializza variabili e fa partire la ricorsione.
# - Il metodo _ricorsione è l'OPERAIO: espande parziale, controlla vincoli e fa backtracking.
# - Se serve, creo una funzione _getScore per calcolare il punteggio del parziale.
# - Il Controller legge gli input dalla View, chiama il metodo pubblico del Model e stampa il risultato.
#
# Schema mentale:
# - Se la traccia dice "partendo dal nodo selezionato", il manager NON fa un ciclo su tutti i nodi.
# - Se la traccia dice "trova il cammino migliore nel grafo", il manager fa un ciclo su tutti i nodi.
# - Se la traccia dice "nella componente connessa più grande", il manager fa un ciclo solo sui nodi di quella componente.
# - Se la traccia dice "arrivare a destinazione", aggiorno l'ottimo solo quando arrivo a destinazione.
# - Se la traccia dice "lunghezza esatta K", aggiorno l'ottimo solo quando len(parziale) == K.
# - Se la traccia dice "massimo assoluto" senza traguardo, aggiorno l'ottimo a ogni passo valido.
# ============================================================


# ============================================================
# CASO 0: IMPORT E VARIABILI STANDARD
# ============================================================
# Esempio:
# Prima di usare ricorsione e backtracking, preparo import e variabili standard.
#
# Logica procedurale:
# 1. Uso copy.deepcopy quando salvo il migliore, perché parziale cambia con append e pop.
# 2. Uso self._bestPath per il miglior percorso.
# 3. Uso self._bestScore per il miglior punteggio.
# 4. Uso parziale per il percorso che sto costruendo.
# ============================================================

# ------------------------------------------------------------
# MODEL - INIT: variabili standard
# ------------------------------------------------------------

    def __init__(self):
        self._graph = nx.Graph()
        self._bestPath = []
        self._bestScore = 0


# ============================================================
# CASO 1: MANAGER CON NODO DI PARTENZA SELEZIONATO
# ============================================================
# Esempio:
# La traccia dice: "partendo dal nodo selezionato dall'utente, trovare il cammino migliore".
#
# Logica procedurale:
# 1. Il nodo di partenza è già noto.
# 2. Non devo provare tutti i nodi del grafo.
# 3. Inizializzo parziale con il solo nodo di partenza.
# 4. Chiamo la ricorsione una sola volta.
#
# Quando usare questo caso:
# quando la View contiene un Dropdown, una TextField o una selezione da cui ricavo il nodo source.
# ============================================================


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPercorsoDaNodo(self, source):
        self._bestPath = []
        self._bestScore = 0

        parziale = [source]
        self._ricorsione(parziale)

        return self._bestPath, self._bestScore


# ============================================================
# CASO 2: MANAGER CON CICLO INIZIALE SU TUTTI I NODI
# ============================================================
# Esempio:
# La traccia dice: "trovare il cammino migliore nel grafo" senza indicare un nodo di partenza.
#
# Logica procedurale:
# 1. Non ho un nodo source imposto.
# 2. Ogni nodo del grafo può essere il punto di partenza del cammino migliore.
# 3. Faccio un for su tutti i nodi.
# 4. Per ogni nodo creo un nuovo parziale iniziale.
# 5. Chiamo la ricorsione partendo da quel nodo.
# 6. Le variabili bestPath e bestScore non vengono resettate dentro il ciclo, altrimenti perderei il migliore globale.
#
# Quando usare questo caso:
# quando la traccia chiede il migliore assoluto nel grafo.
# ============================================================


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPercorsoMiglioreGrafo(self):
        self._bestPath = []
        self._bestScore = 0

        for n in self._graph.nodes:
            parziale = [n]
            self._ricorsione(parziale)

        return self._bestPath, self._bestScore


# ============================================================
# CASO 3: MANAGER LIMITATO A UNA COMPONENTE CONNESSA
# ============================================================
# Esempio:
# La traccia chiede prima di trovare la componente connessa più grande e poi di cercare il percorso migliore
# solo all'interno di quella componente.
#
# Logica procedurale:
# 1. Calcolo le componenti connesse del grafo.
# 2. Seleziono la componente più grande.
# 3. Faccio partire la ricorsione solo dai nodi che appartengono a quella componente.
# 4. Nel metodo ricorsivo controllo anche che i vicini appartengano alla componente ammessa.
# 5. In questo modo non esploro nodi fuori dalla componente richiesta.
#
# Quando usare questo caso:
# quando la traccia dice "all'interno della componente connessa maggiore" oppure "nella componente del nodo selezionato".
# ============================================================


# ------------------------------------------------------------
# MODEL - componente connessa più grande
# ------------------------------------------------------------

    def getPercorsoMiglioreComponenteMaggiore(self):
        self._bestPath = []
        self._bestScore = 0

        componenti = list(nx.connected_components(self._graph))
        componente = max(componenti, key=len)
        self._nodiAmmessi = set(componente)

        for n in self._nodiAmmessi:
            parziale = [n]
            self._ricorsioneConNodiAmmessi(parziale)

        return self._bestPath, self._bestScore


# ------------------------------------------------------------
# MODEL - componente connessa del nodo selezionato
# ------------------------------------------------------------

    def getPercorsoMiglioreComponenteDiNodo(self, source):
        self._bestPath = []
        self._bestScore = 0

        componente = nx.node_connected_component(self._graph, source)
        self._nodiAmmessi = set(componente)

        parziale = [source]
        self._ricorsioneConNodiAmmessi(parziale)

        return self._bestPath, self._bestScore


# ------------------------------------------------------------
# MODEL - ricorsione limitata ai nodi ammessi
# ------------------------------------------------------------

    def _ricorsioneConNodiAmmessi(self, parziale):
        if len(parziale) > self._bestScore:
            self._bestPath = copy.deepcopy(parziale)
            self._bestScore = len(parziale)

        for n in self._graph.neighbors(parziale[-1]):
            if n in self._nodiAmmessi and n not in parziale:
                parziale.append(n)
                self._ricorsioneConNodiAmmessi(parziale)
                parziale.pop()


# ============================================================
# CASO 4: CAMMINO SEMPLICE DI LUNGHEZZA MASSIMA CON PESI STRETTAMENTE CRESCENTI
# ============================================================
# Esempio:
# Trovare un cammino semplice di lunghezza massima tale che ogni arco successivo abbia peso strettamente crescente.
#
# Logica procedurale:
# 1. Non esiste una destinazione obbligatoria.
# 2. Non esiste una lunghezza esatta da raggiungere.
# 3. Ogni parziale valido può essere il migliore.
# 4. Aggiorno l'ottimo a ogni chiamata.
# 5. La terminazione è implicita: se non ci sono vicini validi, il for non entra.
# 6. Controllo peso_corrente > peso_precedente.
#
# Quando usare questo caso:
# quando la traccia dice "più lungo" e "pesi strettamente crescenti".
# ============================================================


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPercorsoCrescenteDaNodo(self, source):
        self._bestPath = []
        self._bestScore = 0

        parziale = [source]
        self._ricorsioneCrescente(parziale)

        return self._bestPath, self._bestScore

    def _ricorsioneCrescente(self, parziale):
        if len(parziale) > self._bestScore:
            self._bestPath = copy.deepcopy(parziale)
            self._bestScore = len(parziale)

        for n in self._graph.successors(parziale[-1]):
            if n not in parziale:
                peso_corrente = self._graph[parziale[-1]][n]['weight']

                if len(parziale) == 1:
                    peso_precedente = -float('inf')
                else:
                    peso_precedente = self._graph[parziale[-2]][parziale[-1]]['weight']

                if peso_corrente > peso_precedente:
                    parziale.append(n)
                    self._ricorsioneCrescente(parziale)
                    parziale.pop()


# ============================================================
# CASO 5: CAMMINO SEMPLICE DI PESO MASSIMO CON PESI STRETTAMENTE DECRESCENTI
# ============================================================
# Esempio:
# Trovare il percorso di peso massimo partendo da un nodo, con archi successivi di peso decrescente.
#
# Logica procedurale:
# 1. Il punteggio da massimizzare non è la lunghezza, ma la somma dei pesi.
# 2. Uso _getScore per calcolare il peso totale del parziale.
# 3. Aggiorno l'ottimo a ogni passo valido.
# 4. Controllo peso_precedente > peso_corrente.
# 5. Non metto return dentro il for, altrimenti diventa greedy.
# ============================================================


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPercorsoDecrescentePesoMassimo(self, source):
        self._bestPath = []
        self._bestScore = 0

        parziale = [source]
        self._ricorsioneDecrescente(parziale)

        return self._bestPath, self._bestScore

    def _ricorsioneDecrescente(self, parziale):
        score = self._getScore(parziale)

        if score > self._bestScore:
            self._bestPath = copy.deepcopy(parziale)
            self._bestScore = score

        for n in self._graph.neighbors(parziale[-1]):
            if n not in parziale:
                peso_corrente = self._graph[parziale[-1]][n]['weight']

                if len(parziale) == 1:
                    peso_precedente = float('inf')
                else:
                    peso_precedente = self._graph[parziale[-2]][parziale[-1]]['weight']

                if peso_corrente < peso_precedente:
                    parziale.append(n)
                    self._ricorsioneDecrescente(parziale)
                    parziale.pop()


# ============================================================
# CASO 6: CAMMINO CON DESTINAZIONE FISSA
# ============================================================
# Esempio:
# Trovare il miglior cammino da source a target.
#
# Logica procedurale:
# 1. La soluzione è valida solo se termina in target.
# 2. Aggiorno l'ottimo solo quando parziale[-1] == target.
# 3. Quando raggiungo target faccio return.
# 4. Prima di target non salvo la soluzione, perché non è ancora completa.
# ============================================================


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPercorsoConDestinazione(self, source, target):
        self._bestPath = []
        self._bestScore = 0
        self._target = target

        parziale = [source]
        self._ricorsioneDestinazione(parziale)

        return self._bestPath, self._bestScore

    def _ricorsioneDestinazione(self, parziale):
        if parziale[-1] == self._target:
            score = self._getScore(parziale)

            if score > self._bestScore:
                self._bestPath = copy.deepcopy(parziale)
                self._bestScore = score

            return

        for n in self._graph.neighbors(parziale[-1]):
            if n not in parziale:
                parziale.append(n)
                self._ricorsioneDestinazione(parziale)
                parziale.pop()


# ============================================================
# CASO 7: CAMMINO CON LUNGHEZZA ESATTA K
# ============================================================
# Esempio:
# Trovare il cammino migliore lungo esattamente K nodi.
#
# Logica procedurale:
# 1. La soluzione è valida solo se len(parziale) == K.
# 2. Aggiorno l'ottimo solo a lunghezza esatta.
# 3. Quando raggiungo K nodi faccio return.
# 4. Se la traccia parla di K archi, controllo len(parziale)-1 == K.
# ============================================================


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPercorsoLunghezzaK(self, source, k):
        self._bestPath = []
        self._bestScore = 0
        self._k = k

        parziale = [source]
        self._ricorsioneLunghezzaK(parziale)

        return self._bestPath, self._bestScore

    def _ricorsioneLunghezzaK(self, parziale):
        if len(parziale) == self._k:
            score = self._getScore(parziale)

            if score > self._bestScore:
                self._bestPath = copy.deepcopy(parziale)
                self._bestScore = score

            return

        for n in self._graph.neighbors(parziale[-1]):
            if n not in parziale:
                parziale.append(n)
                self._ricorsioneLunghezzaK(parziale)
                parziale.pop()


# ============================================================
# CASO 8: CAMMINO CON SERBATOIO LIMITATO
# ============================================================
# Esempio:
# Trovare il cammino con maggior numero di nodi, ma con peso totale non superiore a una soglia.
#
# Logica procedurale:
# 1. Calcolo il peso del parziale.
# 2. Se supera la soglia, faccio return.
# 3. Se è valido, posso aggiornare l'ottimo.
# 4. Continuo a esplorare perché potrei aggiungere nodi senza superare la soglia.
# ============================================================


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPercorsoConBudget(self, source, maxPeso):
        self._bestPath = []
        self._bestScore = 0
        self._maxPeso = maxPeso

        parziale = [source]
        self._ricorsioneBudget(parziale)

        return self._bestPath, self._bestScore

    def _ricorsioneBudget(self, parziale):
        score = self._getScore(parziale)

        if score > self._maxPeso:
            return

        if len(parziale) > self._bestScore:
            self._bestPath = copy.deepcopy(parziale)
            self._bestScore = len(parziale)

        for n in self._graph.neighbors(parziale[-1]):
            if n not in parziale:
                parziale.append(n)
                self._ricorsioneBudget(parziale)
                parziale.pop()


# ============================================================
# CASO 9: SELEZIONARE K NODI CON VINCOLO DI COMPONENTI DIVERSE
# ============================================================
# Esempio:
# Trovare un set di K nodi tale che ogni nodo appartenga a una componente connessa diversa.
#
# Logica procedurale:
# 1. Non sto costruendo un percorso, ma una combinazione di K nodi.
# 2. Uso una ricorsione con indice pos.
# 3. A ogni passo decido se prendere o non prendere il candidato.
# 4. Quando len(parziale) == K, valuto la soluzione.
# 5. Uso nx.has_path per controllare se due nodi appartengono alla stessa componente.
# 6. Se esiste un path tra due nodi, sono nella stessa componente e non posso inserirli insieme.
# ============================================================


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getBestSetKComponentiDiverse(self, k):
        self._bestSet = []
        self._bestScore = float('inf')

        parziale = []
        candidati = list(self._graph.nodes)

        self._ricorsioneK(parziale, candidati, 0, k)

        return self._bestSet, self._bestScore

    def _ricorsioneK(self, parziale, candidati, pos, k):
        if len(parziale) == k:
            score = self._getScoreSet(parziale)

            if score < self._bestScore:
                self._bestSet = copy.deepcopy(parziale)
                self._bestScore = score

            return

        if pos >= len(candidati):
            return

        if len(parziale) + len(candidati) - pos < k:
            return

        candidato = candidati[pos]

        if self._canAdd(parziale, candidato):
            parziale.append(candidato)
            self._ricorsioneK(parziale, candidati, pos + 1, k)
            parziale.pop()

        self._ricorsioneK(parziale, candidati, pos + 1, k)

    def _canAdd(self, parziale, candidato):
        for n in parziale:
            if nx.has_path(self._graph, n, candidato):
                return False
        return True

    def _getScoreSet(self, parziale):
        valori = []
        for n in parziale:
            valori.append(n.oldest_driver_dob)

        valore_min = min(valori)
        valore_max = max(valori)

        return (valore_max - valore_min).days


# ============================================================
# CASO 10: FUNZIONE STANDARD PER CALCOLARE LO SCORE DI UN CAMMINO
# ============================================================
# Esempio:
# La traccia chiede di massimizzare il peso totale del percorso.
#
# Logica procedurale:
# 1. Il parziale è una lista di nodi.
# 2. Ogni arco attraversato è parziale[i] -> parziale[i+1].
# 3. Sommo i pesi degli archi.
# 4. Uso questa funzione dentro la ricorsione ogni volta che devo valutare il parziale.
# ============================================================


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def _getScore(self, parziale):
        score = 0
        for i in range(0, len(parziale)-1):
            score += self._graph[parziale[i]][parziale[i+1]]['weight']
        return score


# ============================================================
# CASO 11: VICINI PER GRAFO NON ORIENTATO E GRAFO ORIENTATO
# ============================================================
# Esempio:
# Devo sapere quale metodo usare per espandere il percorso.
#
# Logica procedurale:
# 1. Se il grafo è non orientato, uso neighbors.
# 2. Se il grafo è orientato e devo seguire il verso degli archi, uso successors.
# 3. Se il grafo è orientato e devo andare contro verso, uso predecessors.
# ============================================================


# ------------------------------------------------------------
# MODEL - grafo non orientato
# ------------------------------------------------------------

        for n in self._graph.neighbors(parziale[-1]):
            ...


# ------------------------------------------------------------
# MODEL - grafo orientato seguendo il verso
# ------------------------------------------------------------

        for n in self._graph.successors(parziale[-1]):
            ...


# ------------------------------------------------------------
# MODEL - grafo orientato contro verso
# ------------------------------------------------------------

        for n in self._graph.predecessors(parziale[-1]):
            ...


# ============================================================
# CASO 12: CONTROLLER STANDARD PER CHIAMARE LA RICORSIONE
# ============================================================
# Esempio:
# L'utente seleziona un nodo o inserisce un id e poi preme "Cerca percorso".
#
# Logica procedurale:
# 1. Leggo il nodo sorgente o l'id dalla View.
# 2. Controllo che il valore esista.
# 3. Chiamo il metodo pubblico del Model.
# 4. Pulisco l'area di output.
# 5. Stampo score e percorso.
# ============================================================


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleCercaPercorso(self, e):
        source = self._choiceNode
        # NON puntare al METODO (l'azione), punta alla VARIABILE (il dato salvato in choice)
        # Metodo = "Come si fa", Variabile = "Cosa ha scelto l'utente"

        if source is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: selezionare un nodo di partenza", color="red"))
            self._view.update_page()
            return

        path, score = self._model.getPercorsoDaNodo(source)

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"Percorso migliore trovato: score = {score}", color="red"))

        for nodo in path:
            self._view.txt_result.controls.append(ft.Text(str(nodo)))

        self._view.update_page()


# ============================================================
# CASO 13: CONTROLLER CON INPUT NUMERICO K
# ============================================================
# Esempio:
# L'utente inserisce K e il programma deve cercare una soluzione di lunghezza K o un set di K nodi.
#
# Logica procedurale:
# 1. Leggo K dalla View.
# 2. Controllo che non sia vuoto.
# 3. Converto K in int.
# 4. Chiamo il metodo pubblico del Model.
# 5. Stampo risultato e score.
# ============================================================


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleCercaK(self, e):
        k = self._view._txtK.value

        if k is None or k == "":
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: inserire un valore K", color="red"))
            self._view.update_page()
            return

        k = int(k)

        bestSet, score = self._model.getBestSetKComponentiDiverse(k)

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"Migliore soluzione trovata: score = {score}", color="red"))

        for n in bestSet:
            self._view.txt_result.controls.append(ft.Text(str(n)))

        self._view.update_page()


# ============================================================
# SCHEMA DECISIONALE RAPIDO
# ============================================================

# Traccia:
# "partendo dal nodo selezionato"
# Uso manager con parziale = [source] e una sola chiamata ricorsiva.

# Traccia:
# "trovare il cammino migliore nel grafo"
# Uso manager con for n in self._graph.nodes.

# Traccia:
# "nella componente connessa più grande"
# Calcolo max(nx.connected_components(...), key=len) e parto solo da quei nodi.

# Traccia:
# "nella componente del nodo selezionato"
# Uso nx.node_connected_component(self._graph, source).

# Traccia:
# "cammino più lungo" senza traguardo
# Aggiorno l'ottimo a ogni passo valido.

# Traccia:
# "peso massimo"
# Uso _getScore(parziale) e aggiorno se score > bestScore.

# Traccia:
# "pesi strettamente crescenti"
# Uso peso_corrente > peso_precedente.

# Traccia:
# "pesi strettamente decrescenti"
# Uso peso_corrente < peso_precedente.

# Traccia:
# "arrivare esattamente a destinazione"
# Aggiorno solo quando parziale[-1] == target e poi faccio return.

# Traccia:
# "lunghezza esatta K"
# Aggiorno solo quando len(parziale) == K e poi faccio return.

# Traccia:
# "peso massimo non superiore a una soglia"
# Se _getScore(parziale) > soglia, faccio return.

# Traccia:
# "scegliere K elementi"
# Uso ricorsione combinatoria con indice pos.

# Traccia:
# "componenti connesse diverse"
# Uso nx.has_path per verificare che i nodi non siano nella stessa componente.

# Attenzione:
# Se metto return dentro il for dopo il primo vicino valido, sto facendo greedy.
# Se voglio l'ottimo globale, normalmente non metto return dentro il for.
# ============================================================