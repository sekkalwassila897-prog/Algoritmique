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
        <title>TP1 - Graphes et Arbres</title>
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
            h1 {
                color: #2c3e50;
                text-align: center;
            }
            h3 {
                color: #34495e;
                margin-top: 30px;
            }
            p {
                font-size: 16px;
                line-height: 1.6;
                color: #2c3e50;
            }
            ul {
                margin-left: 20px;
            }
            li {
                margin-bottom: 8px;
                font-size: 15px;
            }
            .info-box {
                background: #f4f9ff;
                border-left: 5px solid #3498db;
                padding: 15px;
                margin-top: 20px;
                border-radius: 6px;
            }
            pre {
                background: #f0f0f0;
                padding: 10px;
                border-radius: 6px;
                overflow-x: auto;
            }
            .links {
                text-align: center;
                margin-top: 30px;
            }
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
            .links a:hover {
                background: #1f6391;
            }
            footer {
                text-align: center;
                margin-top: 40px;
                font-size: 14px;
                color: #7f8c8d;
            }
        </style>
    </head>

    <body>
        <div class="container">
            <h1>TP1 – Graphes et Arbres</h1>

            <p>
                Ce TP a pour objectif de manipuler et visualiser
                les <strong>graphes</strong> et les <strong>arbres</strong>
                à l’aide de Python, en mettant en œuvre des algorithmes
                fondamentaux de parcours et d’analyse.
            </p>

            <h3>Description détaillée du TP</h3>
            <p>
                Les graphes constituent une structure de données essentielle
                pour modéliser de nombreux problèmes réels tels que les réseaux,
                les chemins, ou les relations entre entités.
            </p>
            <p>
                Dans ce TP, l’utilisateur peut :
            </p>
            <ul>
                <li>Créer des graphes à partir d’une matrice d’adjacence</li>
                <li>Manipuler des graphes orientés, non orientés et pondérés</li>
                <li>Visualiser graphiquement les graphes</li>
                <li>Appliquer des algorithmes de parcours (BFS, DFS)</li>
                <li>Calculer des propriétés telles que le diamètre et la densité</li>
                <li>Exporter les matrices d’adjacence au format CSV</li>
            </ul>

            <h3>Implémentation</h3>
            <p>
                L’application originale est une application <strong>Desktop</strong>
                développée en Python à l’aide de <strong>Tkinter</strong>
                pour l’interface graphique et de <strong>NetworkX</strong>
                pour la manipulation et l’analyse des graphes.
            </p>

            <div class="info-box">
                <p>
                    Cette version Web est une version
                    <strong>descriptive et pédagogique</strong>,
                    développée avec <strong>Flask</strong>,
                    afin de répondre aux exigences du TP5
                    concernant le déploiement des projets.
                </p>
            </div>

            <h3>Comment exécuter les TPs localement</h3>
            <div class="info-box">
                <ol>
                    <li>Cloner ou télécharger le dépôt GitHub du projet.</li>
                    <li>Installer Python (version 3.9 ou supérieure).</li>
                    <li>Installer les bibliothèques nécessaires :
                        <pre>pip install tkinter matplotlib networkx</pre>
                    </li>
                    <li>Ouvrir le dossier du projet dans un éditeur de code (ex: VS Code).</li>
                    <li>Lancer l’interface principale :
                        <pre>python index.py</pre>
                    </li>
                    <li>
                        Depuis l’interface principale, sélectionner le TP souhaité
                        (TP1, TP2, TP3 ou TP4) à l’aide des boutons.
                    </li>
                </ol>
            </div>

            <h3>Rapport du TP</h3>
            <div class="info-box">
                <p>
                    Un rapport détaillé au format PDF est disponible.
                    Il présente les concepts théoriques des graphes,
                    les algorithmes utilisés ainsi que des exemples d’exécution.
                </p>
                <p>
                    📄 <a href="https://github.com/sekkalwassila897-prog/Algoritmique/blob/main/TP1/Rapport_TP1.pdf" target="_blank">
                        Consulter le rapport PDF
                    </a>
                </p>
            </div>

            <div class="links">
                <a href="https://github.com/sekkalwassila897-prog/Algoritmique/blob/main/TP1/TP1.py" target="_blank">
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
