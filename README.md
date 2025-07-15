
# 🧾 AutoFattura Web

**AutoFattura Web** è un'applicazione web scritta in Python (Flask) che consente di generare automaticamente fatture in PDF a partire da un file Excel.

## 🚀 Funzionalità

- Upload di file Excel `.xlsx` o `.xls`
- Generazione automatica di una o più fatture PDF
- Calcolo IVA 22% automatico
- Scaricamento in un unico archivio `.zip`
- Visualizzazione anteprima delle fatture
- Interfaccia web semplice, divisa in HTML, CSS e JS

---

## 📂 Struttura progetto

```
AutofatturaWeb/
├── app.py
├── launcher.py            # Avvio alternativo dell'app Flask
├── uploads/               # Cartella upload Excel (creata automaticamente)
├── fatture_pdf/           # Output PDF e ZIP (creata automaticamente)
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── requirements.txt
└── README.md
```

---

## 🛠️ Requisiti

- Python 3.8+
- pip

Installa le dipendenze:

```bash
pip install -r requirements.txt
```

---

## ▶️ Avvio locale

Puoi avviare l'app in due modi:

```bash
python app.py
```

Poi visita `http://localhost:5000` dal browser.

oppure

```bash
python launcher.py
```
---

## 📥 Formato del file Excel richiesto

L'app accetta un file Excel con le seguenti colonne obbligatorie:

| Numero | Data | Cliente | Indirizzo | PartitaIVA | Prodotto | Quantita | PrezzoUnitario |
|--------|------|---------|-----------|------------|----------|----------|----------------|

🔸 Ogni riga rappresenta un prodotto nella fattura. Le righe con lo stesso **Numero** verranno unite nella stessa fattura PDF.

---

## 📄 Licenza

Questo progetto è open source e gratuito. Puoi usarlo, modificarlo e distribuirlo liberamente.

---

## 👤 Autore

Realizzato da **Davide Bergese**  
GitHub: [@bergesedavide](https://github.com/bergesedavide)
