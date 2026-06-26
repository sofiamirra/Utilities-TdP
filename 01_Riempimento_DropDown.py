# ============================================================
# CASO 1: RIEMPIMENTO DROPDOWN CON ATTRIBUTO SEMPLICE DA DATABASE
# ============================================================
# Esempio:
# L'utente seleziona da due menù a tendina due anni che definiscono un range di interesse.
# I menù devono essere riempiti interrogando il database per ottenere gli anni in cui è stato disputato il campionato.
#
# Logica procedurale:
# 1. Nel DAO creo una query che restituisce una lista di valori semplici.
# 2. Nel Model creo un metodo che richiama il DAO.
# 3. Nel Controller trasformo ogni valore semplice in ft.dropdown.Option(valore).
# 4. Nella View chiamo il metodo di riempimento quando costruisco la pagina.
# ============================================================

# ------------------------------------------------------------
# DAO
# ------------------------------------------------------------

    @staticmethod
    def getAllYears():
        conn = DBConnect.get_connection()
        results = []

        cursor = conn.cursor(dictionary=True)
        query = "SELECT distinct year FROM seasons s  ORDER BY year"

        cursor.execute(query)

        for row in cursor:
            results.append(row["year"])

        cursor.close()
        conn.close()
        return results


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getYears(self):
        return DAO.getAllYears()


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def _fillDDYears(self):
        years = self._model.getYears()
        yearsDD = []
        for year in years:
            yearsDD.append(ft.dropdown.Option(year))
        self._view._ddAnno1.options = yearsDD
        self._view._ddAnno2.options = yearsDD
        self._view.update_page()


# ------------------------------------------------------------
# VIEW
# ------------------------------------------------------------

        self._controller._fillDDYears()


# ============================================================
# CASO 2: RIEMPIMENTO DROPDOWN CON OGGETTO IMPORTATO DA DATABASE
# ============================================================
# Esempio:
# L'utente seleziona da un menù a tendina una categoria di prodotti fra quelle presenti nel database.
#
# Logica procedurale:
# 1. Nel DAO seleziono tutte le colonne necessarie per costruire l'oggetto.
# 2. Nel Model definisco o importo la dataclass dell'oggetto.
# 3. Nel Model creo un metodo che richiama il DAO.
# 4. Nel Controller trasformo ogni oggetto in una Option.
# 5. In ogni Option salvo:
#    - data = oggetto intero, cioè ciò che mi serve per lavorare dopo.
#    - key = stringa da mostrare graficamente nel Dropdown.
# 6. Con on_click salvo l'oggetto selezionato in una variabile del Controller.
# ============================================================


# ------------------------------------------------------------
# DAO
# ------------------------------------------------------------

    @staticmethod
    def getCategorie():
        conn = DBConnect.get_connection()
        results = []

        cursor = conn.cursor(dictionary=True)
        query =  """SELECT * FROM
        categories """

        cursor.execute(query)

        for row in cursor:
            results.append(Category(**row))

        cursor.close()
        conn.close()
        return results


# ------------------------------------------------------------
# MODEL - DATACLASS: creare oggetto Category
# ------------------------------------------------------------

from dataclasses import dataclass

@dataclass
class Category:
    category_id: int
    category_name: str

    def __hash__(self):
        return hash(self.category_id)

    def __eq__(self, other):
        return self.category_id == other.category_id

    def __str__(self):
        return f"{self.category_name} ({self.category_id})"


# ------------------------------------------------------------
# MODEL
# ------------------------------------------------------------

    def getCategories(self):
        return DAO.getCategorie()


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def _fillDDCategories(self):
        categories = self._model.getCategories()
        categoriesDDOptions = list(map(lambda x: ft.dropdown.Option(data=x, key=x.category_name, on_click=self._choiceCategory), categories))
        self._view._ddcategory.options = categoriesDDOptions
        self._view.update_page()

    def _choiceCategory(self, e):
        self._categoryValue = e.control.data


# ------------------------------------------------------------
# VIEW
# ------------------------------------------------------------

        self._controller._fillDDCategories()


# ============================================================
# CASO 3: RIEMPIMENTO DROPDOWN DIPENDENTE DA UN ALTRO DROPDOWN
# ============================================================
# Esempio:
# L'utente sceglie un anno.
# Dopo la scelta dell'anno, il programma deve riempire il Dropdown degli stati disponibili per quell'anno.
#
# Logica procedurale:
# 1. Il Dropdown padre viene creato nella View con on_change.
# 2. Quando l'utente cambia il valore del Dropdown padre, on_change chiama un metodo del Controller.
# 3. Il Controller legge il valore selezionato nel Dropdown padre.
# 4. Se il valore è valido, il Controller chiama il metodo che riempie il Dropdown figlio.
# 5. Il Dropdown figlio viene riempito con dati filtrati rispetto al valore scelto nel Dropdown padre.
#
# Quando usare on_change:
# quando una selezione deve far partire immediatamente un'altra operazione.
#
# Quando usare on_click nelle Option:
# quando voglio salvare l'oggetto preciso selezionato dall'utente.
# ============================================================


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def _fillDDStates(self, year):
        states = self._model.getAllStates(year)
        statesDDOptions = list(map(lambda x: ft.dropdown.Option(data=x, key=x._Name, on_click=self._choiceState), states))
        self._view.ddstate.options = statesDDOptions
        self._view.update_page()

    def handle_year_selection(self, e):
        year = self._view.ddyear.value
        if year is None:
            return
        self._fillDDStates(year)

    def _choiceState(self, e):
        self._stateValue = e.control.data


# ------------------------------------------------------------
# VIEW
# ------------------------------------------------------------

        self.ddyear = ft.Dropdown(label="Anno",
                                  hint_text="Anno da analizzare per gli avvistamenti.",
                                  on_change=self._controller.handle_year_selection)
        self._controller._fillDDYears()
        self.ddstate = ft.Dropdown(label="Stato",
                                   hint_text="Stato da analizzare per gli avvistamenti.")


# ============================================================
# CASO 4: RIEMPIMENTO DROPDOWN COLLEGATO A UN TASTO
# ============================================================
# Esempio:
# L'utente imposta alcuni parametri.
# Poi preme un tasto, per esempio "Crea grafo".
# Solo a quel punto il programma riempie un Dropdown con prodotti, nodi, squadre o altri oggetti disponibili.
#
# Logica procedurale:
# 1. Creo normalmente il Dropdown nella View.
# 2. Creo un bottone nella View collegato a un handler del Controller.
# 3. Dentro l'handler del bottone chiamo il metodo di riempimento del Dropdown.
#
# Quando usare questo caso:
# quando il Dropdown non deve essere riempito subito, ma solo dopo un'azione esplicita dell'utente.
# ============================================================


# ------------------------------------------------------------
# CONTROLLER
# ------------------------------------------------------------

    def handleCreaGrafo(self, e):
        ...
        self._fillDDProdotti()

