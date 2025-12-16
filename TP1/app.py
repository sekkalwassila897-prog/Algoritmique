from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>TP1 - Graphes et Arbres</title>
        <style>
            body {
                font-family: Arial, Helvetica, sans-serif;
                background: linear-gradient(135deg, #dfe9f3, #ffffff);
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

            h1 {
                color: #273c75;
                text-align: center;
                margin-bottom: 10px;
            }

            h3 {
                color: #40739e;
                margin-top: 30px;
            }

            p {
                font-size: 16px;
                line-height: 1.6;
                color: #2f3640;
            }

            ul {
                margin-left: 20px;
            }

            li {
                margin-bottom: 8px;
                font-size: 15px;
            }

            .info-box {
                background: #f1f5ff;
                border-left: 5px solid #40739e;
                padding: 15px;
                margin-top: 25px;
                border-radius: 6px;
            }

            .github {
                text-align: center;
                margin-top: 30px;
            }

            .github a {
                text-decoration: none;
                background: #273c75;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                transition: 0.3s;
            }

            .github a:hover {
                background: #192a56;
            }

            footer {
                text-align: center;
                margin-top: 40px;
                font-size: 14px;
                color: #718093;
            }
        </style>
    </head>

    <body>
        <div class="container">
            <h1>TP1 – Graphes et Arbres</h1>

            <p>
                Ce TP consiste à la manipulation des graphes et des arbres à l'aide de
                <strong>Python</strong>, <strong>NetworkX</strong> et <strong>Tkinter</strong>.
            </p>

            <h3>Fonctionnalités principales</h3>
            <ul>
                <li>Création de graphes via matrice d’adjacence</li>
                <li>Dessin interactif de graphes</li>
                <li>Graphes orientés, non orientés et pondérés</li>
                <li>Calcul des propriétés (BFS, DFS, diamètre, densité…)</li>
                <li>Export des matrices en format CSV</li>
            </ul>

            <div class="info-box">
                <p>
                    L'application originale est une application <strong>Desktop</strong>
                    développée avec <strong>Tkinter</strong>.
                    Dans le cadre du <strong>TP5</strong>, une version Web descriptive
                    a été mise en place afin de permettre le déploiement sur une
                    plateforme d’hébergement Web.
                </p>
            </div>

            <div class="github">
                <a href="https://github.com/sekkalwassila897-prog/Algoritmique/tree/main/TP1/TP1.py" target="_blank">
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

