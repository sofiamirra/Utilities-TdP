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
    # Nel buildGraph, subito dopo clear del grafo, pulisco anche la lista degli archi.
    def buildGraph(self, ...):
        self._graph.clear()
        self._lista_archi.clear()

        # Nel buildGraph popolo la lista degli archi.
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

# ============================================================
# CASO BFS / DFS - VISITE DEL GRAFO E CAMMINO LUNGO DA NODO
# ============================================================
# Esempio:
# La traccia chiede:
# "Partendo dal nodo selezionato, visualizzare il cammino più lungo
# scegliendo l'algoritmo di visita più opportuno tra BFS e DFS".
#
# Questo NON è il caso della ricorsione/backtracking.
# Questo è il caso di una VISITA del grafo.
#
# ------------------------------------------------------------
# QUANDO USARE BFS
# ------------------------------------------------------------
# BFS = visita in ampiezza.
# Usa BFS quando:
# - vuoi visitare il grafo per livelli;
# - vuoi esplorare prima i nodi più vicini alla sorgente;
# - vuoi trovare cammini con pochi archi in un grafo non pesato;
# - la traccia parla di "nodi più vicini", "distanza minima", "livelli".
#
# ------------------------------------------------------------
# QUANDO USARE DFS
# ------------------------------------------------------------
# DFS = visita in profondità.
# Usa DFS quando:
# - vuoi scendere il più possibile lungo un ramo;
# - la traccia parla di "cammino lungo" usando una visita;
# - vuoi costruire un albero di visita profondo;
# - nella simulazione sugli ordini, per il punto "Cerca Percorso Massimo",
#   la scelta naturale era DFS FromTree.
#
# ------------------------------------------------------------
# DIFFERENZA TRA NodesFromEdges E NodesFromTree
# ------------------------------------------------------------
#
# 1. NodesFromEdges:
#    uso:
#       nx.bfs_edges(self._graph, source)
#       nx.dfs_edges(self._graph, source)
#
#    Ottengo gli archi attraversati dalla visita:
#       (padre, figlio)
#
#    Da questi archi posso ricavare i nodi visitati:
#       nodes = [source]
#       nodes.append(edge[1])
#
#    Quando usarlo:
#    - se devo solo stampare gli archi/nodi visitati;
#    - se la traccia chiede semplicemente l'ordine di visita.
#
#
# 2. NodesFromTree:
#    uso:
#       nx.bfs_tree(self._graph, source)
#       nx.dfs_tree(self._graph, source)
#
#    Ottengo un albero di visita.
#
#    Da questo posso:
#    - stampare i nodi visitati;
#    - stampare gli archi dell'albero;
#    - ricostruire il cammino source -> nodo;
#    - cercare il cammino più lungo nell'albero di visita.
#
#    Quando usarlo:
#    - se la traccia chiede un cammino partendo da source;
#    - se devo ricostruire il percorso;
#    - se devo fare come nella simulazione sugli ordini.
#
# ------------------------------------------------------------
# NOTA SUL DROPDOWN
# ------------------------------------------------------------
# Nelle simulazioni d'esame il Dropdown di solito restituisce l'ID del nodo,
# non l'oggetto nodo.
#
# Controller:
#       sourceStr = self._view._ddNode.value
#
# Model:
#       source = self._idMap[int(sourceStr)]
#
# In questo blocco uso self._idMap come nome generico.
# Nell'esame puoi sostituirlo con:
#       self._idMapOrders
#       self._idMapDrivers
#       self._idMapArtists
#       self._idMapProducts
#       ecc.
# ============================================================


# ------------------------------------------------------------
# IMPORT DA AVERE NEL MODEL
# ------------------------------------------------------------

import copy
import networkx as nx


# ============================================================
# MODEL - FUNZIONE DI SUPPORTO: recuperare nodo da ID Dropdown
# ============================================================
# Logica:
# 1. Il Dropdown restituisce sourceStr.
# 2. sourceStr di solito è una stringa, anche se rappresenta un intero.
# 3. Provo a convertirlo in int.
# 4. Recupero il nodo vero dalla idMap.
# 5. Il grafo contiene oggetti, quindi BFS/DFS devono partire dall'oggetto.
#
# Adattare SOLO questa funzione se la mappa ha un nome diverso.
# ============================================================

    def _getNodeFromDropdownId(self, sourceStr):
        if sourceStr is None:
            return None

        try:
            sourceId = int(sourceStr)
        except ValueError:
            sourceId = sourceStr

        source = self._idMap.get(sourceId)

        return source


# ============================================================
# CASO 1: BFS NodesFromEdges
# ============================================================
# Cosa fa:
# - parte dal nodo source;
# - esegue una BFS;
# - prende gli archi di scoperta della BFS;
# - costruisce la lista dei nodi visitati a partire dagli archi.
#
# Restituisce:
# - nodes = nodi visitati;
# - edges = archi attraversati dalla visita.
#
# Quando usarlo:
# - quando voglio stampare l'ordine di visita BFS;
# - quando mi interessano anche gli archi attraversati dalla visita.
# ============================================================

    def getBFSNodesFromEdgesById(self, sourceStr):
        source = self._getNodeFromDropdownId(sourceStr)

        if source is None:
            return [], []

        if source not in self._graph.nodes:
            return [], []

        nodes = [source]
        edges = list(nx.bfs_edges(self._graph, source))

        for edge in edges:
            nodes.append(edge[1])

        return nodes, edges


# ============================================================
# CASO 2: DFS NodesFromEdges
# ============================================================
# Cosa fa:
# - parte dal nodo source;
# - esegue una DFS;
# - prende gli archi di scoperta della DFS;
# - costruisce la lista dei nodi visitati a partire dagli archi.
#
# Restituisce:
# - nodes = nodi visitati;
# - edges = archi attraversati dalla visita.
#
# Quando usarlo:
# - quando voglio stampare l'ordine di visita DFS;
# - quando mi interessano anche gli archi attraversati dalla visita.
# ============================================================

    def getDFSNodesFromEdgesById(self, sourceStr):
        source = self._getNodeFromDropdownId(sourceStr)

        if source is None:
            return [], []

        if source not in self._graph.nodes:
            return [], []

        nodes = [source]
        edges = list(nx.dfs_edges(self._graph, source))

        for edge in edges:
            nodes.append(edge[1])

        return nodes, edges


# ============================================================
# CASO 3: BFS NodesFromTree
# ============================================================
# Cosa fa:
# - costruisce l'albero BFS partendo dal nodo source;
# - prende i nodi dell'albero;
# - prende gli archi dell'albero.
#
# Restituisce:
# - nodes = nodi dell'albero BFS;
# - edges = archi dell'albero BFS.
#
# Quando usarlo:
# - quando voglio l'albero di visita BFS;
# - quando voglio vedere i nodi raggiunti per livelli;
# - quando eventualmente voglio ricostruire cammini source -> nodo.
# ============================================================

    def getBFSNodesFromTreeById(self, sourceStr):
        source = self._getNodeFromDropdownId(sourceStr)

        if source is None:
            return [], []

        if source not in self._graph.nodes:
            return [], []

        tree = nx.bfs_tree(self._graph, source)

        nodes = list(tree.nodes())
        edges = list(tree.edges())

        return nodes, edges


# ============================================================
# CASO 4: DFS NodesFromTree
# ============================================================
# Cosa fa:
# - costruisce l'albero DFS partendo dal nodo source;
# - prende i nodi dell'albero;
# - prende gli archi dell'albero.
#
# Restituisce:
# - nodes = nodi dell'albero DFS;
# - edges = archi dell'albero DFS.
#
# Quando usarlo:
# - quando voglio l'albero di visita DFS;
# - quando voglio scendere in profondità;
# - quando la traccia parla genericamente di visita in profondità.
# ============================================================

    def getDFSNodesFromTreeById(self, sourceStr):
        source = self._getNodeFromDropdownId(sourceStr)

        if source is None:
            return [], []

        if source not in self._graph.nodes:
            return [], []

        tree = nx.dfs_tree(self._graph, source)

        nodes = list(tree.nodes())
        edges = list(tree.edges())

        return nodes, edges


# ============================================================
# FUNZIONE DI SUPPORTO: cammino più lungo dentro un albero di visita
# ============================================================
# Cosa fa:
# 1. Riceve un albero di visita già costruito.
# 2. Per ogni nodo raggiunto, ricostruisce il cammino source -> nodo.
# 3. Tiene il cammino più lungo.
#
# Questo è il pezzo fondamentale della simulazione sugli ordini.
#
# Esempio:
# Se il tree contiene:
# source -> A -> B -> C
# source -> D
#
# allora confronta:
# [source, A]
# [source, A, B]
# [source, A, B, C]
# [source, D]
#
# e tiene il più lungo.
# ============================================================

    def _getCamminoPiuLungoDaTree(self, tree, source):
        lp = []

        nodi = list(tree.nodes())

        for node in nodi:
            tmp = [node]

            while tmp[0] != source:
                pred = nx.predecessor(tree, source, tmp[0])
                tmp.insert(0, pred[0])

            if len(tmp) > len(lp):
                lp = copy.deepcopy(tmp)

        return lp


# ============================================================
# CASO 5: BFS FromTree - cammino più lungo nell'albero BFS
# ============================================================
# Cosa fa:
# - costruisce l'albero BFS;
# - ricostruisce tutti i cammini source -> nodo;
# - restituisce il cammino più lungo nell'albero BFS.
#
# Quando usarlo:
# - se la traccia chiede una visita in ampiezza;
# - se vuoi ragionare per livelli;
# - se il testo richiama nodi più vicini o distanza minima.
# ============================================================

    def getCamminoLungoBFSFromTreeById(self, sourceStr):
        source = self._getNodeFromDropdownId(sourceStr)

        if source is None:
            return []

        if source not in self._graph.nodes:
            return []

        tree = nx.bfs_tree(self._graph, source)

        lp = self._getCamminoPiuLungoDaTree(tree, source)

        return lp


# ============================================================
# CASO 6: DFS FromTree - cammino più lungo nell'albero DFS
# ============================================================
# Cosa fa:
# - costruisce l'albero DFS;
# - ricostruisce tutti i cammini source -> nodo;
# - restituisce il cammino più lungo nell'albero DFS.
#
# Quando usarlo:
# - se la traccia chiede un cammino lungo usando una visita;
# - se devi scendere in profondità;
# - se vuoi replicare la simulazione sugli ordini.
#
# QUESTO È IL CASO PIÙ SIMILE ALLA SIMULAZIONE DI OTTOBRE/NOVEMBRE.
# ============================================================

    def getCamminoLungoDFSFromTreeById(self, sourceStr):
        source = self._getNodeFromDropdownId(sourceStr)

        if source is None:
            return []

        if source not in self._graph.nodes:
            return []

        tree = nx.dfs_tree(self._graph, source)

        lp = self._getCamminoPiuLungoDaTree(tree, source)

        return lp


# ============================================================
# CONTROLLER - BFS NodesFromEdges
# ============================================================
# Collegamento:
# - legge l'id dal Dropdown;
# - controlla che sia stato selezionato;
# - chiama il Model;
# - stampa nodi visitati e archi attraversati.
# ============================================================

    def handleBFSNodesFromEdges(self, e):
        sourceStr = self._view._ddNode.value

        if sourceStr is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Errore: selezionare un nodo di partenza", color="red")
            )
            self._view.update_page()
            return

        nodes, edges = self._model.getBFSNodesFromEdgesById(sourceStr)

        if nodes is None or len(nodes) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Nessun nodo raggiungibile tramite BFS", color="red")
            )
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text(f"BFS NodesFromEdges da nodo {sourceStr}: {len(nodes)} nodi raggiunti", color="red")
        )

        self._view.txt_result.controls.append(ft.Text("Nodi visitati:"))
        for n in nodes:
            self._view.txt_result.controls.append(ft.Text(str(n)))

        self._view.txt_result.controls.append(ft.Text("Archi attraversati dalla BFS:"))
        for edge in edges:
            self._view.txt_result.controls.append(
                ft.Text(f"{edge[0]} --> {edge[1]}")
            )

        self._view.update_page()


# ============================================================
# CONTROLLER - DFS NodesFromEdges
# ============================================================
# Collegamento:
# - legge l'id dal Dropdown;
# - controlla che sia stato selezionato;
# - chiama il Model;
# - stampa nodi visitati e archi attraversati.
# ============================================================

    def handleDFSNodesFromEdges(self, e):
        sourceStr = self._view._ddNode.value

        if sourceStr is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Errore: selezionare un nodo di partenza", color="red")
            )
            self._view.update_page()
            return

        nodes, edges = self._model.getDFSNodesFromEdgesById(sourceStr)

        if nodes is None or len(nodes) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Nessun nodo raggiungibile tramite DFS", color="red")
            )
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text(f"DFS NodesFromEdges da nodo {sourceStr}: {len(nodes)} nodi raggiunti", color="red")
        )

        self._view.txt_result.controls.append(ft.Text("Nodi visitati:"))
        for n in nodes:
            self._view.txt_result.controls.append(ft.Text(str(n)))

        self._view.txt_result.controls.append(ft.Text("Archi attraversati dalla DFS:"))
        for edge in edges:
            self._view.txt_result.controls.append(
                ft.Text(f"{edge[0]} --> {edge[1]}")
            )

        self._view.update_page()


# ============================================================
# CONTROLLER - BFS NodesFromTree
# ============================================================
# Collegamento:
# - legge l'id dal Dropdown;
# - costruisce l'albero BFS nel Model;
# - stampa nodi e archi dell'albero BFS.
# ============================================================

    def handleBFSNodesFromTree(self, e):
        sourceStr = self._view._ddNode.value

        if sourceStr is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Errore: selezionare un nodo di partenza", color="red")
            )
            self._view.update_page()
            return

        nodes, edges = self._model.getBFSNodesFromTreeById(sourceStr)

        if nodes is None or len(nodes) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Nessun nodo raggiungibile tramite albero BFS", color="red")
            )
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text(f"BFS NodesFromTree da nodo {sourceStr}: {len(nodes)} nodi raggiunti", color="red")
        )

        self._view.txt_result.controls.append(ft.Text("Nodi dell'albero BFS:"))
        for n in nodes:
            self._view.txt_result.controls.append(ft.Text(str(n)))

        self._view.txt_result.controls.append(ft.Text("Archi dell'albero BFS:"))
        for edge in edges:
            self._view.txt_result.controls.append(
                ft.Text(f"{edge[0]} --> {edge[1]}")
            )

        self._view.update_page()


# ============================================================
# CONTROLLER - DFS NodesFromTree
# ============================================================
# Collegamento:
# - legge l'id dal Dropdown;
# - costruisce l'albero DFS nel Model;
# - stampa nodi e archi dell'albero DFS.
# ============================================================

    def handleDFSNodesFromTree(self, e):
        sourceStr = self._view._ddNode.value

        if sourceStr is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Errore: selezionare un nodo di partenza", color="red")
            )
            self._view.update_page()
            return

        nodes, edges = self._model.getDFSNodesFromTreeById(sourceStr)

        if nodes is None or len(nodes) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Nessun nodo raggiungibile tramite albero DFS", color="red")
            )
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text(f"DFS NodesFromTree da nodo {sourceStr}: {len(nodes)} nodi raggiunti", color="red")
        )

        self._view.txt_result.controls.append(ft.Text("Nodi dell'albero DFS:"))
        for n in nodes:
            self._view.txt_result.controls.append(ft.Text(str(n)))

        self._view.txt_result.controls.append(ft.Text("Archi dell'albero DFS:"))
        for edge in edges:
            self._view.txt_result.controls.append(
                ft.Text(f"{edge[0]} --> {edge[1]}")
            )

        self._view.update_page()


# ============================================================
# CONTROLLER - CAMMINO LUNGO BFS FromTree
# ============================================================
# Collegamento:
# - legge l'id dal Dropdown;
# - chiama il Model;
# - il Model costruisce bfs_tree;
# - il Model ricostruisce tutti i cammini source -> nodo;
# - il Model restituisce il più lungo.
#
# Da usare se la traccia richiede esplicitamente BFS oppure visita in ampiezza.
# ============================================================

    def handleCamminoLungoBFS(self, e):
        sourceStr = self._view._ddNode.value

        if sourceStr is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Errore: selezionare un nodo di partenza", color="red")
            )
            self._view.update_page()
            return

        cammino = self._model.getCamminoLungoBFSFromTreeById(sourceStr)

        if cammino is None or len(cammino) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Nessun cammino trovato tramite BFS", color="red")
            )
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text(f"Cammino lungo BFS da nodo {sourceStr}: {len(cammino)} nodi", color="red")
        )

        for nodo in cammino:
            self._view.txt_result.controls.append(ft.Text(str(nodo)))

        self._view.update_page()


# ============================================================
# CONTROLLER - CAMMINO LUNGO DFS FromTree
# ============================================================
# Collegamento:
# - legge l'id dal Dropdown;
# - chiama il Model;
# - il Model costruisce dfs_tree;
# - il Model ricostruisce tutti i cammini source -> nodo;
# - il Model restituisce il più lungo.
#
# QUESTO È IL CASO DA USARE PER UNA TRACCIA COME:
# "Cerca Percorso Massimo partendo da un nodo selezionato,
# scegliendo tra visita in ampiezza e visita in profondità".
#
# Nella simulazione sugli ordini:
# - Dropdown nodo ordine;
# - sourceStr = id ordine selezionato;
# - source = self._idMapOrders[int(sourceStr)];
# - tree = nx.dfs_tree(self._graph, source);
# - ricostruisco il cammino più lungo nell'albero.
# ============================================================

    def handleCamminoLungoDFS(self, e):
        sourceStr = self._view._ddNode.value

        if sourceStr is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Errore: selezionare un nodo di partenza", color="red")
            )
            self._view.update_page()
            return

        cammino = self._model.getCamminoLungoDFSFromTreeById(sourceStr)

        if cammino is None or len(cammino) == 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Nessun cammino trovato tramite DFS", color="red")
            )
            self._view.update_page()
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text(f"Cammino lungo DFS da nodo {sourceStr}: {len(cammino)} nodi", color="red")
        )

        for nodo in cammino:
            self._view.txt_result.controls.append(ft.Text(str(nodo)))

        self._view.update_page()


# ============================================================
# SCHEMA RAPIDO DA ESAME
# ============================================================

# Traccia:
# "visualizzare i nodi raggiungibili con visita BFS"
# Uso:
#       getBFSNodesFromEdgesById
# oppure:
#       getBFSNodesFromTreeById
#
# Traccia:
# "visualizzare i nodi raggiungibili con visita DFS"
# Uso:
#       getDFSNodesFromEdgesById
# oppure:
#       getDFSNodesFromTreeById
#
# Traccia:
# "stampare anche gli archi attraversati dalla visita"
# Uso:
#       NodesFromEdges
#
# Traccia:
# "costruire l'albero di visita"
# Uso:
#       NodesFromTree
#
# Traccia:
# "trovare un cammino lungo partendo da un nodo usando BFS/DFS"
# Uso:
#       getCamminoLungoBFSFromTreeById
# oppure, più spesso:
#       getCamminoLungoDFSFromTreeById
#
# Traccia come simulazione sugli ordini:
# "Cerca Percorso Massimo partendo dal nodo selezionato,
# scegliendo tra BFS e DFS"
# Uso:
#       DFS FromTree con ricostruzione del cammino più lungo.
#
# Traccia:
# "percorso ottimo con pesi crescenti/decrescenti, vincoli, massimo score"
# NON basta BFS/DFS.
# Uso:
#       ricorsione / backtracking.
#
# Grafo orientato:
# BFS/DFS seguono il verso degli archi.
#
# Grafo non orientato:
# BFS/DFS esplorano normalmente i vicini.
#
# Se voglio ignorare il verso in un grafo orientato:
# uso:
#       self._graph.to_undirected()
# ============================================================