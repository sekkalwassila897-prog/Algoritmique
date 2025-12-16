# app.py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>TP2 - B-Arbres et B-Arbres*</title>
        <style>
            body {
                font-family: Arial, Helvetica, sans-serif;
                background: linear-gradient(135deg, #f0f4f8, #ffffff);
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 900px;
                margin: 40px auto;
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; text-align: center; }
            h3 { color: #34495e; margin-top: 30px; }
            p { font-size: 16px; line-height: 1.6; color: #2c3e50; }
            ul { margin-left: 20px; }
            li { margin-bottom: 8px; font-size: 15px; }
            .info-box {
                background: #eaf2f8;
                border-left: 5px solid #2980b9;
                padding: 15px;
                margin-top: 25px;
                border-radius: 6px;
            }
            .github { text-align: center; margin-top: 30px; }
            .github a {
                text-decoration: none;
                background: #2980b9;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                transition: 0.3s;
            }
            .github a:hover { background: #1c5980; }
            footer { text-align: center; margin-top: 40px; font-size: 14px; color: #7f8c8d; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>TP2 – B-Arbres et B-Arbres*</h1>
            <p>
                Ce TP permet de manipuler des <strong>B-Arbres</strong> et <strong>B-Arbres*</strong>
                en Python. L'application originale utilise <strong>Tkinter</strong> pour créer une interface
                graphique et <strong>Matplotlib</strong> pour visualiser les arbres.
            </p>
            <h3>Fonctionnalités principales</h3>
            <ul>
                <li>Création d'arbres B et B* selon un ordre donné</li>
                <li>Insertion de clés avec gestion des doublons</li>
                <li>Suppression de clés avec ajustement des noeuds</li>
                <li>Recherche interactive de clés</li>
                <li>Visualisation de l'arbre via Matplotlib (dans l'application originale)</li>
            </ul>
            <div class="info-box">
                <p>
                    Cette version Web est descriptive et pédagogique.
                    Pour interagir avec les arbres en Python, veuillez consulter le code source
                    et l'exécuter localement.
                </p>
            </div>
            <div class="github">
                <a href="https://github.com/sekkalwassila897-prog/Algoritmique/blob/main/TP2/TP2.py" target="_blank">
                    🔗 Voir le code sur GitHub
                </a>
            </div>
            <footer>
                TP Algorithmique Avancée & Complexité – Master IL
            </footer>
        </div>
    </body>
    </html>
    """
import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)
