# ============================================================
# POPOLAMENTO NODI CON OGGETTI FILTRATI DA DATABASE
# ============================================================
# Esempio:
# L'utente seleziona due anni da due Dropdown.
# Il programma deve creare i nodi del grafo usando tutti i piloti che hanno partecipato
# ad almeno una gara nel range temporale selezionato.
#
# Logica procedurale:
# 1. Nel DAO creo una query che seleziona DISTINCT d.* per ottenere ogni pilota una sola volta.
# 2. Uso le tabelle collegate per filtrare i piloti in base agli anni e alle gare effettivamente disputate.
# 3. Nel DAO trasformo ogni riga in un oggetto Driver.
# 4. Nel Model creo la dataclass Driver.
# 5. Nel Model svuoto il grafo, recupero i nodi dal DAO e li aggiungo con add_nodes_from.
# 6. Nel Model creo una idMap con chiave pari alla primary key dell'oggetto.
# 7. Nel Controller leggo gli anni dalla View, costruisco il grafo e stampo il numero di nodi e archi.
# ============================================================


# ------------------------------------------------------------
# DAO
# ------------------------------------------------------------

    @staticmethod
    def getAllNodes(year1, year2):
        conn = DBConnect.get_connection()
        results = []

        cursor = conn.cursor(dictionary=True)
        query = """SELECT DISTINCT d.*
                FROM drivers d, races r, results re
                WHERE r.raceId = re.raceId AND re.driverId = d.driverId
                AND r.year BETWEEN %s AND %s
                AND re.position IS NOT NULL
                ORDER BY d.driverId
                """

        cursor.execute(query, (year1, year2))

        for row in cursor:
            results.append(Driver(**row))

        cursor.close()
        conn.close()
        return results


# ------------------------------------------------------------
# MODEL - DATACLASS: creare oggetto Driver
# ------------------------------------------------------------

import datetime
from dataclasses import dataclass

@dataclass
class Driver:
    driverId: int
    driverRef: str
    number: int
    code: str
    forename: str
    surname: str
    dob: datetime.date
    nationality: str
    url: str

    def __hash__(self):
        return hash(self.driverId)

    def __eq__(self, other):
        return self.driverId == other.driverId

    def __str__(self):
        return self.driverRef


# ------------------------------------------------------------
# MODEL - INIT: inizializzare grafo e idMap
# - nx.Graph() per grafo semplice, non orientato
# - nx.DiGraph() per grafo semplice, orientato
    # ------------------------------------------------------------

    def __init__(self):
        self._graph = nx.Graph()
        self._idMapDrivers = {}


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def buildGraph(self, y1, y2):
        self._graph.clear()
        self._idMapDrivers = {}
        nodes = DAO.getAllNodes(y1, y2)
        self._graph.add_nodes_from(nodes)
        for d in nodes:
            self._idMapDrivers[d.driverId] = d


# ------------------------------------------------------------
# MODEL - DETTAGLI GRAFO PER STAMPA
# ------------------------------------------------------------

    def getGraphDetails(self):
        return len(self._graph.nodes), len(self._graph.edges)


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleCreaGrafo(self, e):
        year1 = self._view._ddAnno1.value
        year2 = self._view._ddAnno2.value
        self._model.buildGraph(year1, year2)
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Grafo correttamente creato!"))

        nNodes, nEdges = self._model.getGraphDetails()
        self._view.txt_result.controls.append(ft.Text(f"Numero di nodi: {nNodes}"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di archi: {nEdges}"))
        self._view.update_page()