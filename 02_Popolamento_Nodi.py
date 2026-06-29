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

# ============================================================
# CONTROLLER - HANDLE CREA GRAFO CON CONTROLLI INPUT
# ============================================================
# Esempio:
# Prima di creare il grafo devo controllare che l'utente abbia inserito/selezionato
# tutti i valori necessari.
#
# Logica procedurale:
# 1. Leggo i valori dalla View.
# 2. Se un valore arriva da un Dropdown, controllo che non sia None.
# 3. Se un valore arriva da una TextField numerica, controllo:
#    - che non sia None;
#    - che non sia stringa vuota;
#    - che sia convertibile a int;
#    - che rispetti eventuali vincoli, per esempio > 0.
# 4. Se un controllo fallisce:
#    - pulisco txt_result;
#    - stampo un messaggio di errore;
#    - faccio update_page();
#    - faccio return per bloccare la creazione del grafo.
# 5. Solo se tutti i controlli passano, chiamo self._model.buildGraph(...).
# ============================================================

    # ------------------------------------------------------------
    # CONTROLLER - caso con due Dropdown anno
    # ------------------------------------------------------------

    def handleCreaGrafo(self, e):
        year1 = self._view._ddAnno1.value
        year2 = self._view._ddAnno2.value

        if year1 is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Errore: selezionare il primo anno", color="red")
            )
            self._view.update_page()
            return

        if year2 is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Errore: selezionare il secondo anno", color="red")
            )
            self._view.update_page()
            return

        self._model.buildGraph(year1, year2)

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Grafo correttamente creato!"))

        nNodes, nEdges = self._model.getGraphDetails()
        self._view.txt_result.controls.append(ft.Text(f"Numero di nodi: {nNodes}"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di archi: {nEdges}"))

        self._view.update_page()

# ------------------------------------------------------------
# CONTROLLER - caso con Dropdown + valore numerico K
# ------------------------------------------------------------

    def handleCreaGrafo(self, e):
        storeId = self._view._ddStore.value
        k = self._view._txtIntK.value

        if storeId is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Errore: selezionare uno store", color="red")
            )
            self._view.update_page()
            return

        if k is None or k == "":
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Errore: inserire un valore per K", color="red")
            )
            self._view.update_page()
            return

        try:
            kInt = int(k)
        except ValueError:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Errore: K deve essere un numero intero", color="red")
            )
            self._view.update_page()
            return

        if kInt <= 0:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Errore: K deve essere maggiore di zero", color="red")
            )
            self._view.update_page()
            return

        self._model.buildGraph(storeId, kInt)

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Grafo correttamente creato!"))

        nNodes, nEdges = self._model.getGraphDetails()
        self._view.txt_result.controls.append(ft.Text(f"Numero di nodi: {nNodes}"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di archi: {nEdges}"))

        self._view.update_page()

# ============================================================
# CASO 2: POPOLAMENTO NODI CON CLASSE CHE HA CAMPI AGGIUNTIVI
# ============================================================
# Esempio:
# La classe Constructor contiene un campo aggiuntivo oldest_driver_dob inizializzato a None.
# Questo campo non arriva direttamente dalla tabella constructors, ma verrà riempito dopo con una query separata.
#
# Logica procedurale:
# 1. Se la tabella del database contiene più colonne rispetto alla dataclass, NON uso SELECT *.
# 2. Nella SELECT scrivo manualmente solo i campi presenti nella dataclass e disponibili nel database.
# 3. Posso comunque usare Constructor(**row), perché Python associa automaticamente le chiavi del dizionario
#    ai campi della dataclass con lo stesso nome.
# 4. Il campo aggiuntivo oldest_driver_dob rimane inizialmente None.
# 5. Dopo aver popolato i nodi, chiamo un secondo metodo del DAO per aggiornare quel campo.
# 6. Il campo aggiornato sarà poi disponibile nel Model, per esempio nella ricorsione.
# ============================================================


# ------------------------------------------------------------
# MODEL - DATACLASS: creare oggetto Constructor con campo aggiuntivo
# ------------------------------------------------------------

from dataclasses import dataclass
import datetime

@dataclass
class Constructor:
    constructorId: int
    constructorRef: str
    name: str
    nationality: str
    oldest_driver_dob: datetime.date = None

    def __hash__(self):
        return hash(self.constructorId)

    def __eq__(self, other):
        return self.constructorId == other.constructorId

    def __str__(self):
        return self.constructorRef


# ------------------------------------------------------------
# DAO - recuperare i nodi selezionando manualmente i campi compatibili
# ------------------------------------------------------------

    @staticmethod
    def getConstructors(y1, y2):
        conn = DBConnect.get_connection()
        results = []

        cursor = conn.cursor(dictionary=True)
        query = """SELECT DISTINCT c.constructorId, c.constructorRef, c.name, c.nationality
        FROM results r, races ra, constructors c
        WHERE r.constructorId = c.constructorId AND ra.raceId = r.raceId
        AND ra.year BETWEEN %s AND %s
        AND r.position is not null"""

        cursor.execute(query, (y1, y2))

        for row in cursor:
            results.append(Constructor(**row))

        cursor.close()
        conn.close()
        return results


# ------------------------------------------------------------
# DAO - recuperare la data di nascita del pilota più anziano
# ------------------------------------------------------------

    @staticmethod
    def getDoB(squadra, year1, year2):
        conn = DBConnect.get_connection()

        cursor = conn.cursor(dictionary=True)
        query = """SELECT MIN(d.dob) as oldest_dob
                    FROM drivers d, results r, races ra
                    WHERE d.driverId = r.driverId
                    AND r.raceId = ra.raceId
                    AND r.constructorId = %s
                    AND ra.year BETWEEN %s AND %s
                    AND r.position is not null
                                    """

        cursor.execute(query, (squadra.constructorId, year1, year2))

        result = None
        for row in cursor:
            # prende il valore della colonna e lo salva
            result = row["oldest_dob"]

        cursor.close()
        conn.close()
        return result


# ------------------------------------------------------------
# MODEL - BUILDGRAPH COMPLETO: nodi + campo aggiuntivo aggiornato dal DAO
# ------------------------------------------------------------

    def buildGraph(self, year1, year2):
        self._graph.clear()
        self._idMapConstructors = {}

        nodes = DAO.getConstructors(year1, year2)
        self._graph.add_nodes_from(nodes)

        for c in nodes:
            self._idMapConstructors[c.constructorId] = c

        for squadra in self._graph.nodes:
            # assegna quella data al campo dell'oggetto squadra
            squadra.oldest_driver_dob = DAO.getDoB(squadra, year1, year2)

# ============================================================
# DAO - NODI: clienti che hanno almeno una fattura
# ============================================================

@staticmethod
def getAllNodes():
    conn = DBConnect.get_connection()
    results = []

    cursor = conn.cursor(dictionary=True)
    query = """SELECT DISTINCT c.*
               FROM customer c, invoice i
               WHERE c.CustomerId = i.CustomerId
               ORDER BY c.LastName, c.FirstName"""

    cursor.execute(query)

    for row in cursor:
        results.append(Customer(**row))

    cursor.close()
    conn.close()
    return results

