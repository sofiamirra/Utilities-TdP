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
# SCHEMA DECISIONALE RAPIDO
# ============================================================
# Caso A:
# La query riesce già a calcolare coppie e peso dell'arco.
# Uso un DTO Arco e nel Model faccio add_edge con weight.
#
# Caso B:
# La query trova solo coppie candidate e il peso o il filtro richiede logica Python.
# Non uso DTO, restituisco id1 e id2 e completo tutto nel Model.
#
# Caso C:
# Devo confrontare due elementi della stessa tabella.
# Duplico la tabella nella query con alias diversi, per esempio r1/r2 oppure s1/s2.
#
# Caso D:
# Voglio evitare archi duplicati e cappi.
# Uso una condizione del tipo id1 > id2.
#
# Caso E:
# Il DAO restituisce id, ma il grafo contiene oggetti.
# Uso la idMap per trasformare gli id negli oggetti nodo già presenti nel grafo.
# ============================================================