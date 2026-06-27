# ============================================================
# 03_POPOLAMENTO_ARCHI.py
# ============================================================
# CASO 1: ARCHI E PESO CALCOLATI DIRETTAMENTE DALLA QUERY
# ============================================================
# Esempio:
# Due piloti sono collegati da un arco se hanno corso per lo stesso costruttore nella stessa gara.
# Il peso dell'arco è il numero di volte in cui questa condizione si verifica nel range di anni scelto.
#
# Logica procedurale:
# 1. Nel DAO duplico la tabella results come r1 e r2 perché devo confrontare due righe diverse della stessa tabella.
# 2. Uso una sola tabella races perché la gara è il contesto comune in cui confronto i due risultati.
# 3. Impongo che r1 e r2 siano nella stessa gara e abbiano lo stesso constructorId.
# 4. Impongo r1.driverId > r2.driverId per evitare duplicati e auto-coppie.
# 5. Uso GROUP BY sulla coppia di piloti e COUNT(*) per ottenere il peso dell'arco.
# 6. Nel DAO trasformo ogni riga in un oggetto DTO Arco.
# 7. Nel Model ricevo la lista di archi e aggiungo ogni arco al grafo con il relativo peso.
# ============================================================


# ------------------------------------------------------------
# DAO
# ------------------------------------------------------------

    @staticmethod
    def getAllEdges(year1, year2, idMapD):
        conn = DBConnect.get_connection()
        results = []

        cursor = conn.cursor(dictionary=True)
        query = """SELECT r1.driverId as id1, r2.driverId as id2, COUNT(*) as peso
                FROM results r1, results r2, races r
                    WHERE r.raceId = r1.raceId AND r.raceId = r2.raceId
                    AND r1.constructorId = r2.constructorId
                    AND r1.position IS NOT NULL
                    AND r2.position IS NOT NULL
                    AND r1.driverId > r2.driverId
                    AND r.year BETWEEN %s AND %s
                    GROUP BY r1.driverId, r2.driverId """

        cursor.execute(query, (year1, year2))

        for row in cursor:
            results.append(Arco(idMapD[row["id1"]], idMapD[row["id2"]], row["peso"]))

        cursor.close()
        conn.close()
        return results


# ------------------------------------------------------------
# DTO - creare oggetto Arco
# ------------------------------------------------------------

from dataclasses import dataclass
from model.driver import Driver

@dataclass
class Arco:
    d1: Driver
    d2: Driver
    peso: int

    def __str__(self):
        return f"{self.d1} --> {self.d2} ({self.peso})"

# ------------------------------------------------------------
# MODEL - BUILDGRAPH: aggiungere dopo il popolamento dei nodi
# ------------------------------------------------------------

    allEdges = DAO.getAllEdges(y1, y2, self._idMapDrivers)
    for e in allEdges:
        self._graph.add_edge(e.d1, e.d2, weight=e.peso)


# ============================================================
# CASO 2: ARCHI CANDIDATI DALLA QUERY E FILTRO FINALE IN PYTHON
# ============================================================
# Esempio:
# Due avvistamenti sono candidati a essere collegati se appartengono allo stesso stato,
# hanno la stessa forma e si riferiscono allo stesso anno.
# La query restituisce solo le coppie candidate.
# Nel Model recupero gli oggetti veri dalla idMap, calcolo la distanza e aggiungo l'arco solo se la distanza è minore di 100.
#
# Logica procedurale:
# 1. Nel DAO duplico la tabella sighting come s1 e s2 perché devo confrontare due avvistamenti diversi.
# 2. Uso la query per filtrare le condizioni che il database può controllare facilmente: stesso stato, stessa forma, stesso anno.
# 3. Uso s1.id > s2.id per evitare duplicati e auto-coppie.
# 4. Il DAO restituisce righe grezze con id1 e id2, non un DTO.
# 5. Nel Model uso _idMapSights per recuperare gli oggetti associati agli id.
# 6. Nel Model calcolo la distanza con distance_HV.
# 7. Aggiungo l'arco solo se supera il filtro finale definito in Python.
# ============================================================


# ------------------------------------------------------------
# DAO
# ------------------------------------------------------------

    @staticmethod
    def getEdgesInformation(year, state):
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """SELECT s1.id as id1, s2.id as id2
            FROM sighting s1, sighting s2, state st
            WHERE s1.state = st.id AND s1.state = s2.state
              AND s1.shape = s2.shape
              AND s1.id > s2.id
              AND YEAR(s1.datetime) = %s
              AND YEAR(s2.datetime) = %s
              AND st.Name = %s"""
            cursor.execute(query, (year, year, state))

            for row in cursor:
                result.append(row)
            cursor.close()
            cnx.close()
        return result


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def add_edges(self, year, state):
        coppie_grezze = DAO.getEdgesInformation(year, state)

        for riga in coppie_grezze:
            id_1 = riga['id1']
            id_2 = riga['id2']

            s1 = self._idMapSights.get(id_1)
            s2 = self._idMapSights.get(id_2)

            if s1 is not None and s2 is not None:
                distanza = s1.distance_HV(s2)

                if distanza < 100:
                    self._graph.add_edge(s1, s2)


# ------------------------------------------------------------
# MODEL - BUILDGRAPH: aggiungere dopo il popolamento dei nodi
# ------------------------------------------------------------

        self.add_edges(year, state)


# ============================================================
# CASO 3: COPPIE CANDIDATE DAL DAO E VERSO DELL'ARCO DECISO IN PYTHON
# ============================================================
# Esempio:
# Esiste un arco tra l'artista A e l'artista B se almeno un cliente ha acquistato brani di entrambi gli artisti.
# Il verso va dall'artista più popolare verso quello meno popolare.
# Se i due artisti hanno la stessa popolarità, devo aggiungere due archi in entrambi i versi.
# La popolarità di un artista è la somma di tutti i brani acquistati di quell'artista.
# Il peso dell'arco è la somma delle rispettive popolarità.
#
# Logica procedurale:
# 1. Nel DAO creo una mappa {ArtistId: popolarita}.
# 2. Nel DAO creo una lista di coppie candidate di artisti acquistati da almeno uno stesso cliente.
# 3. Nel Model recupero gli oggetti Artist dalla idMap.
# 4. Nel Model leggo le popolarità dalla mappa.
# 5. Nel Model decido il verso dell'arco confrontando pop_1 e pop_2.
# 6. Nel Model gestisco la parità creando due archi.
# 7. Alla fine inserisco nel grafo gli archi salvati nella lista.
#
# Quando usare questo caso:
# quando la query trova bene le coppie candidate, ma la logica di orientamento è più chiara da gestire in Python.
# È molto utile quando in caso di parità bisogna creare due archi separati.
# ============================================================


# ------------------------------------------------------------
# DAO - mappa popolarità artisti
# ------------------------------------------------------------

    @staticmethod
    def getMappaPopolarita(genre_id):
        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """SELECT a.Name, a.ArtistId, sum(il.Quantity) as popolarita
                FROM track t, album ab, artist a, InvoiceLine il
                WHERE t.TrackId = il.TrackId AND ab.AlbumId = t.AlbumId AND ab.ArtistId = a.ArtistId
                AND t.GenreId = %s
                GROUP BY a.ArtistId, a.Name
                        """
        cursor.execute(query, (genre_id, ))

        mappa = {}
        for row in cursor:
            mappa[row["ArtistId"]] = row["popolarita"]

        cursor.close()
        conn.close()
        return mappa


# ------------------------------------------------------------
# DAO - coppie candidate di artisti
# ------------------------------------------------------------

    @staticmethod
    def getCoppieArtisti(g):
        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary=True)
        result = []

        query = """
                SELECT DISTINCT a1.ArtistId AS a1_id, a2.ArtistId AS a2_id
                FROM track t1, album al1, artist a1, invoiceline il1, invoice i1,
                     invoice i2, invoiceline il2, track t2, album al2, artist a2
                WHERE
                    t1.AlbumId = al1.AlbumId
                    AND al1.ArtistId = a1.ArtistId
                    AND t1.TrackId = il1.TrackId
                    AND il1.InvoiceId = i1.InvoiceId

                    AND i1.CustomerId = i2.CustomerId

                    AND i2.InvoiceId = il2.InvoiceId
                    AND il2.TrackId = t2.TrackId
                    AND t2.AlbumId = al2.AlbumId
                    AND al2.ArtistId = a2.ArtistId

                    AND t1.GenreId = %s
                    AND t2.GenreId = %s
                    AND a1.ArtistId > a2.ArtistId
            """

        cursor.execute(query, (g, g))

        for row in cursor:
            result.append((row["a1_id"], row["a2_id"]))

        cursor.close()
        conn.close()
        return result


# ------------------------------------------------------------
# DTO - creare oggetto Arco per artisti
# ------------------------------------------------------------

from dataclasses import dataclass
from model.artist import Artist

@dataclass
class Arco:
    artistA: Artist
    artistB: Artist
    peso: int

    def __str__(self):
        return f"{self.artistA} --> {self.artistB} ({self.peso})"


# ------------------------------------------------------------
# MODEL - INIT: grafo orientato, idMap e lista archi
# ------------------------------------------------------------

    def __init__(self):
        self._graph = nx.DiGraph()
        self._idMapArtists = {}
        self._lista_archi = []


# ------------------------------------------------------------
# MODEL - BUILDGRAPH COMPLETO
# ------------------------------------------------------------

    def buildGraph(self, genre_id):
        self._graph.clear()
        self._lista_archi.clear()

        nodes = DAO.getAllNodes(genre_id, self._idMapArtists)
        self._graph.add_nodes_from(nodes)

        mappa_popolarita = DAO.getMappaPopolarita(genre_id)
        coppie_grezze = DAO.getCoppieArtisti(genre_id)

        for id_1, id_2 in coppie_grezze:
            nodo_1 = self._idMapArtists.get(id_1)
            nodo_2 = self._idMapArtists.get(id_2)

            if nodo_1 not in self._graph.nodes or nodo_2 not in self._graph.nodes:
                continue

            pop_1 = mappa_popolarita.get(id_1, 0)
            pop_2 = mappa_popolarita.get(id_2, 0)
            peso_totale = pop_1 + pop_2

            if pop_1 > pop_2:
                self._lista_archi.append(Arco(nodo_1, nodo_2, peso_totale))
            elif pop_2 > pop_1:
                self._lista_archi.append(Arco(nodo_2, nodo_1, peso_totale))
            else:
                self._lista_archi.append(Arco(nodo_1, nodo_2, peso_totale))
                self._lista_archi.append(Arco(nodo_2, nodo_1, peso_totale))

        for a in self._lista_archi:
            self._graph.add_edge(a.artistA, a.artistB, weight=a.peso)


# ============================================================
# CASO 4: ARCHI ORIENTATI DELEGATI INTERAMENTE AL DAO
# ============================================================
# Esempio:
# Due prodotti sono connessi se entrambi sono stati venduti almeno una volta nel range selezionato.
# L'arco esce dal prodotto con numero di vendite maggiore ed entra nel prodotto con numero di vendite minore.
# In caso di parità, si inseriscono entrambi gli archi.
# Il peso è la somma delle vendite dei due prodotti nel range.
#
# Logica procedurale:
# 1. Nel DAO creo una sottoquery t1 che calcola le vendite per ciascun prodotto.
# 2. Nel DAO creo una seconda sottoquery t2 identica per confrontare coppie di prodotti.
# 3. Uso t1.product_id <> t2.product_id per evitare cappi.
# 4. Uso t1.n >= t2.n per orientare l'arco dal prodotto più venduto verso quello meno venduto.
# 5. In caso di parità, t1.n >= t2.n è vero sia per A-B sia per B-A, quindi SQL produce entrambi gli archi.
# 6. Il DAO può restituire direttamente DTO Arco già completi.
#
# Quando usare questo caso:
# quando il verso dell'arco è esprimibile direttamente in SQL con una condizione semplice tra due valori.
# Qui il DAO basta perché la parità viene gestita automaticamente dalla coppia ordinata in entrambi i versi.
# ============================================================


# ------------------------------------------------------------
# DAO
# ------------------------------------------------------------

    @staticmethod
    def getAllEdges(category, d1, d2, idMapP):
        conn = DBConnect.get_connection()
        results = []

        cursor = conn.cursor(dictionary=True)
        query = """SELECT t1.product_id as id1, t2.product_id as id2, t1.n as nid1, t2.n as nid2, t1.n + t2.n as peso
                FROM (SELECT p.product_id, count(*) as n
                FROM products p, order_items oi, orders o
                WHERE oi.order_id = o.order_id AND oi.product_id = p.product_id
                AND o.order_date BETWEEN %s AND %s
                AND p.category_id = %s
                GROUP BY p.product_id
                ) t1,
                (SELECT p.product_id, count(*) as n
                FROM products p, order_items oi, orders o
                WHERE oi.order_id = o.order_id AND oi.product_id = p.product_id
                AND o.order_date BETWEEN %s AND %s
                AND p.category_id = %s
                GROUP BY p.product_id
                ) t2
                WHERE t1.product_id <> t2.product_id
                AND t1.n >= t2.n
                ORDER BY peso desc"""

        cursor.execute(query, (d1, d2, category.category_id, d1, d2, category.category_id))

        for row in cursor:
            results.append(Arco(idMapP[row["id1"]], idMapP[row["id2"]], row["peso"]))

        cursor.close()
        conn.close()
        return results


# ------------------------------------------------------------
# MODEL - BUILDGRAPH: inserire gli archi restituiti dal DAO
# ------------------------------------------------------------

        allEdges = DAO.getAllEdges(category, d1, d2, self._idMapProducts)
        for e in allEdges:
            self._graph.add_edge(e.p1, e.p2, weight=e.peso)
            self._lista_archi.append(e)

