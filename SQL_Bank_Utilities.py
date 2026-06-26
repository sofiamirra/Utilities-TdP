# ============================================================
# 05_SQL_COMANDI_UTILI.py
# ============================================================
# Questo file raccoglie comandi e funzioni SQL utili negli esercizi di TdP.
# Non è pensato per essere eseguito direttamente.
# Ogni blocco contiene frammenti SQL da copiare dentro SELECT, WHERE, ORDER BY,
# GROUP BY, HAVING oppure dentro una query del DAO.
#
# Regola generale:
# - SELECT: uso funzioni per trasformare, pulire, calcolare o rinominare valori.
# - WHERE: uso funzioni per filtrare righe in base a stringhe, date o valori nulli.
# - ORDER BY: uso funzioni o alias per ordinare risultati calcolati.
# - SUM/AVG/COUNT: posso combinarli con REPLACE, CAST, COALESCE, CASE WHEN.
#
# Nota importante:
# Gli esempi sono pensati soprattutto per MySQL/MariaDB, tipici dei progetti TdP.
# In MySQL il separatore decimale da usare nei numeri è il punto.
# Quindi 12.50 è un numero decimale corretto.
# Invece 12,50 è una stringa in formato italiano/europeo e va convertita prima di fare SUM, AVG o confronti numerici.
# ============================================================


# ============================================================
# CASO 0: REGOLA BASE SU VIRGOLE E PUNTI NEI NUMERI MYSQL
# ============================================================
# Esempio:
# Nel database posso trovare prezzi o quantità salvati come stringhe:
# "€12,50"
# "1.234,50"
# "$1,234.50"
#
# Logica procedurale:
# 1. MySQL usa il punto come separatore decimale.
# 2. Se ho una virgola decimale, devo sostituirla con il punto.
# 3. Se ho separatori delle migliaia, devo rimuoverli.
# 4. Dopo la pulizia, converto la stringa in numero con CAST.
# 5. Solo dopo CAST uso SUM, AVG, MIN, MAX oppure confronti numerici.
#
# Output mentale fondamentale:
# "€12,50"    -> "12,50"   -> "12.50"   -> 12.50
# "1.234,50" -> "1234,50" -> "1234.50" -> 1234.50
# "$1,234.50" -> "1,234.50" -> "1234.50" -> 1234.50
#
# Errore da evitare:
# CAST('12,50' AS DECIMAL(10,2)) non va trattato come 12.50.
# In MySQL la virgola non è separatore decimale numerico: prima va trasformata in punto.
# ============================================================


# ------------------------------------------------------------
# SQL - NUMERO GIA IN FORMATO MYSQL
# ------------------------------------------------------------

SELECT CAST('12.50' AS DECIMAL(10, 2)) AS valore;

# Output:
# valore = 12.50


# ------------------------------------------------------------
# SQL - NUMERO IN FORMATO ITALIANO/EUROPEO
# ------------------------------------------------------------

SELECT CAST(REPLACE('12,50', ',', '.') AS DECIMAL(10, 2)) AS valore;

# Output:
# '12,50' -> '12.50' -> 12.50


# ------------------------------------------------------------
# SQL - PREZZO EUROPEO CON SIMBOLO EURO
# ------------------------------------------------------------

SELECT CAST(REPLACE(REPLACE('€12,50', '€', ''), ',', '.') AS DECIMAL(10, 2)) AS valore;

# Output:
# '€12,50' -> '12,50' -> '12.50' -> 12.50


# ------------------------------------------------------------
# SQL - PREZZO EUROPEO CON PUNTO MIGLIAIA E VIRGOLA DECIMALE
# ------------------------------------------------------------

SELECT CAST(REPLACE(REPLACE('1.234,50', '.', ''), ',', '.') AS DECIMAL(10, 2)) AS valore;

# Output:
# '1.234,50' -> '1234,50' -> '1234.50' -> 1234.50


# ------------------------------------------------------------
# SQL - PREZZO AMERICANO CON VIRGOLA MIGLIAIA E PUNTO DECIMALE
# ------------------------------------------------------------

SELECT CAST(REPLACE(REPLACE('$1,234.50', '$', ''), ',', '') AS DECIMAL(10, 2)) AS valore;

# Output:
# '$1,234.50' -> '1,234.50' -> '1234.50' -> 1234.50


# ============================================================
# CASO 1: REPLACE PER RIMUOVERE O SOSTITUIRE CARATTERI
# ============================================================
# Esempio:
# Nel database un valore numerico è salvato come stringa con caratteri sporchi.
#
# Logica procedurale:
# 1. Uso REPLACE(colonna, carattere_da_togliere, nuovo_valore).
# 2. Se devo eliminare un carattere, il nuovo valore è stringa vuota ''.
# 3. Se devo sostituire la virgola decimale, uso REPLACE(colonna, ',', '.').
# 4. Se devo eliminare più caratteri, annido più REPLACE.
# ============================================================


# ------------------------------------------------------------
# SQL - FORMA GENERALE
# ------------------------------------------------------------

REPLACE(nome_colonna, 'carattere_da_rimuovere', '')

# Output esempio:
# REPLACE('€12,50', '€', '') -> '12,50'


# ------------------------------------------------------------
# SQL - ESEMPIO IN SELECT
# ------------------------------------------------------------

SELECT REPLACE(p.prezzo, '€', '') AS prezzo_pulito
FROM products p;

# Output esempio:
# p.prezzo = '€12,50'
# prezzo_pulito = '12,50'


# ------------------------------------------------------------
# SQL - ESEMPIO CON REPLACE ANNIDATI
# ------------------------------------------------------------

SELECT REPLACE(REPLACE(p.prezzo, '€', ''), ',', '.') AS prezzo_pulito
FROM products p;

# Output esempio:
# p.prezzo = '€12,50'
# dopo primo REPLACE = '12,50'
# dopo secondo REPLACE = '12.50'


# ------------------------------------------------------------
# SQL - ESEMPIO CON SOMMA DOPO PULIZIA
# ------------------------------------------------------------

SELECT SUM(CAST(REPLACE(REPLACE(p.prezzo, '€', ''), ',', '.') AS DECIMAL(10, 2))) AS totale
FROM products p;

# Output esempio:
# p.prezzo = '€12,50', '€10,00', '€2,50'
# valori puliti = '12.50', '10.00', '2.50'
# valori numerici = 12.50, 10.00, 2.50
# totale = 25.00


# ============================================================
# CASO 2: CAST E DECIMAL PER CONVERTIRE STRINGHE IN NUMERI
# ============================================================
# Esempio:
# Dopo aver pulito una stringa, devo usarla in SUM, AVG oppure in un confronto numerico.
#
# Logica procedurale:
# 1. REPLACE pulisce la stringa.
# 2. CAST trasforma la stringa pulita in numero.
# 3. DECIMAL(10, 2) indica massimo 10 cifre totali, di cui 2 dopo il punto decimale.
# 4. Per soldi, prezzi, pesi e quantità decimali è meglio DECIMAL rispetto a FLOAT.
# ============================================================


# ------------------------------------------------------------
# SQL - FORMA GENERALE
# ------------------------------------------------------------

CAST(nome_colonna AS DECIMAL(10, 2))

# Output esempio:
# CAST('12.50' AS DECIMAL(10, 2)) -> 12.50


# ------------------------------------------------------------
# SQL - ESEMPIO CON SOMMA
# ------------------------------------------------------------

SELECT SUM(CAST(importo AS DECIMAL(10, 2))) AS totale
FROM payments;

# Output esempio:
# importo = '10.50', '2.25', '7.25'
# totale = 20.00


# ------------------------------------------------------------
# SQL - ESEMPIO CON WHERE
# ------------------------------------------------------------

SELECT *
FROM products p
WHERE CAST(p.price AS DECIMAL(10, 2)) > 100;

# Output esempio:
# p.price = '120.50' passa
# p.price = '80.00' non passa


# ------------------------------------------------------------
# SQL - ESEMPIO COMPLETO CON VIRGOLA DECIMALE
# ------------------------------------------------------------

SELECT SUM(CAST(REPLACE(importo, ',', '.') AS DECIMAL(10, 2))) AS totale
FROM payments;

# Output esempio:
# importo = '10,50', '2,25', '7,25'
# dopo REPLACE = '10.50', '2.25', '7.25'
# dopo CAST = 10.50, 2.25, 7.25
# totale = 20.00


# ============================================================
# CASO 3: FORMATO EUROPEO CON MIGLIAIA E DECIMALI
# ============================================================
# Esempio:
# La stringa usa il punto per le migliaia e la virgola per i decimali:
# "1.234,50"
#
# Logica procedurale:
# 1. Prima rimuovo il punto delle migliaia.
# 2. Poi sostituisco la virgola decimale con il punto.
# 3. Poi converto con CAST.
#
# Ordine importante:
# Prima togliere '.', poi cambiare ',' in '.'
# ============================================================


# ------------------------------------------------------------
# SQL - FORMATO EUROPEO
# ------------------------------------------------------------

SELECT CAST(REPLACE(REPLACE(prezzo, '.', ''), ',', '.') AS DECIMAL(10, 2)) AS prezzo_num
FROM products;

# Output esempio:
# prezzo = '1.234,50'
# dopo REPLACE(prezzo, '.', '') = '1234,50'
# dopo REPLACE(..., ',', '.') = '1234.50'
# dopo CAST = 1234.50


# ------------------------------------------------------------
# SQL - SOMMA FORMATO EUROPEO
# ------------------------------------------------------------

SELECT SUM(CAST(REPLACE(REPLACE(prezzo, '.', ''), ',', '.') AS DECIMAL(10, 2))) AS totale
FROM products;

# Output esempio:
# prezzo = '1.234,50', '100,25', '2.000,00'
# valori numerici = 1234.50, 100.25, 2000.00
# totale = 3334.75


# ============================================================
# CASO 4: FORMATO AMERICANO CON MIGLIAIA E DECIMALI
# ============================================================
# Esempio:
# La stringa usa la virgola per le migliaia e il punto per i decimali:
# "1,234.50"
#
# Logica procedurale:
# 1. Rimuovo la virgola delle migliaia.
# 2. Lascio il punto decimale invariato.
# 3. Converto con CAST.
# ============================================================


# ------------------------------------------------------------
# SQL - FORMATO AMERICANO
# ------------------------------------------------------------

SELECT CAST(REPLACE(prezzo, ',', '') AS DECIMAL(10, 2)) AS prezzo_num
FROM products;

# Output esempio:
# prezzo = '1,234.50'
# dopo REPLACE = '1234.50'
# dopo CAST = 1234.50


# ------------------------------------------------------------
# SQL - SOMMA FORMATO AMERICANO CON SIMBOLO DOLLARO
# ------------------------------------------------------------

SELECT SUM(CAST(REPLACE(REPLACE(prezzo, '$', ''), ',', '') AS DECIMAL(10, 2))) AS totale
FROM products;

# Output esempio:
# prezzo = '$1,234.50', '$100.25'
# valori puliti = '1234.50', '100.25'
# totale = 1334.75


# ============================================================
# CASO 5: COALESCE PER GESTIRE VALORI NULL
# ============================================================
# Esempio:
# Una colonna può contenere NULL.
# Se devo stampare, sommare o confrontare quel valore, posso sostituire NULL con un valore di default.
#
# Logica procedurale:
# 1. COALESCE restituisce il primo valore non NULL.
# 2. Se la colonna è NULL, uso il valore di riserva.
# 3. È utile in SELECT, SUM, CONCAT, ORDER BY e calcoli.
# ============================================================


# ------------------------------------------------------------
# SQL - FORMA GENERALE
# ------------------------------------------------------------

COALESCE(nome_colonna, valore_di_default)

# Output esempio:
# COALESCE(NULL, 0) -> 0
# COALESCE(5, 0) -> 5


# ------------------------------------------------------------
# SQL - ESEMPIO IN SELECT
# ------------------------------------------------------------

SELECT COALESCE(p.discount, 0) AS discount
FROM products p;

# Output esempio:
# p.discount = NULL -> discount = 0
# p.discount = 0.20 -> discount = 0.20


# ------------------------------------------------------------
# SQL - ESEMPIO IN SOMMA
# ------------------------------------------------------------

SELECT SUM(COALESCE(o.quantity, 0)) AS totale_quantita
FROM orders o;

# Output esempio:
# quantity = 2, NULL, 3
# dopo COALESCE = 2, 0, 3
# totale_quantita = 5

# ============================================================
# CASO 7: LIKE PER CERCARE TESTO PARZIALE
# ============================================================
# Esempio:
# Devo selezionare righe in cui una stringa contiene, inizia o finisce con una certa parola.
#
# Logica procedurale:
# 1. Uso LIKE nel WHERE.
# 2. Il simbolo % indica qualsiasi sequenza di caratteri.
# 3. Il simbolo _ indica un singolo carattere.
# 4. Posso usare NOT LIKE per escludere un pattern.
# 5. Posso usare LOWER per rendere il confronto più robusto.
# ============================================================


# ------------------------------------------------------------
# SQL - CONTIENE UNA PAROLA
# ------------------------------------------------------------

SELECT *
FROM products p
WHERE p.product_name LIKE '%bike%';

# Output esempio:
# 'Mountain bike' passa
# 'Bike helmet' passa
# 'Helmet' non passa


# ------------------------------------------------------------
# SQL - INIZIA CON UNA PAROLA
# ------------------------------------------------------------

SELECT *
FROM products p
WHERE p.product_name LIKE 'bike%';

# Output esempio:
# 'bike helmet' passa
# 'mountain bike' non passa


# ------------------------------------------------------------
# SQL - FINISCE CON UNA PAROLA
# ------------------------------------------------------------

SELECT *
FROM products p
WHERE p.product_name LIKE '%bike';

# Output esempio:
# 'mountain bike' passa
# 'bike helmet' non passa


# ------------------------------------------------------------
# SQL - UN SOLO CARATTERE VARIABILE
# ------------------------------------------------------------

SELECT *
FROM drivers d
WHERE d.code LIKE 'A__';

# Output esempio:
# 'ALO' passa
# 'AI' non passa
# 'ABCD' non passa


# ------------------------------------------------------------
# SQL - VERSIONE CASE INSENSITIVE
# ------------------------------------------------------------

SELECT *
FROM products p
WHERE LOWER(p.product_name) LIKE '%bike%';

# Output esempio:
# 'BIKE HELMET' passa
# 'Bike helmet' passa
# 'bike helmet' passa


# ============================================================
# CASO 8: SUBSTRING, LEFT, RIGHT PER ESTRARRE PARTI DI STRINGA
# ============================================================
# Esempio:
# Da un codice testuale devo estrarre solo una parte.
#
# Logica procedurale:
# 1. SUBSTRING(colonna, posizione_iniziale, lunghezza) estrae una porzione.
# 2. In MySQL la posizione iniziale parte da 1.
# 3. LEFT(colonna, n) prende i primi n caratteri.
# 4. RIGHT(colonna, n) prende gli ultimi n caratteri.
# ============================================================


# ------------------------------------------------------------
# SQL - SUBSTRING
# ------------------------------------------------------------

SELECT SUBSTRING(d.code, 1, 2) AS prefisso
FROM drivers d;

# Output esempio:
# d.code = 'ALO'
# prefisso = 'AL'


# ------------------------------------------------------------
# SQL - LEFT
# ------------------------------------------------------------

SELECT LEFT(d.driverRef, 3) AS primi_tre
FROM drivers d;

# Output esempio:
# d.driverRef = 'hamilton'
# primi_tre = 'ham'


# ------------------------------------------------------------
# SQL - RIGHT
# ------------------------------------------------------------

SELECT RIGHT(d.driverRef, 3) AS ultimi_tre
FROM drivers d;

# Output esempio:
# d.driverRef = 'hamilton'
# ultimi_tre = 'ton'


# ------------------------------------------------------------
# SQL - SUBSTRING IN WHERE
# ------------------------------------------------------------

SELECT *
FROM drivers d
WHERE SUBSTRING(d.code, 1, 1) = 'A';

# Output esempio:
# d.code = 'ALO' passa
# d.code = 'HAM' non passa


# ============================================================
# CASO 9: TRIM PER RIMUOVERE SPAZI AI BORDI
# ============================================================
# Esempio:
# Una colonna contiene spazi prima o dopo il testo.
#
# Logica procedurale:
# 1. TRIM rimuove spazi a destra e sinistra.
# 2. LTRIM rimuove spazi a sinistra.
# 3. RTRIM rimuove spazi a destra.
# 4. È utile prima di LIKE, GROUP BY o confronti con =.
# ============================================================


# ------------------------------------------------------------
# SQL - TRIM
# ------------------------------------------------------------

SELECT TRIM(c.country) AS country_clean
FROM customers c;

# Output esempio:
# c.country = ' Italy '
# country_clean = 'Italy'


# ------------------------------------------------------------
# SQL - TRIM IN WHERE
# ------------------------------------------------------------

SELECT *
FROM customers c
WHERE TRIM(c.country) = 'Italy';

# Output esempio:
# ' Italy ' passa
# 'Italy' passa
# 'France' non passa


# ============================================================
# CASO 10: CONCAT PER UNIRE STRINGHE
# ============================================================
# Esempio:
# Voglio stampare nome e cognome in un'unica colonna.
#
# Logica procedurale:
# 1. Uso CONCAT per unire più campi.
# 2. Posso inserire stringhe fisse tra i campi.
# 3. Se un campo può essere NULL, conviene usare COALESCE.
# ============================================================


# ------------------------------------------------------------
# SQL - CONCAT SEMPLICE
# ------------------------------------------------------------

SELECT CONCAT(d.forename, ' ', d.surname) AS full_name
FROM drivers d;

# Output esempio:
# forename = 'Lewis'
# surname = 'Hamilton'
# full_name = 'Lewis Hamilton'


# ------------------------------------------------------------
# SQL - CONCAT CON COALESCE
# ------------------------------------------------------------

SELECT CONCAT(COALESCE(d.code, 'NO_CODE'), ' - ', d.surname) AS label_driver
FROM drivers d;

# Output esempio:
# code = NULL, surname = 'Hamilton'
# label_driver = 'NO_CODE - Hamilton'


# ============================================================
# CASO 11: YEAR, MONTH, DAY PER FILTRARE DATE
# ============================================================
# Esempio:
# Devo filtrare righe in base all'anno, al mese o al giorno di una colonna DATE/DATETIME.
#
# Logica procedurale:
# 1. YEAR(colonna) estrae l'anno.
# 2. MONTH(colonna) estrae il mese.
# 3. DAY(colonna) estrae il giorno del mese.
# 4. Sono molto utili nel WHERE quando il database contiene DATETIME complete.
# ============================================================


# ------------------------------------------------------------
# SQL - YEAR IN SELECT
# ------------------------------------------------------------

SELECT YEAR(s.datetime) AS anno
FROM sighting s;

# Output esempio:
# s.datetime = '2010-07-25 18:30:00'
# anno = 2010


# ------------------------------------------------------------
# SQL - YEAR IN WHERE
# ------------------------------------------------------------

SELECT *
FROM sighting s
WHERE YEAR(s.datetime) = %s;

# Output esempio:
# s.datetime = '2010-07-25 18:30:00', parametro = 2010 -> passa
# s.datetime = '2011-07-25 18:30:00', parametro = 2010 -> non passa


# ------------------------------------------------------------
# SQL - MONTH
# ------------------------------------------------------------

SELECT *
FROM orders o
WHERE MONTH(o.orderDate) = 12;

# Output esempio:
# '2020-12-01' passa
# '2020-11-01' non passa


# ------------------------------------------------------------
# SQL - DAY
# ------------------------------------------------------------

SELECT *
FROM orders o
WHERE DAY(o.orderDate) = 1;

# Output esempio:
# '2020-12-01' passa
# '2020-12-15' non passa


# ============================================================
# CASO 12: DATEDIFF E TIMESTAMPDIFF PER DIFFERENZE TRA DATE
# ============================================================
# Esempio:
# Devo calcolare quanti giorni passano tra due date oppure devo filtrare eventi vicini nel tempo.
#
# Logica procedurale:
# 1. DATEDIFF(data_finale, data_iniziale) restituisce la differenza in giorni.
# 2. TIMESTAMPDIFF(unità, data_iniziale, data_finale) permette di scegliere l'unità.
# 3. Le unità più comuni sono DAY, MONTH, YEAR, HOUR, MINUTE.
# 4. In MySQL normalmente uso DATEDIFF, TIMESTAMPDIFF oppure TO_DAYS, non DAYS().
# ============================================================


# ------------------------------------------------------------
# SQL - DATEDIFF IN SELECT
# ------------------------------------------------------------

SELECT DATEDIFF(o.shippedDate, o.orderDate) AS giorni_spedizione
FROM orders o;

# Output esempio:
# shippedDate = '2020-01-10'
# orderDate = '2020-01-03'
# giorni_spedizione = 7


# ------------------------------------------------------------
# SQL - DATEDIFF IN WHERE
# ------------------------------------------------------------

SELECT *
FROM orders o
WHERE DATEDIFF(o.shippedDate, o.orderDate) <= 7;

# Output esempio:
# differenza = 5 -> passa
# differenza = 10 -> non passa


# ------------------------------------------------------------
# SQL - TIMESTAMPDIFF IN GIORNI
# ------------------------------------------------------------

SELECT TIMESTAMPDIFF(DAY, s1.datetime, s2.datetime) AS differenza_giorni
FROM sighting s1, sighting s2;

# Output esempio:
# s1.datetime = '2020-01-01 10:00:00'
# s2.datetime = '2020-01-03 10:00:00'
# differenza_giorni = 2


# ------------------------------------------------------------
# SQL - TIMESTAMPDIFF IN ANNI
# ------------------------------------------------------------

SELECT TIMESTAMPDIFF(YEAR, d.dob, CURDATE()) AS eta
FROM drivers d;

# Output esempio:
# dob = '2000-01-01'
# CURDATE() = '2026-06-26'
# eta = 26


# ============================================================
# CASO 13: TO_DAYS PER TRASFORMARE DATE IN NUMERI
# ============================================================
# Esempio:
# Devo confrontare due date trasformandole in numeri di giorni.
#
# Logica procedurale:
# 1. TO_DAYS(data) converte una data in numero di giorni.
# 2. La differenza tra due TO_DAYS equivale a una differenza in giorni.
# 3. È utile quando voglio scrivere manualmente una distanza temporale.
# ============================================================


# ------------------------------------------------------------
# SQL - DIFFERENZA TRA DATE CON TO_DAYS
# ------------------------------------------------------------

SELECT TO_DAYS(s2.datetime) - TO_DAYS(s1.datetime) AS diff_giorni
FROM sighting s1, sighting s2;

# Output esempio:
# s1.datetime = '2020-01-01'
# s2.datetime = '2020-01-03'
# diff_giorni = 2


# ------------------------------------------------------------
# SQL - FILTRO CON TO_DAYS
# ------------------------------------------------------------

SELECT *
FROM sighting s1, sighting s2
WHERE ABS(TO_DAYS(s2.datetime) - TO_DAYS(s1.datetime)) <= 10;

# Output esempio:
# differenza assoluta = 7 -> passa
# differenza assoluta = 15 -> non passa


# ============================================================
# CASO 14: DATE_FORMAT PER FORMATTARE DATE
# ============================================================
# Esempio:
# Devo stampare o raggruppare una data in formato anno-mese oppure anno.
#
# Logica procedurale:
# 1. DATE_FORMAT permette di trasformare una data in una stringa formattata.
# 2. '%Y' restituisce l'anno.
# 3. '%m' restituisce il mese numerico.
# 4. '%Y-%m' restituisce anno-mese.
# ============================================================


# ------------------------------------------------------------
# SQL - FORMATO ANNO-MESE
# ------------------------------------------------------------

SELECT DATE_FORMAT(o.orderDate, '%Y-%m') AS mese
FROM orders o;

# Output esempio:
# orderDate = '2020-12-25'
# mese = '2020-12'


# ------------------------------------------------------------
# SQL - GROUP BY ANNO-MESE
# ------------------------------------------------------------

SELECT DATE_FORMAT(o.orderDate, '%Y-%m') AS mese, COUNT(*) AS n_ordini
FROM orders o
GROUP BY DATE_FORMAT(o.orderDate, '%Y-%m');

# Output esempio:
# mese = '2020-12', n_ordini = 15


# ============================================================
# CASO 15: STR_TO_DATE PER CONVERTIRE STRINGHE IN DATE
# ============================================================
# Esempio:
# Una data è salvata come stringa, per esempio '25/12/2020'.
# La converto in vera data per poter filtrare o calcolare differenze.
#
# Logica procedurale:
# 1. STR_TO_DATE(stringa, formato) converte una stringa in data.
# 2. Il formato deve corrispondere alla struttura della stringa.
# 3. Dopo la conversione posso usare YEAR, DATEDIFF, ORDER BY.
# ============================================================


# ------------------------------------------------------------
# SQL - CONVERSIONE STRINGA IN DATA
# ------------------------------------------------------------

SELECT STR_TO_DATE(o.data_testuale, '%d/%m/%Y') AS data_convertita
FROM orders o;

# Output esempio:
# data_testuale = '25/12/2020'
# data_convertita = '2020-12-25'


# ------------------------------------------------------------
# SQL - YEAR SU DATA CONVERTITA
# ------------------------------------------------------------

SELECT *
FROM orders o
WHERE YEAR(STR_TO_DATE(o.data_testuale, '%d/%m/%Y')) = 2020;

# Output esempio:
# data_testuale = '25/12/2020' passa
# data_testuale = '25/12/2021' non passa


# ============================================================
# CASO 16: CASE WHEN PER CREARE VALORI CONDIZIONALI
# ============================================================
# Esempio:
# Voglio creare una colonna calcolata che dipende da una condizione.
#
# Logica procedurale:
# 1. CASE WHEN funziona come un if dentro SQL.
# 2. Posso usarlo in SELECT per creare etichette.
# 3. Posso usarlo dentro SUM per contare o pesare solo alcune righe.
# ============================================================


# ------------------------------------------------------------
# SQL - CASE WHEN IN SELECT
# ------------------------------------------------------------

SELECT p.productName,
       CASE
           WHEN p.price > 100 THEN 'costoso'
           ELSE 'economico'
       END AS fascia_prezzo
FROM products p;

# Output esempio:
# price = 120 -> fascia_prezzo = 'costoso'
# price = 80 -> fascia_prezzo = 'economico'


# ------------------------------------------------------------
# SQL - CASE WHEN DENTRO SUM
# ------------------------------------------------------------

SELECT SUM(CASE WHEN o.status = 'Shipped' THEN 1 ELSE 0 END) AS ordini_spediti
FROM orders o;

# Output esempio:
# status = 'Shipped', 'Cancelled', 'Shipped'
# valori generati = 1, 0, 1
# ordini_spediti = 2


# ------------------------------------------------------------
# SQL - CASE WHEN PER PESO CONDIZIONALE
# ------------------------------------------------------------

SELECT SUM(CASE WHEN r.position <= 3 THEN 10 ELSE 1 END) AS punteggio
FROM results r;

# Output esempio:
# position = 1 -> 10
# position = 5 -> 1


# ============================================================
# CASO 17: NULLIF PER EVITARE DIVISIONE PER ZERO
# ============================================================
# Esempio:
# Devo calcolare un rapporto, ma il denominatore potrebbe essere zero.
#
# Logica procedurale:
# 1. NULLIF(a, b) restituisce NULL se a = b.
# 2. NULLIF(denominatore, 0) evita la divisione per zero.
# 3. Posso combinare con COALESCE per sostituire il risultato NULL con 0.
# ============================================================


# ------------------------------------------------------------
# SQL - RAPPORTO SICURO
# ------------------------------------------------------------

SELECT totale_vendite / NULLIF(numero_ordini, 0) AS media
FROM statistiche;

# Output esempio:
# totale_vendite = 100, numero_ordini = 4 -> media = 25
# totale_vendite = 100, numero_ordini = 0 -> media = NULL


# ------------------------------------------------------------
# SQL - RAPPORTO SICURO CON DEFAULT
# ------------------------------------------------------------

SELECT COALESCE(totale_vendite / NULLIF(numero_ordini, 0), 0) AS media
FROM statistiche;

# Output esempio:
# totale_vendite = 100, numero_ordini = 0 -> media = 0


# ============================================================
# CASO 18: ABS, ROUND, CEIL, FLOOR PER CALCOLI NUMERICI
# ============================================================
# Esempio:
# Devo usare valori assoluti, arrotondamenti o confronti numerici più puliti.
#
# Logica procedurale:
# 1. ABS restituisce il valore assoluto.
# 2. ROUND arrotonda a un numero specifico di decimali.
# 3. CEIL arrotonda per eccesso.
# 4. FLOOR arrotonda per difetto.
# ============================================================


# ------------------------------------------------------------
# SQL - ABS
# ------------------------------------------------------------

SELECT ABS(peso1 - peso2) AS differenza_assoluta
FROM tabella;

# Output esempio:
# peso1 = 5, peso2 = 9
# differenza_assoluta = 4


# ------------------------------------------------------------
# SQL - ROUND
# ------------------------------------------------------------

SELECT ROUND(AVG(p.price), 2) AS prezzo_medio
FROM products p;

# Output esempio:
# AVG = 12.34567
# prezzo_medio = 12.35


# ------------------------------------------------------------
# SQL - CEIL / FLOOR
# ------------------------------------------------------------

SELECT CEIL(p.price) AS prezzo_eccesso, FLOOR(p.price) AS prezzo_difetto
FROM products p;

# Output esempio:
# price = 12.34
# prezzo_eccesso = 13
# prezzo_difetto = 12


# ============================================================
# CASO 19: UPPER E LOWER PER CONFRONTI TESTUALI ROBUSTI
# ============================================================
# Esempio:
# Nel database lo stesso valore può comparire con maiuscole/minuscole diverse.
#
# Logica procedurale:
# 1. LOWER trasforma tutto in minuscolo.
# 2. UPPER trasforma tutto in maiuscolo.
# 3. Sono utili con LIKE oppure con confronti testuali.
# ============================================================


# ------------------------------------------------------------
# SQL - LOWER IN WHERE
# ------------------------------------------------------------

SELECT *
FROM state st
WHERE LOWER(st.Name) = LOWER(%s);

# Output esempio:
# st.Name = 'Italy', parametro = 'ITALY' -> passa
# st.Name = 'Italy', parametro = 'italy' -> passa


# ------------------------------------------------------------
# SQL - UPPER IN SELECT
# ------------------------------------------------------------

SELECT UPPER(d.nationality) AS nationality
FROM drivers d;

# Output esempio:
# nationality = 'italian'
# output = 'ITALIAN'


# ============================================================
# CASO 20: FORMAT PER STAMPARE NUMERI FORMATTI, NON PER SOMMARE
# ============================================================
# Esempio:
# Voglio mostrare un numero con separatori leggibili.
#
# Logica procedurale:
# 1. FORMAT formatta un numero per la stampa.
# 2. Il risultato di FORMAT è una stringa.
# 3. Non usare FORMAT prima di SUM o AVG.
# 4. Prima calcolo come numero, poi eventualmente formatto solo l'output.
# ============================================================


# ------------------------------------------------------------
# SQL - FORMAT PER OUTPUT
# ------------------------------------------------------------

SELECT FORMAT(1234.5, 2) AS valore_formattato;

# Output esempio:
# valore_formattato = '1,234.50'


# ------------------------------------------------------------
# SQL - GIUSTO: SOMMARE PRIMA, FORMATTARE DOPO
# ------------------------------------------------------------

SELECT FORMAT(SUM(CAST(REPLACE(prezzo, ',', '.') AS DECIMAL(10, 2))), 2) AS totale_formattato
FROM products;

# Output esempio:
# prezzi = '10,50', '2,25'
# somma numerica = 12.75
# totale_formattato = '12.75'


# ============================================================
# CASO 21: REGEXP_REPLACE PER RIMUOVERE PATTERN COMPLESSI
# ============================================================
# Esempio:
# Devo rimuovere tutti i caratteri non numerici da una stringa.
#
# Logica procedurale:
# 1. REGEXP_REPLACE usa una regular expression.
# 2. È più potente di REPLACE perché può rimuovere insiemi di caratteri.
# 3. Verificare che il DBMS e la versione MySQL supportino REGEXP_REPLACE.
# 4. Se non funziona, tornare a REPLACE annidati.
# ============================================================


# ------------------------------------------------------------
# SQL - RIMUOVERE CARATTERI NON NUMERICI
# ------------------------------------------------------------

SELECT REGEXP_REPLACE(p.price_text, '[^0-9.]', '') AS price_clean
FROM products p;

# Output esempio:
# price_text = '€12.50 kg'
# price_clean = '12.50'


# ------------------------------------------------------------
# SQL - SOMMA DOPO REGEXP_REPLACE
# ------------------------------------------------------------

SELECT SUM(CAST(REGEXP_REPLACE(p.price_text, '[^0-9.]', '') AS DECIMAL(10, 2))) AS totale
FROM products p;

# Output esempio:
# price_text = '€12.50', '€10.00'
# price_clean = '12.50', '10.00'
# totale = 22.50


# ------------------------------------------------------------
# SPAZI UTILI DA CERCARE SU INTERNET
# ------------------------------------------------------------

MySQL Reference Manual - String Functions
MySQL Reference Manual - Date and Time Functions
MySQL Reference Manual - Cast Functions and Operators
MySQL Reference Manual - Type Conversion in Expression Evaluation
MySQL Reference Manual - Numeric Data Type Syntax
W3Schools SQL Functions
w3resource MySQL Functions
Stack Overflow solo per errori specifici, non come prima fonte
