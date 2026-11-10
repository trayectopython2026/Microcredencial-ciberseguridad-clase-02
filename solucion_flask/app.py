from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

# Reportes ficticios guardados SOLO en la memoria del proceso Python.
reportes = [
    {"titulo": "Actualizaciones pendientes", "categoria": "red", "descripcion": "Equipo del aula ficticia pendiente de revisión.", "fecha": "Demostración"},
    {"titulo": "Mensaje sospechoso", "categoria": "phishing", "descripcion": "Correo simulado identificado por el equipo.", "fecha": "Demostración"},
]
CATEGORIAS = {"phishing", "malware", "contraseña", "red"}

@app.after_request
def cabeceras_basicas(respuesta):
    # Capas defensivas; no sustituyen validación ni autenticación.
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["Referrer-Policy"] = "no-referrer"
    return respuesta

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        categoria = request.form.get("categoria", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        # Validación IMPORTANTE: en el servidor, no solo en el navegador.
        if not titulo or not descripcion:
            error = "El título y la descripción son obligatorios."
        elif len(titulo) > 60 or len(descripcion) > 250:
            error = "El título permite 60 caracteres y la descripción 250 como máximo."
        elif categoria not in CATEGORIAS:
            error = "La categoría no es válida."
        else:
            reportes.insert(0, {
                "titulo": titulo,
                "categoria": categoria,
                "descripcion": descripcion,
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
            })
            # Para el laboratorio mantenemos una sola ruta y no persistimos datos.
            return render_template("index.html", reportes=reportes[:10], error=None, exito=True)
    return render_template("index.html", reportes=reportes[:10], error=error, exito=False)

if __name__ == "__main__":
    # Bind local y debug apagado: la app es solo educativa.
    app.run(host="127.0.0.1", port=5001, debug=False)
