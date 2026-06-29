# ============================================================
# REGOLA GENERALE: VICINI NELLA RICORSIONE
# ============================================================
# Se il grafo è NON orientato:
#     uso self._graph.neighbors(nodo)
#
# Se il grafo è ORIENTATO e devo rispettare il verso degli archi:
#     uso self._graph.successors(nodo)
#
# Se il grafo è ORIENTATO ma devo andare contro il verso degli archi:
#     uso self._graph.predecessors(nodo)
#
# Attenzione:
# In un nx.DiGraph, usare neighbors(nodo) di solito equivale ai successori,
# ma all'esame è più chiaro e sicuro scrivere successors()
# quando la traccia dice che bisogna rispettare il verso degli archi.
#
# Regola pratica da esame:
# - nx.Graph()   --> neighbors()
# - nx.DiGraph() --> successors() se seguo gli archi
# - nx.DiGraph() --> predecessors() se risalgo gli archi al contrario
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
# CASO 1: MANAGER CON NODO DI PARTENZA SELEZIONATO
# ============================================================
# Quando usarlo:
# - la traccia dice "partendo dal nodo selezionato".
# - il source arriva da Dropdown, TextField o scelta salvata nel Controller.
#
# Controlli:
# - nel Controller controllo che source non sia None.
# - nel Model controllo che source sia effettivamente nel grafo.
# ============================================================

# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPercorsoDaNodo(self, source):
        self._bestPath = []
        self._bestScore = 0

        if source is None:
            return [], 0
        if source not in self._graph.nodes:
            return [], 0

        parziale = [source]
        self._ricorsione(parziale)

        return self._bestPath, self._bestScore


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleCercaPercorsoDaNodo(self, e):
        source = self._choiceNode

        if source is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: selezionare un nodo di partenza", color="red"))
            self._view.update_page()
            return

        path, score = self._model.getPercorsoDaNodo(source)

        if path is None or len(path) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Nessun cammino trovato", color="red"))
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"Percorso migliore trovato: score = {score}", color="red"))
        for nodo in path:
            self._view.txt_result.controls.append(ft.Text(str(nodo)))
        self._view.update_page()


# ============================================================
# CASO 2: MANAGER CON CICLO SU TUTTI I NODI
# ============================================================
# Quando usarlo:
# - la traccia dice "trovare il cammino migliore nel grafo" senza dare un nodo di partenza.
#
# Logica:
# - ogni nodo puo' essere la partenza del cammino migliore.
# - inizializzo bestPath e bestScore una sola volta prima del for.
# - NON resetto bestPath dentro il ciclo.
# ============================================================

# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPercorsoMiglioreGrafo(self):
        self._bestPath = []
        self._bestScore = 0

        if len(self._graph.nodes) == 0:
            return [], 0

        for n in self._graph.nodes:
            parziale = [n]
            self._ricorsione(parziale)

        return self._bestPath, self._bestScore


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleCercaPercorsoMiglioreGrafo(self, e):
        path, score = self._model.getPercorsoMiglioreGrafo()

        if path is None or len(path) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Nessun cammino trovato. Verificare che il grafo sia stato creato.", color="red"))
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"Percorso migliore nel grafo: score = {score}", color="red"))
        for nodo in path:
            self._view.txt_result.controls.append(ft.Text(str(nodo)))
        self._view.update_page()


# ============================================================
# CASO 3: MANAGER LIMITATO A UNA COMPONENTE CONNESSA
# ============================================================
# Quando usarlo:
# - la traccia dice "nella componente connessa piu' grande".
# - oppure "nella componente del nodo selezionato".
#
# Nota:
# - connected_components funziona su grafi non orientati.
# - se il grafo e' orientato, valutare weakly_connected_components oppure convertire a non orientato.
# ============================================================

# ------------------------------------------------------------
# MODEL - componente connessa piu' grande
# ------------------------------------------------------------

    def getPercorsoMiglioreComponenteMaggiore(self):
        self._bestPath = []
        self._bestScore = 0

        if len(self._graph.nodes) == 0:
            return [], 0

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

        if source is None:
            return [], 0
        if source not in self._graph.nodes:
            return [], 0

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


# ------------------------------------------------------------
# CONTROLLER - componente piu' grande
# ------------------------------------------------------------

    def handleCercaComponenteMaggiore(self, e):
        path, score = self._model.getPercorsoMiglioreComponenteMaggiore()

        if path is None or len(path) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Nessun cammino trovato nella componente maggiore", color="red"))
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"Percorso migliore nella componente maggiore: score = {score}", color="red"))
        for nodo in path:
            self._view.txt_result.controls.append(ft.Text(str(nodo)))
        self._view.update_page()


# ------------------------------------------------------------
# CONTROLLER - componente del nodo selezionato
# ------------------------------------------------------------

    def handleCercaComponenteDiNodo(self, e):
        source = self._choiceNode

        if source is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: selezionare un nodo di partenza", color="red"))
            self._view.update_page()
            return

        path, score = self._model.getPercorsoMiglioreComponenteDiNodo(source)

        if path is None or len(path) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Nessun cammino trovato nella componente del nodo selezionato", color="red"))
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"Percorso migliore nella componente del nodo: score = {score}", color="red"))
        for nodo in path:
            self._view.txt_result.controls.append(ft.Text(str(nodo)))
        self._view.update_page()


# ============================================================
# CASO 4: CAMMINO LUNGO MASSIMO CON PESI STRETTAMENTE CRESCENTI
# ============================================================
# Quando usarlo:
# - la traccia dice "cammino semplice di lunghezza massima".
# - ogni arco successivo deve avere peso strettamente crescente.
#
# Logica:
# - non c'e' nodo destinazione.
# - non c'e' lunghezza fissa.
# - aggiorno l'ottimo a ogni passo valido.
# - terminazione implicita: quando non ci sono vicini validi, il for non entra.
# ============================================================

# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPercorsoCrescenteDaNodo(self, source):
        self._bestPath = []
        self._bestScore = 0

        if source is None:
            return [], 0
        if source not in self._graph.nodes:
            return [], 0

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


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleCercaPercorsoCrescente(self, e):
        source = self._choiceNode

        if source is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: selezionare un nodo di partenza", color="red"))
            self._view.update_page()
            return

        path, score = self._model.getPercorsoCrescenteDaNodo(source)

        if path is None or len(path) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Nessun cammino crescente trovato", color="red"))
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"Percorso crescente migliore: lunghezza = {score}", color="red"))
        for nodo in path:
            self._view.txt_result.controls.append(ft.Text(str(nodo)))
        self._view.update_page()


# ============================================================
# CASO 5: CAMMINO DI PESO MASSIMO CON PESI STRETTAMENTE DECRESCENTI
# ============================================================
# Quando usarlo:
# - la traccia dice "percorso di peso massimo".
# - ogni arco successivo deve avere peso strettamente decrescente.
# - un nodo puo' comparire una volta sola nel percorso.
#
# Logica:
# - score = somma dei pesi degli archi.
# - aggiorno l'ottimo a ogni passo valido.
# - controllo peso_corrente < peso_precedente.
# ============================================================

# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPercorsoDecrescentePesoMassimo(self, source):
        self._bestPath = []
        self._bestScore = 0

        if source is None:
            return [], 0
        if source not in self._graph.nodes:
            return [], 0

        parziale = [source]
        self._ricorsioneDecrescente(parziale)

        return self._bestPath, self._bestScore

    def _ricorsioneDecrescente(self, parziale):
        score = self._getScore(parziale)

        if score > self._bestScore:
            self._bestPath = copy.deepcopy(parziale)
            self._bestScore = score

        for n in self._graph.successors(parziale[-1]):
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


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleRicorsioneDecrescente(self, e):
        source = self._choiceNode

        if source is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: selezionare un nodo di partenza", color="red"))
            self._view.update_page()
            return

        path, score = self._model.getPercorsoDecrescentePesoMassimo(source)

        if path is None or len(path) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Nessun percorso trovato", color="red"))
            self._view.update_page()
            return

        # Usare questo controllo solo se la traccia pretende un percorso con almeno un arco.
        # Se anche il singolo nodo e' considerato soluzione valida, eliminare questo blocco.
        if len(path) == 1:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Nessun arco valido trovato a partire dal nodo selezionato", color="red"))
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"Percorso di peso massimo trovato: score = {score}", color="red"))

        dettagli = self._model.getPathDetails(path)
        for d in dettagli:
            self._view.txt_result.controls.append(ft.Text(f"{d[0]} --> {d[1]} peso={d[2]}"))

        self._view.update_page()


# ============================================================
# CASO 6: CAMMINO CON DESTINAZIONE FISSA
# ============================================================
# Quando usarlo:
# - la traccia dice "da source a target".
# - la soluzione e' valida solo se termina nel nodo destinazione.
#
# Logica:
# - aggiorno bestPath solo quando parziale[-1] == target.
# - quando arrivo a target, faccio return.
# ============================================================

# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPercorsoConDestinazione(self, source, target):
        self._bestPath = []
        self._bestScore = 0
        self._target = target

        if source is None or target is None:
            return [], 0
        if source not in self._graph.nodes or target not in self._graph.nodes:
            return [], 0

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


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleCercaDestinazione(self, e):
        source = self._sourceValue
        target = self._targetValue

        if source is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: selezionare un nodo di partenza", color="red"))
            self._view.update_page()
            return

        if target is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: selezionare un nodo di destinazione", color="red"))
            self._view.update_page()
            return

        path, score = self._model.getPercorsoConDestinazione(source, target)

        if path is None or len(path) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Nessun cammino trovato tra i due nodi selezionati", color="red"))
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"Percorso migliore da {source} a {target}: score = {score}", color="red"))
        for nodo in path:
            self._view.txt_result.controls.append(ft.Text(str(nodo)))
        self._view.update_page()


# ============================================================
# CASO 7: CAMMINO CON LUNGHEZZA ESATTA K
# ============================================================
# Quando usarlo:
# - la traccia dice "cammino lungo esattamente K nodi".
# - se parla di K archi (passi), controllare len(parziale)-1 == K.
#
# Controlli:
# - K arriva spesso da TextField, quindi serve try/except nel Controller.
# ============================================================

# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPercorsoLunghezzaK(self, source, k):
        self._bestPath = []
        self._bestScore = 0
        self._k = k

        if source is None:
            return [], 0
        if source not in self._graph.nodes:
            return [], 0
        if k <= 0:
            return [], 0

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


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleCercaLunghezzaK(self, e):
        source = self._choiceNode
        k = self._view._txtK.value

        if source is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: selezionare un nodo di partenza", color="red"))
            self._view.update_page()
            return

        if k is None or k == "":
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: inserire un valore K", color="red"))
            self._view.update_page()
            return

        try:
            k = int(k)
        except ValueError:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: K deve essere un numero intero", color="red"))
            self._view.update_page()
            return

        if k <= 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: K deve essere maggiore di zero", color="red"))
            self._view.update_page()
            return

        path, score = self._model.getPercorsoLunghezzaK(source, k)

        if path is None or len(path) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Nessun cammino trovato con la lunghezza richiesta", color="red"))
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"Cammino migliore di lunghezza {k}: score = {score}", color="red"))
        for nodo in path:
            self._view.txt_result.controls.append(ft.Text(str(nodo)))
        self._view.update_page()


# ============================================================
# CASO 8: CAMMINO CON SERBATOIO / BUDGET LIMITATO
# ============================================================
# Quando usarlo:
# - la traccia dice "peso totale non superiore a X".
# - massimizzare lunghezza o altro punteggio rispettando una soglia.
# ============================================================

# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPercorsoConBudget(self, source, maxPeso):
        self._bestPath = []
        self._bestScore = 0
        self._maxPeso = maxPeso

        if source is None:
            return [], 0
        if source not in self._graph.nodes:
            return [], 0
        if maxPeso <= 0:
            return [], 0

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


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleCercaBudget(self, e):
        source = self._choiceNode
        maxPeso = self._view._txtMaxPeso.value

        if source is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: selezionare un nodo di partenza", color="red"))
            self._view.update_page()
            return

        if maxPeso is None or maxPeso == "":
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: inserire il valore massimo consentito", color="red"))
            self._view.update_page()
            return

        try:
            maxPeso = float(maxPeso)
        except ValueError:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: il valore massimo deve essere numerico", color="red"))
            self._view.update_page()
            return

        if maxPeso <= 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: il valore massimo deve essere maggiore di zero", color="red"))
            self._view.update_page()
            return

        path, score = self._model.getPercorsoConBudget(source, maxPeso)

        if path is None or len(path) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Nessun cammino trovato con il budget inserito", color="red"))
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"Cammino migliore con budget {maxPeso}: lunghezza = {score}", color="red"))
        for nodo in path:
            self._view.txt_result.controls.append(ft.Text(str(nodo)))
        self._view.update_page()


# ============================================================
# CASO 9: SELEZIONARE K NODI CON VINCOLO DI COMPONENTI DIVERSE
# ============================================================
# Quando usarlo:
# - non sto costruendo un cammino, ma una combinazione di K nodi.
# - esempio: scegliere K costruttori appartenenti a componenti diverse.
#
# Logica:
# - uso indice pos.
# - a ogni passo scelgo se prendere o saltare il candidato.
# - quando len(parziale) == K valuto la soluzione.
# ============================================================

# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getBestSetKComponentiDiverse(self, k):
        self._bestSet = []
        self._bestScore = float('inf')

        if len(self._graph.nodes) == 0:
            return [], float('inf')
        if k <= 0:
            return [], float('inf')

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


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleCercaKComponentiDiverse(self, e):
        k = self._view._txtK.value

        if k is None or k == "":
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: inserire un valore K", color="red"))
            self._view.update_page()
            return

        try:
            k = int(k)
        except ValueError:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: K deve essere un numero intero", color="red"))
            self._view.update_page()
            return

        if k <= 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: K deve essere maggiore di zero", color="red"))
            self._view.update_page()
            return

        bestSet, score = self._model.getBestSetKComponentiDiverse(k)

        if bestSet is None or len(bestSet) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Nessuna soluzione trovata con i vincoli inseriti", color="red"))
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"Migliore soluzione trovata: score = {score}", color="red"))
        for n in bestSet:
            self._view.txt_result.controls.append(ft.Text(str(n)))
        self._view.update_page()


# ============================================================
# CASO 10: FUNZIONE STANDARD PER CALCOLARE LO SCORE DI UN CAMMINO
# ============================================================
# Quando usarla:
# - la traccia chiede di massimizzare il peso totale del percorso.
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
# CASO 11: STAMPARE UN PERCORSO CON ARCHI E PESI
# ============================================================
# Per evitare di accedere direttamente a self._graph dal Controller.
# ============================================================

# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getPathDetails(self, path):
        dettagli = []

        if path is None or len(path) < 2:
            return dettagli

        for i in range(0, len(path)-1):
            n1 = path[i]
            n2 = path[i+1]
            peso = self._graph[n1][n2]['weight']
            dettagli.append((n1, n2, peso))

        return dettagli

# ------------------------------------------------------------
# CONTROLLER - stampa path con dettagli
# ------------------------------------------------------------

path, score = self._model.getPercorso(...)

if path is None or len(path) == 0:
    self._view.txt_result.controls.clear()
    self._view.txt_result.controls.append(
        ft.Text("Nessun percorso trovato", color="red")
    )
    self._view.update_page()
    return

dettagli = self._model.getPathDetails(path)

self._view.txt_result.controls.clear()
self._view.txt_result.controls.append(
    ft.Text(f"Percorso trovato con score = {score}", color="red")
)

self._view.txt_result.controls.append(ft.Text("Nodi attraversati:"))
for nodo in path:
    self._view.txt_result.controls.append(ft.Text(str(nodo)))

self._view.txt_result.controls.append(ft.Text("Archi attraversati:"))
for n1, n2, peso in dettagli:
    self._view.txt_result.controls.append(
        ft.Text(f"{n1} --> {n2} | peso: {peso}")
    )

self._view.update_page()


# ============================================================
#  RICORSIONE CON NODO PARTENZA, DESTINAZIONE ED ESATTAMENTE K ARCHI
# ============================================================
# Caso:
# Devo trovare un cammino che:
# - parte da source;
# - termina in target;
# - ha esattamente K archi;
# - rispetta il verso degli archi;
# - non ripete nodi;
# - massimizza la somma dei pesi.
#
# Attenzione:
# K archi significa:
#
#     len(parziale) - 1 == K
#
# perché se ho:
#     A -> B -> C
#
# ho 3 nodi ma 2 archi.
# ============================================================

# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

def getPercorso(self, sourceStr, targetStr, k):
    self._bestPath = []
    self._bestScore = -float("inf")
    self._target = None
    self._k = k

    if sourceStr is None or targetStr is None:
        return [], 0

    if k <= 0:
        return [], 0

    try:
        sourceId = int(sourceStr)
        targetId = int(targetStr)
    except ValueError:
        return [], 0

    source = self._idMapProducts.get(sourceId)
    target = self._idMapProducts.get(targetId)

    if source is None or target is None:
        return [], 0

    if source not in self._graph.nodes or target not in self._graph.nodes:
        return [], 0

    self._target = target

    parziale = [source]
    self._ricorsione(parziale)

    if len(self._bestPath) == 0:
        return [], 0

    return self._bestPath, self._bestScore


def _ricorsione(self, parziale):
    if len(parziale) > self._k:
        return

    if parziale[-1] == self._target:
        if len(parziale) == self._k:
            score = self._getScore(parziale)

            if score > self._bestScore:
                self._bestPath = copy.deepcopy(parziale)
                self._bestScore = score

        return

    if len(parziale) == self._k:
        return

    for n in self._graph.successors(parziale[-1]):
        if n not in parziale:
            parziale.append(n)
            self._ricorsione(parziale)
            parziale.pop()


def _getScore(self, parziale):
    score = 0

    for i in range(0, len(parziale) - 1):
        score += self._graph[parziale[i]][parziale[i + 1]]["weight"]

    return score

# ------------------------------------------------------------
# CONTROLLER - source, target e lunghezza esatta K nodi
# ------------------------------------------------------------

def handleCercaCammino(self, e):
    source = self._view._ddProdStart.value
    target = self._view._ddProdEnd.value
    k = self._view._txtInLun.value

    if source is None:
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text("Errore: selezionare un prodotto di partenza", color="red")
        )
        self._view.update_page()
        return

    if target is None:
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text("Errore: selezionare un prodotto di destinazione", color="red")
        )
        self._view.update_page()
        return

    if k is None or k == "":
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text("Errore: inserire la lunghezza del cammino", color="red")
        )
        self._view.update_page()
        return

    try:
        k = int(k)
    except ValueError:
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text("Errore: la lunghezza deve essere un numero intero", color="red")
        )
        self._view.update_page()
        return

    if k <= 0:
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text("Errore: la lunghezza deve essere maggiore di zero", color="red")
        )
        self._view.update_page()
        return

    path, score = self._model.getPercorso(source, target, k)

    if path is None or len(path) == 0:
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text("Nessun cammino trovato tra i due prodotti con la lunghezza richiesta", color="red")
        )
        self._view.update_page()
        return

    self._view.txt_result.controls.clear()
    self._view.txt_result.controls.append(
        ft.Text(f"Percorso migliore trovato con score = {score} e lunghezza = {k}", color="red")
    )

    for nodo in path:
        self._view.txt_result.controls.append(ft.Text(str(nodo)))

    self._view.update_page()

# Nota se la traccia dice K archi e non K nodi, allora devi solo cambiare queste condizioni:
    # al posto di:
    len(parziale) == self._k
    len(parziale) > self._k

    # usare:
    len(parziale) - 1 == self._k
    len(parziale) - 1 > self._k

# ============================================================
#  RICORSIONE CON NODO PARTENZA, DESTINAZIONE ED ESATTAMENTE K ARCHI
# ============================================================
# Caso:
# Devo trovare un cammino che:
# - parte da source;
# - termina in target;
# - ha esattamente K archi;
# - rispetta il verso degli archi;
# - non ripete nodi;
# - massimizza la somma dei pesi.
#
# Attenzione:
# K archi significa:
#
#     len(parziale) - 1 == K
#
# perché se ho:
#     A -> B -> C
#
# ho 3 nodi ma 2 archi.
# ============================================================


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

def getPercorso(self, source, target, k):
    self._bestPath = []
    self._bestScore = -float("inf")
    self._target = None
    self._k = k

    if source is None or target is None:
        return [], 0

    if k <= 0:
        return [], 0

    try:
        sourceId = int(source)
        targetId = int(target)
    except ValueError:
        return [], 0

    source = self._idMapProducts.get(sourceId)
    target = self._idMapProducts.get(targetId)

    if source is None or target is None:
        return [], 0

    if source not in self._graph.nodes or target not in self._graph.nodes:
        return [], 0

    if source == target:
        return [], 0

    self._target = target

    parziale = [source]
    self._ricorsione(parziale)

    if len(self._bestPath) == 0:
        return [], 0

    return self._bestPath, self._bestScore


def _ricorsione(self, parziale):
    archi_usati = len(parziale) - 1

    # Se ho superato il numero di archi richiesto, ramo inutile.
    if archi_usati > self._k:
        return

    # Se sono arrivata al target, accetto il cammino solo se ho esattamente K archi.
    # Se arrivo al target troppo presto, mi fermo comunque.
    if parziale[-1] == self._target:
        if archi_usati == self._k:
            score = self._getScore(parziale)

            if score > self._bestScore:
                self._bestPath = copy.deepcopy(parziale)
                self._bestScore = score

        return

    # Se ho già usato K archi ma non sono sul target, il cammino non è valido.
    if archi_usati == self._k:
        return

    # Grafo diretto:
    # uso successors per rispettare il verso degli archi.
    for n in self._graph.successors(parziale[-1]):
        if n not in parziale:
            parziale.append(n)
            self._ricorsioneKArchi(parziale)
            parziale.pop()


def _getScore(self, parziale):
    score = 0

    for i in range(0, len(parziale) - 1):
        score += self._graph[parziale[i]][parziale[i + 1]]["weight"]

    return score

# ============================================================
# CONDIZIONE: OGNI NOSO PUÒ ESSERE ATTRAVERSATO UNA SOLA VOLTA
# ============================================================

for n in self._graph.neighbors(parziale[-1]):
    if n not in parziale:
        parziale.append(n)

# ============================================================
# CASO: CAMMINO MIGLIORE CON CARATTERISTICA STRETTAMENTE CRESCENTE
# ============================================================
# Esempio:
# Da un nodo posso spostarmi solo verso un nodo con densità di popolazione
# strettamente crescente.
#
# Caratteristica:
#     densità = Population / Area
#
# Score da massimizzare:
#     somma pesi archi / distanza totale percorsa
#
# Distanza tra due nodi:
#     n1.distance_HV(n2)
#
# Logica procedurale:
# 1. Non ho un nodo source scelto dall'utente.
# 2. Non ho un nodo target.
# 3. Non ho una lunghezza K.
# 4. Quindi provo tutti i nodi come possibile partenza.
# 5. Il grafo è non orientato, quindi uso neighbors().
# 6. Il vincolo direzionale viene imposto manualmente:
#       caratteristica_nuova > caratteristica_corrente
# 7. Ogni cammino valido con almeno un arco può essere una soluzione.
# 8. Aggiorno il best se lo score migliora.
# ============================================================

# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

def getPercorso(self):
    self._bestPath = []
    self._bestScore = -float("inf")

    if len(self._graph.nodes) == 0:
        return [], 0

    for n in self._graph.nodes:
        parziale = [n]
        self._ricorsione(parziale)

    if len(self._bestPath) == 0:
        return [], 0

    return self._bestPath, self._bestScore


def _ricorsione(self, parziale):
    if len(parziale) > 1:
        score = self._getScore(parziale)

        if score > self._bestScore:
            self._bestPath = copy.deepcopy(parziale)
            self._bestScore = score

    for n in self._graph.neighbors(parziale[-1]):
        if n not in parziale:
            valore_corrente = self.getDensita(parziale[-1])
            valore_nuovo = self.getDensita(n)

            if valore_nuovo > valore_corrente:
                parziale.append(n)
                self._ricorsione(parziale)
                parziale.pop()


def _getScore(self, parziale):
    peso_totale = 0
    distanza_totale = 0

    for i in range(0, len(parziale) - 1):
        n1 = parziale[i]
        n2 = parziale[i + 1]

        peso_totale += self._graph[n1][n2]["weight"]
        distanza_totale += n1.distance_HV(n2)

    if distanza_totale == 0:
        return 0

    return peso_totale / distanza_totale


def getDensita(self, stato):
    if stato.Area == 0:
        return 0

    return stato.Population / stato.Area


def getPathDetails(self, path):
    dettagli = []

    if path is None or len(path) < 2:
        return dettagli

    for i in range(0, len(path) - 1):
        n1 = path[i]
        n2 = path[i + 1]

        peso = self._graph[n1][n2]["weight"]
        distanza = n1.distance_HV(n2)

        dettagli.append((n1, n2, peso, distanza))

    return dettagli

# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

def handle_path(self, e):
    path, score = self._model.getPercorso()

    self._view.txt_result2.controls.clear()

    if path is None or len(path) == 0:
        self._view.txt_result2.controls.append(
            ft.Text("Nessun percorso trovato", color="red")
        )
        self._view.update_page()
        return

    self._view.txt_result2.controls.append(
        ft.Text(f"Punteggio totale del percorso: {score:.4f}", color="red")
    )

    self._view.txt_result2.controls.append(
        ft.Text("Stati attraversati:")
    )

    for stato in path:
        densita = self._model.getDensita(stato)
        self._view.txt_result2.controls.append(
            ft.Text(f"{stato} - densità: {densita:.4f}")
        )

    dettagli = self._model.getPathDetails(path)

    self._view.txt_result2.controls.append(
        ft.Text("Archi attraversati:")
    )

    for n1, n2, peso, distanza in dettagli:
        self._view.txt_result2.controls.append(
            ft.Text(f"{n1} --> {n2} | peso: {peso:.2f} | distanza: {distanza:.2f}")
        )

    self._view.update_page()
# ============================================================
# VARIANTE GENERALE: CAMBIO SOLO LA CARATTERISTICA
# ============================================================
# Se in un altro esercizio il vincolo non è sulla densità ma su un'altra
# caratteristica, lascio uguale la struttura e cambio solo la funzione
# che calcola il valore del nodo.
#
# Esempi:
# - anno crescente
# - popolazione crescente
# - vendite crescenti
# - prezzo crescente
# - durata crescente
# - data crescente
#
# Dentro la ricorsione resta:
#
#     valore_corrente = self.getValore(parziale[-1])
#     valore_nuovo = self.getValore(n)
#
#     if valore_nuovo > valore_corrente:
#         ...
# ============================================================

def getValore(self, nodo):
    return nodo.attributo_da_confrontare


# ============================================================
# SCHEMA DECISIONALE RAPIDO
# ============================================================
# "partendo dal nodo selezionato"
#     -> manager con parziale = [source]
#     -> Controller controlla source is None.
#
# "migliore nel grafo"
#     -> manager con for n in self._graph.nodes.
#     -> Controller controlla path vuoto.
#
# "componente connessa piu' grande"
#     -> max(nx.connected_components(...), key=len).
#     -> Model controlla grafo vuoto.
#
# "componente del nodo selezionato"
#     -> nx.node_connected_component(self._graph, source).
#     -> Controller controlla source.
#
# "cammino piu' lungo" senza traguardo
#     -> aggiorno ottimo a ogni passo valido.
#
# "peso massimo"
#     -> uso _getScore(parziale).
#
# "pesi crescenti"
#     -> peso_corrente > peso_precedente.
#
# "pesi decrescenti"
#     -> peso_corrente < peso_precedente.
#
# "destinazione fissa"
#     -> aggiorno solo quando parziale[-1] == target.
#     -> Controller controlla source e target.
#
# "lunghezza esatta K"
#     -> aggiorno solo quando len(parziale) == K.
#     -> Controller controlla K.
#
# "budget/soglia"
#     -> se _getScore(parziale) > soglia, faccio return.
#     -> Controller controlla valore numerico.
#
# "scegliere K elementi"
#     -> ricorsione combinatoria con indice pos.
#     -> Controller controlla K e bestSet vuoto.
#
# Attenzione:
# - return dentro il for dopo il primo vicino valido = GREEDY.
# - se voglio l'ottimo globale, normalmente NON metto return dentro il for.
#
# Regola controlli:
# Ogni volta che il Controller chiama il Model usando input utente,
# controllo prima gli input e poi controllo se la soluzione restituita e' vuota.
# ============================================================
