# ============================================================
# 04_STAMPA_DETTAGLI.py
# ============================================================

# ============================================================
# CASO 1: STAMPARE GLI ARCHI DI PESO MAGGIORE
# ============================================================
# Esempio:
# Dopo aver creato il grafo, il programma deve stampare i 3 archi con peso maggiore.
#
# Logica procedurale:
# 1. Nel Model uso la lista degli archi già salvata durante il popolamento del grafo.
# 2. Ordino la lista in base al peso in ordine decrescente.
# 3. Restituisco solo i primi 3 archi.
# 4. Nel Controller pulisco l'area di output.
# 5. Chiamo il metodo del Model e stampo ogni arco usando il metodo __str__ del DTO Arco.
#
# Quando usare questo caso:
# quando durante il popolamento degli archi ho salvato anche una lista di oggetti Arco,
# per esempio self._lista_archi.append(e).
# ============================================================

# ------------------------------------------------------------
# MODEL - INIT: inizializzare la lista degli archi
# ------------------------------------------------------------

        self._lista_archi = []

# ------------------------------------------------------------
# MODEL - BUILDGRAPH: salvare ogni arco nella lista degli archi
# ------------------------------------------------------------

        for e in allEdges:
            self._graph.add_edge(e.d1, e.d2, weight=e.peso)
            self._lista_archi.append(e)


    # ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getTop3Archi(self):
        self._lista_archi.sort(key=lambda x: x.peso, reverse=True)
        return self._lista_archi[:3]


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleDettagli(self, e):
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Archi di peso maggiore: ", color="red"))
        top_archi = self._model.getTop3Archi()
        for arco in top_archi:
            self._view.txt_result.controls.append(ft.Text(str(arco)))
        self._view.update_page()


# ============================================================
# CASO 2: STAMPARE COMPONENTI CONNESSE E NODI DELLA COMPONENTE PIU GRANDE
# ============================================================
# Esempio:
# Il programma deve stampare:
# - il numero di componenti connesse del grafo;
# - la componente connessa più grande;
# - i nodi della componente più grande ordinati per grado decrescente.
#
# Logica procedurale:
# 1. Nel Model uso nx.connected_components per ottenere tutte le componenti connesse.
# 2. Ogni componente è un insieme di nodi.
# 3. Prendo la componente più grande usando max(componenti, key=len).
# 4. Ordino i nodi della componente più grande in base al grado.
# 5. Nel Controller stampo prima il numero di componenti.
# 6. Poi stampo i nodi della componente più grande.
# 7. Infine stampo gli stessi nodi con il grado in ordine decrescente.
#
# Quando usare questo caso:
# quando il grafo è non orientato e voglio studiare le isole separate del grafo.
# ============================================================


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getComponentiConnesseDetails(self):
        componenti = list(nx.connected_components(self._graph))
        largest = max(componenti, key=len)
        nodi_ordinati = sorted(largest, key=lambda n: self._graph.degree(n), reverse=True)

        return len(componenti), largest, nodi_ordinati


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleComponentiConnesse(self, e):
        self._view.txt_result.controls.clear()

        nComp, bComp, nodes = self._model.getComponentiConnesseDetails()
        self._view.txt_result.controls.append(ft.Text(f"Il grafo ha {nComp} componenti connesse", color="red"))
        self._view.txt_result.controls.append(ft.Text(f"Componente più grande ({len(nodes)} nodi): ", color="red"))
        for node in nodes:
            self._view.txt_result.controls.append(ft.Text(f"{node.driverRef} ({node.driverId}) -- DoB: {node.dob}"))

        self._view.txt_result.controls.append(ft.Text(f"Componente connessa in ordine decrescente: ", color="red"))
        for node in nodes:
            grado = self._model._graph.degree(node)
            self._view.txt_result.controls.append(ft.Text(f"{node.driverRef} ({node.driverId}) -- DoB: {node.dob} (grado={grado})"))
        self._view.update_page()


# ============================================================
# CASO 3: STAMPARE I 5 NODI CON SCORE MASSIMO IN UN GRAFO ORIENTATO
# ============================================================
# Esempio:
# Il programma deve visualizzare i 5 prodotti più venduti.
# Lo score di un prodotto è:
# somma dei pesi degli archi uscenti - somma dei pesi degli archi entranti.
#
# Logica procedurale:
# 1. Questo caso si usa su grafi orientati e pesati.
# 2. Per ogni nodo calcolo il peso totale degli archi uscenti.
# 3. Per ogni nodo calcolo il peso totale degli archi entranti.
# 4. Lo score è uscenti - entranti.
# 5. Inserisco ogni nodo in una lista di tuple del tipo (nodo, score).
# 6. Ordino la lista in ordine decrescente rispetto allo score.
# 7. Restituisco i primi 5 elementi.
#
# Nota:
# Questa versione è più compatta e veloce da implementare rispetto al ciclo manuale su out_edges e in_edges,
# perché NetworkX calcola direttamente i gradi pesati tramite weight='weight'.
# ============================================================


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getBestSellers(self):
        listBestSellers = []
        for n in self._graph.nodes:
            uscenti = self._graph.out_degree(n, weight='weight')
            entranti = self._graph.in_degree(n, weight='weight')
            score = uscenti - entranti
            listBestSellers.append((n, score))

        listBestSellers.sort(key=lambda x: x[1], reverse=True)
        return listBestSellers[0:5]


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleBestProdotti(self, e):
        bestProdotti = self._model.getBestSellers()
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Prodotti maggiormente profittevoli: "))
        for p in bestProdotti:
            self._view.txt_result.controls.append(ft.Text(f"{p[0]} - score = {p[1]}"))
        self._view.update_page()


# ============================================================
# CASO 4: STAMPARE IL NODO PIU INFLUENTE IN UN GRAFO ORIENTATO
# ============================================================
# Esempio:
# Il programma deve trovare un solo nodo massimo, per esempio l'artista più influente.
# L'influenza è calcolata come:
# peso totale degli archi uscenti - peso totale degli archi entranti.
#
# Logica procedurale:
# 1. Questo caso è simile al caso dei best sellers, ma restituisce solo il nodo migliore.
# 2. Inizializzo max_influenza a -infinito per gestire anche score negativi.
# 3. Per ogni nodo calcolo archi uscenti pesati e archi entranti pesati.
# 4. Se il valore trovato è maggiore del massimo attuale, aggiorno il nodo migliore.
# 5. Restituisco il nodo migliore e il valore della sua influenza.
#
# Quando usare questo caso:
# quando l'esercizio chiede il migliore assoluto e non una classifica dei primi k nodi.
# ============================================================


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getArtistaPiuInfluente(self):
        best_artist = None
        max_influenza = -float('inf')

        for nodo in self._graph.nodes:
            uscenti = self._graph.out_degree(nodo, weight='weight')
            entranti = self._graph.in_degree(nodo, weight='weight')
            influenza = uscenti - entranti

            if influenza > max_influenza:
                max_influenza = influenza
                best_artist = nodo

        return best_artist, max_influenza


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleArtistaPiuInfluente(self, e):
        best_artist, max_influenza = self._model.getArtistaPiuInfluente()
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Artista più influente: ", color="red"))
        self._view.txt_result.controls.append(ft.Text(f"{best_artist} - influenza = {max_influenza}"))
        self._view.update_page()


# ============================================================
# CASO 5: STAMPARE I VICINI ORDINATI PER PESO DECRESCENTE
# ============================================================
# Esempio:
# Data una squadra selezionata dall'utente, il programma deve stampare:
# - tutte le squadre adiacenti;
# - il peso dell'arco corrispondente;
# - l'elenco ordinato in ordine decrescente di peso.
#
# Logica procedurale:
# 1. Nel Model recupero i vicini del nodo sorgente.
# 2. Per ogni vicino costruisco una tupla del tipo (vicino, peso_arco).
# 3. Il peso dell'arco si recupera con self._grafo[source][v]['weight'].
# 4. Ordino la lista di tuple per peso decrescente.
# 5. Nel Controller chiamo il Model passando il nodo scelto dall'utente.
# 6. Stampo il numero di vicini e poi ogni vicino con il peso.
#
# Nota:
# Se nel progetto il grafo si chiama self._graph invece di self._grafo,
# sostituire self._grafo con self._graph nel metodo del Model.
# ============================================================


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getViciniOrdinati(self, source):
        vicini = self._grafo.neighbors(source)
        viciniTupla = []
        for v in vicini:
            viciniTupla.append((v, self._grafo[source][v]['weight']))
        viciniTupla.sort(key=lambda x: x[1], reverse=True)
        return viciniTupla


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleViciniOrdinati(self, e):
        viciniTupla = self._model.getViciniOrdinati(self._choiceTeam)
        self._view._txt_result.controls.clear()
        self._view._txt_result.controls.append(
            ft.Text(f"Il nodo {self._choiceTeam} ha {len(viciniTupla)} vicini",
                    color="green"))
        for v in viciniTupla:
            self._view._txt_result.controls.append(ft.Text(f"{v[0]} - peso {v[1]}"))
        self._view.update_page()

