from flask import Flask, request, jsonify, send_from_directory, render_template, send_file
import os
import pandas as pd
from fpdf import FPDF
from werkzeug.utils import secure_filename
import zipfile

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "fatture_pdf"
ALLOWED_EXTENSIONS = {"xlsx", "xls"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "FATTURA", border=0, ln=1, align="C")
        self.set_line_width(0.5)
        self.line(10, 28, 200, 28)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, "C")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "Nessun file inviato"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "Nessun file selezionato"}), 400
    if not allowed_file(file.filename):
        return jsonify({"status": "error", "message": "Formato file non supportato"}), 400

    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(upload_path)

    try:
        df = pd.read_excel(upload_path)
        required_cols = ["Numero", "Data", "Cliente", "Indirizzo", "PartitaIVA", "Prodotto", "Quantita", "PrezzoUnitario"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            return jsonify({"status": "error", "message": f"Colonne mancanti: {missing}"}), 400

        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        if df["Data"].isnull().any():
            return jsonify({"status": "error", "message": "Alcune date non valide o mancanti!"}), 400

        grouped = df.groupby("Numero")
        pdf_files = []

        for numero, group in grouped:
            cliente = group.iloc[0]["Cliente"]
            indirizzo = group.iloc[0]["Indirizzo"]
            partita_iva = group.iloc[0]["PartitaIVA"]
            data = group.iloc[0]["Data"]

            pdf = PDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            pdf.cell(40, 10, f"Numero: {numero}")
            pdf.cell(0, 10, f"Data: {data.strftime('%d/%m/%Y')}", ln=1)
            pdf.ln(5)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, cliente, ln=1)
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 8, f"Indirizzo: {indirizzo}", ln=1)
            pdf.cell(0, 8, f"Partita IVA: {partita_iva}", ln=1)
            pdf.ln(10)

            pdf.set_font("Arial", "B", 12)
            pdf.cell(80, 10, "Prodotto")
            pdf.cell(30, 10, "Quantità", align="C")
            pdf.cell(40, 10, "Prezzo Unitario", align="R")
            pdf.cell(40, 10, "Totale", align="R", ln=1)
            pdf.set_font("Arial", size=12)

            totale_netto = 0.0
            for _, riga in group.iterrows():
                totale_riga = riga["Quantita"] * riga["PrezzoUnitario"]
                totale_netto += totale_riga
                pdf.cell(80, 10, str(riga["Prodotto"]))
                pdf.cell(30, 10, str(riga["Quantita"]), align="C")
                pdf.cell(40, 10, f"EUR {riga['PrezzoUnitario']:.2f}", align="R")
                pdf.cell(40, 10, f"EUR {totale_riga:.2f}", align="R", ln=1)

            IVA_PERCENTUALE = 22
            iva = totale_netto * IVA_PERCENTUALE / 100
            totale_con_iva = totale_netto + iva

            pdf.ln(10)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"Totale netto: EUR {totale_netto:.2f}", ln=1, align="R")
            pdf.cell(0, 10, f"IVA {IVA_PERCENTUALE}%: EUR {iva:.2f}", ln=1, align="R")
            pdf.cell(0, 12, f"Totale da pagare: EUR {totale_con_iva:.2f}", ln=1, align="R")
            pdf.ln(20)
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 10, "Fattura generata automaticamente da AutoFattura Web", 0, 1, "C")
            pdf.cell(0, 10, "Firma: __________________________", 0, 1, "C")

            nome_pdf = f"Fattura_{numero}.pdf"
            pdf_path = os.path.join(app.config["OUTPUT_FOLDER"], nome_pdf)
            pdf.output(pdf_path)
            pdf_files.append(nome_pdf)

        # Creo ZIP con tutte le fatture
        zip_path = os.path.join(app.config["OUTPUT_FOLDER"], "fatture.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for f in pdf_files:
                zipf.write(os.path.join(app.config["OUTPUT_FOLDER"], f), f)

        return jsonify({
            "status": "success",
            "message": "Fatture generate!",
            "download": "/download",
            "pdf_files": pdf_files
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/download")
def download_zip():
    return send_from_directory(app.config["OUTPUT_FOLDER"], "fatture.zip", as_attachment=True)

@app.route("/pdf/<filename>")
def serve_pdf(filename):
    if not filename.endswith(".pdf"):
        return "Invalid file", 400
    path = os.path.join(app.config["OUTPUT_FOLDER"], filename)
    if not os.path.exists(path):
        return "File not found", 404
    return send_file(path, mimetype='application/pdf')

if __name__ == "__main__":
    app.run(port=5000, debug=True)
