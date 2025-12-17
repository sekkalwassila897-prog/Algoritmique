from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>TP4 - Algorithmes classiques sur les graphes</title>
        <style>
            body {
                font-family: Arial, Helvetica, sans-serif;
                background: linear-gradient(135deg, #eef2f3, #ffffff);
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 950px;
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
                background: #f4f9ff;
                border-left: 5px solid #3498db;
                padding: 15px;
                margin-top: 20px;
                border-radius: 6px;
            }
            .links { text-align: center; margin-top: 30px; }
            .links a {
                display: inline-block;
                margin: 8px;
                text-decoration: none;
                background: #3498db;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                transition: 0.3s;
            }
            .links a:hover { background: #1f6391; }
            footer { text-align: center; margin-top: 40px; font-size: 14px; color: #7f8c8d; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>TP4 – Algorithmes classiques sur les graphes</h1>

            <p>
                Ce TP a pour objectif de comprendre et manipuler des
                <strong>graphes</strong> en utilisant des algorithmes classiques :
                <strong>BFS</strong>, <strong>DFS</strong>, <strong>Dijkstra</strong>, etc.
            </p>

            <h3>Description détaillée du TP</h3>
            <p>
                Les graphes sont des structures de données fondamentales
                en informatique. Ce TP met l’accent sur :
            </p>
            <ul>
                <li>La représentation des graphes (listes d’adjacence, matrices)</li>
                <li>Parcours en profondeur (DFS) et en largeur (BFS)</li>
                <li>Algorithmes de plus court chemin (Dijkstra)</li>
                <li>Visualisation interactive des graphes</li>
            </ul>

            <h3>Implémentation</h3>
            <p>
                L’application originale est un <strong>Desktop</strong> développé en Python avec <strong>PyQt5</strong> pour l’interface graphique.
            </p>

            <div class="info-box">
                <p>
                    Cette version Web est <strong>descriptive et pédagogique</strong>,
                    développée avec <strong>Flask</strong>,
                    afin de répondre aux exigences du TP5 concernant le déploiement des projets.
                </p>
            </div>

            <h3>Comment exécuter les TPs localement</h3>
            <div class="info-box">
                <ol>
                    <li>Cloner ou télécharger le dépôt GitHub du projet.</li>
                    <li>Installer Python (version 3.9 ou supérieure).</li>
                    <li>Installer les bibliothèques nécessaires :
                        <pre>pip install pyqt5 networkx matplotlib flask</pre>
                    </li>
                    <li>Ouvrir le dossier du projet dans un éditeur de code (ex: VS Code).</li>
                    <li>Lancer l’interface principale :
                        <pre>python index.py</pre>
                    </li>
                    <li>Depuis l’interface principale, sélectionner TP4 pour exécuter le Desktop PyQt5 ou consulter la version Web.</li>
                </ol>
            </div>

            <h3>Rapport du TP</h3>
            <div class="info-box">
                <p>
                    Un rapport détaillé au format PDF est disponible.
                </p>
                <p>
                    📄 <a href="https://github.com/sekkalwassila897-prog/Algoritmique/blob/main/melgithub/PRESENTATION%20TP4.pdf" target="_blank">
                        Consulter le rapport PDF
                    </a>
                </p>
            </div>

            <div class="links">
                <a href="https://github.com/sekkalwassila897-prog/Algoritmique/blob/main/TP4/main_app.py" target="_blank">
                    🔗 Code source sur GitHub
                </a>
            </div>

            <footer>
                TP Algorithmique Avancée & Complexité – Master IL
            </footer>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
