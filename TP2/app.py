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
        <title>TP2 - B-Arbres et B-Arbres*</title>
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
            <h1>TP2 – B-Arbres et B-Arbres*</h1>

            <p>
                Ce TP a pour objectif de comprendre et manipuler les
                <strong>B-Arbres</strong> et <strong>B-Arbres*</strong>,
                qui sont des structures de données équilibrées largement
                utilisées dans les systèmes de bases de données et les systèmes de fichiers.
            </p>

            <h3>Description détaillée du TP</h3>
            <p>
                Les B-Arbres permettent de stocker un grand nombre de clés
                tout en garantissant des opérations efficaces de recherche,
                insertion et suppression en temps logarithmique.
            </p>
            <p>
                Dans ce TP, l’accent est mis sur :
            </p>
            <ul>
                <li>La création de B-Arbres et B-Arbres* selon un ordre donné</li>
                <li>L’insertion de clés avec gestion des débordements</li>
                <li>La suppression de clés avec redistribution ou fusion des nœuds</li>
                <li>La recherche interactive de clés</li>
                <li>La visualisation graphique de la structure de l’arbre</li>
            </ul>

            <h3>Implémentation</h3>
            <p>
                L’application originale est une application <strong>Desktop</strong>
                développée en Python à l’aide de <strong>Tkinter</strong>
                pour l’interface graphique et <strong>Matplotlib</strong>
                pour la visualisation des arbres.
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
                    Il présente la partie théorique des B-Arbres,
                    la conception de l’application et des exemples d’exécution.
                </p>
                <p>
                    📄 <a href="https://github.com/sekkalwassila897-prog/Algoritmique/blob/main/melgithub/TP2_BTree_BStarTree_Presentation.pdf" target="_blank">
                        Consulter le rapport PDF
                    </a>
                </p>
            </div>

            <div class="links">
                <a href="https://github.com/sekkalwassila897-prog/Algoritmique/blob/main/TP2/TP2.py" target="_blank">
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
