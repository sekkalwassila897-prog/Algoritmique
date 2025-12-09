import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import csv

# ======================  MAIN APPLICATION CLASS  =======================
class GraphApp:
    def __init__(self, root):
        self.root = root
        # إذا كان root هو Frame (وليس نافذة)، لا نضبط العنوان أو الحجم
        if isinstance(root, tk.Tk):
            self.root.title("🧩 Application de Graphes et Arbres")
            self.root.geometry("1100x700")
        else:
            self.root = root  # داخل إطار رئيسي موجود

        self.root.configure(bg="#ecf0f1")
        self.G = None

        self.main_menu()

    # ======================  Page d'accueil  =======================
    def main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg="#273c75")
        frame.pack(fill="x")

        title = tk.Label(
            frame,
            text="🧩 Application de Graphes et Arbres",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#273c75",
            pady=15,
        )
        title.pack()

        container = tk.Frame(self.root, bg="#f5f6fa")
        container.pack(expand=True)

        tk.Label(
            container,
            text="Choisissez la méthode d'entrée :",
            font=("Arial", 16, "bold"),
            bg="#f5f6fa",
        ).pack(pady=20)

        tk.Button(
            container,
            text="Méthode 1 : Matrice d'adjacence",
            width=30,
            height=2,
            bg="#44bd32",
            fg="white",
            font=("Arial", 14, "bold"),
            command=self.method_matrix,
        ).pack(pady=10)

        tk.Button(
            container,
            text="Méthode 2 : Dessiner un graphe",
            width=30,
            height=2,
            bg="#0097e6",
            fg="white",
            font=("Arial", 14, "bold"),
            command=self.method_draw,
        ).pack(pady=10)

    # ======================  Méthode 1 =======================
    def method_matrix(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Top bar
        topbar = tk.Frame(self.root, bg="#273c75")
        topbar.pack(fill="x")

        tk.Button(
            topbar,
            text="← Retour",
            bg="#718093",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.main_menu,
        ).pack(side="left", padx=10, pady=10)

        tk.Label(
            topbar,
            text="Création via Matrice d'adjacence",
            fg="white",
            bg="#273c75",
            font=("Arial", 16, "bold"),
        ).pack(pady=10)

        # Conteneur principal
        main_frame = tk.Frame(self.root, bg="#ecf0f1")
        main_frame.pack(expand=True, fill="both")

        entry_frame = tk.Frame(main_frame, bg="#ecf0f1")
        entry_frame.pack(pady=10)

        tk.Label(entry_frame, text="Nombre de sommets :", bg="#ecf0f1", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        self.n = tk.IntVar()
        tk.Entry(entry_frame, textvariable=self.n, width=10).pack(side="left")

        tk.Button(
            entry_frame,
            text="Générer matrice",
            bg="#44bd32",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.create_matrix_input,
        ).pack(side="left", padx=10)

    def create_matrix_input(self):
        n = self.n.get()
        if n <= 0:
            messagebox.showerror("Erreur", "Le nombre de sommets doit être positif.")
            return

        for widget in self.root.winfo_children()[1:]:
            widget.destroy()

        # ----- Top Bar -----
        topbar = tk.Frame(self.root, bg="#273c75")
        topbar.pack(fill="x")

        tk.Button(
            topbar,
            text="← Retour",
            bg="#718093",
            fg="white",
            command=self.method_matrix,
        ).pack(side="left", padx=10, pady=10)

        # ----- Corps -----
        body = tk.Frame(self.root, bg="#f5f6fa")
        body.pack(expand=True, fill="both")
        left_frame = tk.Frame(body, bg="#f5f6fa")
        left_frame.pack(side="left", padx=20, pady=20)

        right_frame = tk.Frame(body, bg="white", bd=2, relief="ridge")
        right_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        self.graph_frame = right_frame

        # ----- Titre au-dessus de la matrice -----
        tk.Label(
            left_frame,
            text=f"Matrice {n} × {n}",
            font=("Arial", 14, "bold"),
            bg="#f5f6fa",
        ).pack(pady=10)

        # Matrice
        grid_frame = tk.Frame(left_frame, bg="#dcdde1", bd=2, relief="ridge")
        grid_frame.pack(pady=10)
        self.entries = []

        for i in range(n):
            row = []
            for j in range(n):
                e = tk.Entry(grid_frame, width=6, justify="center", font=("Arial", 10))
                e.grid(row=i, column=j, padx=3, pady=3)
                e.insert(0, "0")
                row.append(e)
            self.entries.append(row)

        # Options
        self.is_oriented = tk.BooleanVar()
        self.is_weighted = tk.BooleanVar()
        tk.Checkbutton(left_frame, text="Orienté", variable=self.is_oriented, bg="#f5f6fa").pack()
        tk.Checkbutton(left_frame, text="Pondéré", variable=self.is_weighted, bg="#f5f6fa").pack()

        # Boutons principaux
        tk.Button(
            left_frame,
            text="Afficher le graphe",
            bg="#0097e6",
            fg="white",
            font=("Arial", 12, "bold"),
            command=lambda: self.display_graph_from_matrix(right_frame),
        ).pack(pady=8)

        tk.Button(
            left_frame,
            text="Calculer propriétés",
            bg="#9c88ff",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.open_properties_window,
        ).pack(pady=8)

        # 🔹 Nouveau : Réinitialiser + Changer sommets
        tk.Button(
            left_frame,
            text="Réinitialiser la matrice",
            bg="#e1b12c",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.reset_matrix,
        ).pack(pady=8)

        tk.Button(
            left_frame,
            text="Changer le nombre de sommets",
            bg="#718093",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.method_matrix,
        ).pack(pady=8)

    def reset_matrix(self):
        for row in self.entries:
            for cell in row:
                cell.delete(0, tk.END)
                cell.insert(0, "0")

    # ================= Afficher le graphe =================
    def display_graph_from_matrix(self, container):
        n = self.n.get()
        try:
            matrix = np.array([[float(self.entries[i][j].get()) for j in range(n)] for i in range(n)])
        except ValueError:
            messagebox.showerror("Erreur", "Tous les champs doivent être des nombres.")
            return

        oriented = self.is_oriented.get()
        weighted = self.is_weighted.get()

        # إنشاء نوع الغراف بدون إضافة weight افتراضياً إذا لم يكن pondéré
        self.G = nx.DiGraph() if oriented else nx.Graph()
        for i in range(n):
            self.G.add_node(i + 1)

        for i in range(n):
            for j in range(n):
                if matrix[i][j] != 0:
                    if weighted:
                        # فقط إذا كان pondéré نضيف الوزن كـ attribute
                        self.G.add_edge(i + 1, j + 1, weight=matrix[i][j])
                    else:
                        # غير مُقَيَّم/غير مُوزَن: نضيف الحافة بدون attribute "weight"
                        self.G.add_edge(i + 1, j + 1)

        # Effacer ancien contenu
        for widget in container.winfo_children():
            widget.destroy()

        # Ajouter boutons d’export
        btn_frame = tk.Frame(container, bg="white")
        btn_frame.pack(fill="x", pady=5)
        tk.Button(btn_frame, text="💾 Sauvegarder Image", bg="#44bd32", fg="white",
                  command=lambda: self.save_graph_image()).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📄 Exporter CSV", bg="#9c88ff", fg="white",
                  command=lambda: self.export_matrix_csv()).pack(side="left", padx=5)

        # Afficher le graphe
        fig, ax = plt.subplots(figsize=(5, 4))
        pos = nx.spring_layout(self.G)

        # ارسم العقد أولاً
        nx.draw_networkx_nodes(self.G, pos, node_color="#44bd32", node_size=800, ax=ax)
        nx.draw_networkx_labels(self.G, pos, font_weight="bold", font_color="white", ax=ax)

        # ارسم الحواف مع تفعيل الأسهم فقط للـ DiGraph
        if oriented:
            # للـ DiGraph: ارسم الحواف مع أسهم واضحة
            nx.draw_networkx_edges(self.G, pos, arrowstyle='->', arrowsize=20, width=2, ax=ax)
        else:
            # للـ Graph غير الموجَّه: ارسم حواف عادية (بدون أسهم)
            nx.draw_networkx_edges(self.G, pos, arrows=False, width=2, ax=ax)

        # تسميات الحواف تظهر فقط اذا كانت pondérée
        if weighted:
            labels = nx.get_edge_attributes(self.G, "weight")
            if labels:
                nx.draw_networkx_edge_labels(self.G, pos, edge_labels=labels, font_color="black", ax=ax)

        ax.set_axis_off()

        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def save_graph_image(self):
        if self.G is None:
            messagebox.showerror("Erreur", "Aucun graphe à sauvegarder.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if file:
            fig, ax = plt.subplots()
            pos = nx.spring_layout(self.G)
            # رسم بسيط عند الحفظ
            nx.draw_networkx_nodes(self.G, pos, node_color="#44bd32", node_size=800, ax=ax)
            nx.draw_networkx_labels(self.G, pos, font_weight="bold", font_color="white", ax=ax)
            if self.G.is_directed():
                nx.draw_networkx_edges(self.G, pos, arrowstyle='->', arrowsize=20, width=2, ax=ax)
            else:
                nx.draw_networkx_edges(self.G, pos, arrows=False, width=2, ax=ax)
            labels = nx.get_edge_attributes(self.G, "weight")
            if labels:
                nx.draw_networkx_edge_labels(self.G, pos, edge_labels=labels, font_color="black", ax=ax)

            ax.set_axis_off()
            plt.savefig(file, bbox_inches="tight")
            plt.close(fig)
            messagebox.showinfo("Succès", "Image enregistrée avec succès ✅")

    def export_matrix_csv(self):
        if not getattr(self, "entries", None):
            messagebox.showerror("Erreur", "Aucune matrice à exporter.")
            return
        n = len(self.entries)
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Fichier CSV", "*.csv")])
        if file:
            with open(file, "w", newline="") as f:
                writer = csv.writer(f)
                for i in range(n):
                    row = [self.entries[i][j].get() for j in range(n)]
                    writer.writerow(row)
            messagebox.showinfo("Succès", "Matrice exportée en CSV ✅")

    # ================= Fenêtre de propriétés =================
    def open_properties_window(self):
        if self.G is None:
            messagebox.showerror("Erreur", "Aucun graphe n'est chargé !")
            return

        prop_window = tk.Toplevel(self.root)
        prop_window.title("Calcul des Propriétés du Graphe")
        prop_window.geometry("700x700")
        prop_window.configure(bg="#f5f6fa")

        tk.Label(
            prop_window,
            text="Sélectionnez les propriétés à calculer :",
            font=("Arial", 14, "bold"),
            bg="#f5f6fa",
        ).pack(pady=15)

        props = [
            "Ordre", "Taille", "Degré moyen", "Sommets isolés", "Sommets pendants",
            "Densité", "Graphe complet ?", "Est un arbre ?", "Composantes connexes",
            "Diamètre", "Contient un cycle ?", "BFS", "DFS"
        ]
        self.prop_vars = {p: tk.BooleanVar() for p in props}

        for p in props:
            tk.Checkbutton(prop_window, text=p, variable=self.prop_vars[p], bg="#f5f6fa", font=("Arial", 12)).pack(anchor="w", padx=40)

        tk.Button(
            prop_window,
            text="Calculer",
            bg="#44bd32",
            fg="white",
            font=("Arial", 13, "bold"),
            command=lambda: self.calculate_properties(prop_window),
        ).pack(pady=15)

    def calculate_properties(self, win):
        results = []
        G = self.G
        if not G:
            return

        try:
            if self.prop_vars["Ordre"].get():
                results.append(f"Ordre du graphe : {G.number_of_nodes()}")
            if self.prop_vars["Taille"].get():
                results.append(f"Taille du graphe : {G.number_of_edges()}")
            if self.prop_vars["Degré moyen"].get():
                deg = sum(dict(G.degree()).values()) / G.number_of_nodes()
                results.append(f"Degré moyen : {deg:.2f}")
            if self.prop_vars["Sommets isolés"].get():
                results.append(f"Sommets isolés : {list(nx.isolates(G))}")
            if self.prop_vars["Sommets pendants"].get():
                pend = [n for n, d in G.degree() if d == 1]
                results.append(f"Sommets pendants : {pend}")
            if self.prop_vars["Densité"].get():
                results.append(f"Densité : {nx.density(G):.2f}")
            if self.prop_vars["Graphe complet ?"].get():
                results.append("Graphe complet" if nx.density(G) == 1 else "Non complet")
            if self.prop_vars["Est un arbre ?"].get():
                results.append("Oui" if nx.is_tree(G) else "Non")
            if self.prop_vars["Composantes connexes"].get():
                comp = list(nx.connected_components(G)) if not G.is_directed() else list(nx.strongly_connected_components(G))
                results.append(f"Composantes connexes : {len(comp)}")
            if self.prop_vars["Diamètre"].get():
                try:
                    results.append(f"Diamètre : {nx.diameter(G)}")
                except:
                    results.append("Diamètre : Graphe non connexe")
            if self.prop_vars["Contient un cycle ?"].get():
                # nx.cycle_basis works only for undirected graphs
                if not G.is_directed():
                    results.append("Oui" if len(list(nx.cycle_basis(G))) > 0 else "Non")
                else:
                    # pour orienté on utilise simple_cycles
                    results.append("Oui" if any(True for _ in nx.simple_cycles(G)) else "Non")
            if self.prop_vars["BFS"].get():
                start = list(G.nodes())[0]
                results.append(f"BFS : {list(nx.bfs_edges(G, start))}")
            if self.prop_vars["DFS"].get():
                start = list(G.nodes())[0]
                results.append(f"DFS : {list(nx.dfs_edges(G, start))}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            return

        result_win = tk.Toplevel(win)
        result_win.title("Résultats")
        result_win.geometry("600x500")
        result_win.configure(bg="#f5f6fa")

        tk.Label(result_win, text="Résultats du calcul :", font=("Arial", 14, "bold"), bg="#f5f6fa").pack(pady=10)
        text_box = tk.Text(result_win, wrap="word", font=("Arial", 12), bg="white", relief="sunken")
        text_box.pack(expand=True, fill="both", padx=20, pady=10)
        text_box.insert("end", "\n".join(results))
        text_box.config(state="disabled")

    # ======================  Méthode 2 =======================
    def method_draw(self):
        """Affiche شاشة اختيار نوع الرسم (choisir le type)."""
        for widget in self.root.winfo_children():
            widget.destroy()

        # --- Top Bar ---
        topbar = tk.Frame(self.root, bg="#273c75")
        topbar.pack(fill="x")

        tk.Button(
            topbar,
            text="← Retour",
            bg="#718093",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.main_menu,
        ).pack(side="left", padx=10, pady=10)

        tk.Label(
            topbar,
            text="✏️ Dessiner un graphe - Choix du type",
            fg="white",
            bg="#273c75",
            font=("Arial", 16, "bold"),
        ).pack(pady=10)

        # Choix du type
        choice_frame = tk.Frame(self.root, bg="#f5f6fa")
        choice_frame.pack(pady=20)
        tk.Label(choice_frame, text="Choisissez le type de graphe :", bg="#f5f6fa", font=("Arial", 13, "bold")).pack(side="left", padx=10)

        self.graph_type = tk.StringVar(value="non_oriente")
        tk.Radiobutton(choice_frame, text="Non orienté", variable=self.graph_type, value="non_oriente", bg="#f5f6fa").pack(side="left")
        tk.Radiobutton(choice_frame, text="Orienté", variable=self.graph_type, value="oriente", bg="#f5f6fa").pack(side="left")
        tk.Radiobutton(choice_frame, text="Pondéré", variable=self.graph_type, value="pondere", bg="#f5f6fa").pack(side="left")

        tk.Button(
            choice_frame,
            text="Valider le choix",
            bg="#44bd32",
            fg="white",
            font=("Arial", 12, "bold"),
            command=lambda: self.setup_draw_interface(self.graph_type.get()),
        ).pack(side="left", padx=15)

    # ======================  Interface de dessin  =======================
    def setup_draw_interface(self, mode):
        for widget in self.root.winfo_children()[1:]:
            widget.destroy()

        self.draw_mode = mode
        self.nodes = {}
        self.edges = []  # list of (src,dst, line_id, extras)
        self.node_counter = 1
        self.selected_node = None
        self.edge_weight_entries = {}  # (src,dst) -> Entry widget (for single-weight edges or directed entries)
        self.directed_weights = {}     # (src,dst) -> float (for storing two weights when needed)
        # for pondere non_oriente with two weights we still keep G as undirected visually,
        # but save directional weights in self.directed_weights
        if mode == "oriente":
            self.G = nx.DiGraph()
        else:
            self.G = nx.Graph()

        # --- Corps principal ---
        body = tk.Frame(self.root, bg="#f5f6fa")
        body.pack(expand=True, fill="both")

        # --- Outils (gauche) ---
        tools = tk.Frame(body, bg="#f5f6fa", width=280)
        tools.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(tools, text="🛠️ Outils de dessin", bg="#f5f6fa", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(tools, text="Ajouter sommet", bg="#44bd32", fg="white", font=("Arial", 11, "bold"),
                  command=lambda: self.set_action("add_node")).pack(fill="x", pady=5)
        tk.Button(tools, text="Supprimer sommet", bg="#e84118", fg="white", font=("Arial", 11, "bold"),
                  command=lambda: self.set_action("del_node")).pack(fill="x", pady=5)

        # Existing add-edge button (single weight or default)
        tk.Button(tools,
                  text="Ajouter arc" if mode == "oriente" else "Ajouter arête",
                  bg="#0097e6", fg="white", font=("Arial", 11, "bold"),
                  command=lambda: self.set_action("add_edge")).pack(fill="x", pady=5)

        # New: if pondere mode, add a button to add an edge with 2 weights (directional)
        if mode == "pondere":
            tk.Button(tools,
                      text="Ajouter arête (2 poids)",
                      bg="#0066cc",
                      fg="white",
                      font=("Arial", 11, "bold"),
                      command=lambda: self.set_action("add_edge_two_weights")).pack(fill="x", pady=5)

        # ---- BUTTON ADDED: Ajouter boucle (loop) ----
        tk.Button(tools, text="Ajouter boucle", bg="#00a8ff", fg="white", font=("Arial", 11, "bold"),
                  command=lambda: self.set_action("add_loop")).pack(fill="x", pady=5)
        # ---------------------------------------------

        tk.Button(tools, text="Exporter matrice", bg="#9c88ff", fg="white", font=("Arial", 11, "bold"),
                  command=self.export_drawn_matrix).pack(fill="x", pady=5)
        tk.Button(tools, text="Réinitialiser", bg="#e1b12c", fg="white", font=("Arial", 11, "bold"),
                  command=self.reset_drawing).pack(fill="x", pady=5)

        # Retour الى اختيار النوع (زر كما طلبت)
        tk.Button(tools, text="← Retour (choisir type)", bg="#718093", fg="white", font=("Arial", 11, "bold"),
                  command=self.method_draw).pack(fill="x", pady=12)

        tk.Button(tools, text="Calculer propriétés", bg="#44bd32", fg="white", font=("Arial", 11, "bold"),
                  command=self.open_properties_window).pack(fill="x", pady=5)

        # --- Zone de dessin (droite) ---
        canvas_frame = tk.Frame(body, bg="white", bd=2, relief="ridge")
        canvas_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tk.Label(canvas_frame, text="🧭 Zone de dessin", bg="white", font=("Arial", 13, "bold")).pack(pady=5)
        self.canvas = tk.Canvas(canvas_frame, bg="white", cursor="cross")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Action courante
        self.current_action = None

    def set_action(self, action):
        self.current_action = action
        self.selected_node = None

    def _edge_key_undirected(self, a, b):
        return tuple(sorted((a, b)))

    def on_canvas_click(self, event):
        if self.current_action == "add_node":
            node_id = self.node_counter
            x, y = event.x, event.y
            node = self.canvas.create_oval(x-15, y-15, x+15, y+15, fill="#44bd32")
            label = self.canvas.create_text(x, y, text=str(node_id), fill="white", font=("Arial", 10, "bold"))
            self.nodes[node_id] = {"node": node, "label": label, "pos": (x, y)}
            self.G.add_node(node_id)
            self.node_counter += 1

        elif self.current_action == "del_node":
            clicked = self.find_node(event.x, event.y)
            if clicked:
                node_id = clicked
                # remove any associated weight entries for incident edges
                keys_to_remove = [k for k in list(self.edge_weight_entries.keys()) if node_id in k]
                for k in keys_to_remove:
                    entry = self.edge_weight_entries.pop(k)
                    try:
                        entry.destroy()
                    except:
                        pass
                # remove any directed weights involving the node
                dkeys = [k for k in list(self.directed_weights.keys()) if node_id in k]
                for k in dkeys:
                    self.directed_weights.pop(k, None)

                # delete canvas items
                self.canvas.delete(self.nodes[node_id]["node"])
                self.canvas.delete(self.nodes[node_id]["label"])
                # remove connected lines from canvas and from self.edges
                remaining_edges = []
                for (src, dst, line_id, extras) in self.edges:
                    if src == node_id or dst == node_id:
                        try:
                            self.canvas.delete(line_id)
                            # extras may contain entry widgets: destroy them
                            if extras:
                                for w in extras:
                                    try:
                                        w.destroy()
                                    except:
                                        pass
                        except:
                            pass
                    else:
                        remaining_edges.append((src, dst, line_id, extras))
                self.edges = remaining_edges
                # remove node from graph and dict
                if self.G.has_node(node_id):
                    self.G.remove_node(node_id)
                del self.nodes[node_id]

        elif self.current_action in ("add_edge", "add_edge_two_weights"):
            clicked = self.find_node(event.x, event.y)
            if not clicked:
                return
            if not self.selected_node:
                self.selected_node = clicked
                # give user feedback (flash)
                x, y = self.nodes[clicked]["pos"]
                tmp = self.canvas.create_oval(x-18, y-18, x+18, y+18, outline="#f39c12")
                self.root.after(250, lambda: self.canvas.delete(tmp))
            else:
                src, dst = self.selected_node, clicked
                if src == dst:
                    self.selected_node = None
                    return
                x1, y1 = self.nodes[src]["pos"]
                x2, y2 = self.nodes[dst]["pos"]

                # draw single line visually
                arrow = tk.LAST if self.draw_mode == "oriente" else None
                line = self.canvas.create_line(x1, y1, x2, y2, arrow=arrow, width=2)
                extras = []  # to keep references to entry widgets created for this line

                if self.current_action == "add_edge_two_weights":
                    # create two small entries near the midpoint (offset a bit)
                    mx, my = (x1 + x2)//2, (y1 + y2)//2
                    # entry for src -> dst (placed slightly above)
                    e1 = tk.Entry(self.canvas, width=6, justify="center")
                    self.canvas.create_window(mx, my-10, window=e1)
                    e1.insert(0, "1")
                    # entry for dst -> src (placed slightly below)
                    e2 = tk.Entry(self.canvas, width=6, justify="center")
                    self.canvas.create_window(mx, my+10, window=e2)
                    e2.insert(0, "1")

                    extras.extend([e1, e2])

                    # store directed weights initial values and widgets
                    self.directed_weights[(src, dst)] = float(e1.get()) if self._safe_float(e1.get()) else 1.0
                    self.directed_weights[(dst, src)] = float(e2.get()) if self._safe_float(e2.get()) else 1.0

                    # bind updates
                    def bind_update(entry_widget, s, d):
                        def update(ev=None):
                            val = 1.0
                            try:
                                val = float(entry_widget.get())
                            except:
                                val = 1.0
                            self.directed_weights[(s, d)] = val
                        entry_widget.bind("<Return>", lambda ev: update())
                        entry_widget.bind("<FocusOut>", lambda ev: update())
                    bind_update(e1, src, dst)
                    bind_update(e2, dst, src)

                    # also keep references in edge_weight_entries for convenience (ordered)
                    self.edge_weight_entries[(src, dst)] = e1
                    self.edge_weight_entries[(dst, src)] = e2

                    # add a visual edge in graph (undirected or directed) with placeholder weight if desired
                    # For undirected visual graph, we add a single edge; matrix will use directed_weights for entries
                    if self.G.is_directed():
                        self.G.add_edge(src, dst, weight=self.directed_weights[(src, dst)])
                    else:
                        # ensure undirected graph has an edge so connectivity works
                        u, v = self._edge_key_undirected(src, dst)
                        self.G.add_edge(u, v, weight=self.directed_weights.get((src, dst), 1.0))
                else:
                    # simple add_edge: create single entry at midpoint if pondere mode else no entry
                    if self.draw_mode == "pondere":
                        mx, my = (x1 + x2)//2, (y1 + y2)//2
                        e = tk.Entry(self.canvas, width=6, justify="center")
                        self.canvas.create_window(mx, my, window=e)
                        e.insert(0, "1")
                        extras.append(e)

                        # store single weight for both directions by default
                        try:
                            w = float(e.get())
                        except:
                            w = 1.0
                        if self.G.is_directed():
                            self.G.add_edge(src, dst, weight=w)
                            self.edge_weight_entries[(src, dst)] = e
                        else:
                            u, v = self._edge_key_undirected(src, dst)
                            self.G.add_edge(u, v, weight=w)
                            # store entries both directions for export convenience
                            self.edge_weight_entries[(src, dst)] = e
                            self.edge_weight_entries[(dst, src)] = e

                        def update_simple(ev=None, s=src, d=dst, entry=e):
                            try:
                                val = float(entry.get())
                            except:
                                val = 1.0
                            if self.G.is_directed():
                                if self.G.has_edge(s, d):
                                    self.G[s][d]["weight"] = val
                                else:
                                    self.G.add_edge(s, d, weight=val)
                            else:
                                u, v = self._edge_key_undirected(s, d)
                                if self.G.has_edge(u, v):
                                    self.G[u][v]["weight"] = val
                                else:
                                    self.G.add_edge(u, v, weight=val)
                        e.bind("<Return>", update_simple)
                        e.bind("<FocusOut>", update_simple)
                    else:
                        # not pondered: add unweighted edge
                        if self.G.is_directed():
                            self.G.add_edge(src, dst)
                        else:
                            u, v = self._edge_key_undirected(src, dst)
                            self.G.add_edge(u, v)

                # save edge record with extras to allow cleanup later
                self.edges.append((src, dst, line, extras))
                self.selected_node = None

        elif self.current_action == "add_loop":
            # Add a loop on clicked node
            clicked = self.find_node(event.x, event.y)
            if not clicked:
                return
            node_id = clicked
            x, y = self.nodes[node_id]["pos"]
            # draw a small oval around the node to represent the loop
            loop = self.canvas.create_oval(x-28, y-28, x+28, y+28, width=2)
            extras = []

            # If pondered mode, add an Entry widget near the loop to input weight
            if self.draw_mode == "pondere":
                e = tk.Entry(self.canvas, width=6, justify="center")
                self.canvas.create_window(x+35, y, window=e)
                e.insert(0, "1")
                extras.append(e)
                # store entry for export/sync
                self.edge_weight_entries[(node_id, node_id)] = e
                # initialize directed_weights for self-loop
                try:
                    val = float(e.get())
                except:
                    val = 1.0
                self.directed_weights[(node_id, node_id)] = val
                # bind updates to keep directed_weights in sync
                def update_loop(ev=None, n=node_id, entry=e):
                    try:
                        v = float(entry.get())
                    except:
                        v = 1.0
                    self.directed_weights[(n, n)] = v
                    # update graph attribute too
                    if self.G.has_edge(n, n):
                        self.G[n][n]["weight"] = v
                    else:
                        self.G.add_edge(n, n, weight=v)
                e.bind("<Return>", update_loop)
                e.bind("<FocusOut>", update_loop)
                # ensure graph edge exists with initial weight
                if self.G.has_edge(node_id, node_id):
                    self.G[node_id][node_id]["weight"] = self.directed_weights[(node_id, node_id)]
                else:
                    self.G.add_edge(node_id, node_id, weight=self.directed_weights[(node_id, node_id)])
            else:
                # not pondered: add unweighted self-loop in graph
                if self.G.is_directed():
                    self.G.add_edge(node_id, node_id)
                else:
                    # for undirected graph, networkx allows self-loop edges too
                    self.G.add_edge(node_id, node_id)

            # save edge record
            self.edges.append((node_id, node_id, loop, extras))

    def _safe_float(self, s):
        try:
            float(s)
            return True
        except:
            return False

    def find_node(self, x, y):
        for nid, info in self.nodes.items():
            xn, yn = info["pos"]
            if (x - xn)**2 + (y - yn)**2 <= 20**2:
                return nid
        return None

    def reset_drawing(self):
        self.canvas.delete("all")
        # destroy any Entry widgets used for weights
        for entry in list(self.edge_weight_entries.values()):
            try:
                entry.destroy()
            except:
                pass
        self.edge_weight_entries.clear()
        self.directed_weights.clear()
        self.nodes.clear()
        self.edges.clear()
        # recreate underlying graph object according to mode
        if self.draw_mode == "oriente":
            self.G = nx.DiGraph()
        else:
            self.G = nx.Graph()
        self.node_counter = 1

    # ======================  Exporter matrice du graphe dessiné =======================
    def export_drawn_matrix(self):
        """Affiche la matrice d’adjacence du graphe dessiné sans modifier l’interface."""
        if self.G is None or len(self.G.nodes) == 0:
            messagebox.showerror("Erreur", "Aucun graphe n'est encore dessiné.")
            return

        # --- avant: مزامنة الأوزان من حقول الإدخال إن وُجدت ---
        # update directed_weights from widgets
        for (s, d), entry in list(self.edge_weight_entries.items()):
            try:
                val = float(entry.get())
            except:
                val = self.directed_weights.get((s, d), 1.0)
            # update directed_weights
            self.directed_weights[(s, d)] = val
            # also update G where appropriate (for visualization/compatibility)
            if self.G.is_directed():
                if self.G.has_edge(s, d):
                    self.G[s][d]["weight"] = val
                else:
                    self.G.add_edge(s, d, weight=val)
            else:
                # undirected G: ensure there is an undirected edge
                u, v = self._edge_key_undirected(s, d)
                if not self.G.has_edge(u, v):
                    # add with some weight (we'll rely on directed_weights for the matrix)
                    self.G.add_edge(u, v, weight=self.directed_weights.get((s, d), 1.0))

        # --- Construction de la matrice d’adjacence ---
        nodes = sorted(self.G.nodes)
        n = len(nodes)
        matrix = np.zeros((n, n), dtype=float)

        # Fill matrix using directed_weights if present (supports two different weights for each direction).
        for i, src in enumerate(nodes):
            for j, dst in enumerate(nodes):
                # priority: directed_weights[(src,dst)] if exists, else G edge attribute weight if exists, else 0
                if (src, dst) in self.directed_weights:
                    matrix[i][j] = self.directed_weights[(src, dst)]
                elif self.G.has_edge(src, dst):
                    matrix[i][j] = self.G[src][dst].get("weight", 1)
                elif not self.G.is_directed() and self.G.has_edge(dst, src):
                    # undirected graphs shouldn't have (dst,src) different, but keep fallback
                    matrix[i][j] = self.G[dst][src].get("weight", 1)
                else:
                    matrix[i][j] = 0

        # --- Création d’une nouvelle fenêtre pour l’afficher ---
        win = tk.Toplevel(self.root)
        win.title("Matrice d'adjacence générée")
        win.geometry("700x450")
        win.configure(bg="#f5f6fa")

        tk.Label(
            win,
            text="📊 Matrice d’adjacence du graphe dessiné",
            font=("Arial", 15, "bold"),
            bg="#f5f6fa",
            fg="#273c75"
        ).pack(pady=15)

        # --- Tableau d’affichage ---
        frame_table = tk.Frame(win, bg="white", bd=2, relief="ridge")
        frame_table.pack(expand=True, fill="both", padx=15, pady=10)

        from tkinter import ttk
        table = ttk.Treeview(frame_table, columns=[str(i) for i in range(n)], show="headings", height=12)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        style.configure("Treeview", font=("Arial", 10))

        for i in range(n):
            table.heading(str(i), text=f"S{i+1}")
            table.column(str(i), width=70, anchor="center")

        for i in range(n):
            values = [
                (int(v) if v % 1 == 0 else round(v, 2)) if v != 0 else 0
                for v in matrix[i]
            ]
            table.insert("", "end", values=values)
        table.pack(expand=True, fill="both")

        # --- Informations sur le graphe ---
        info_text = ""
        if isinstance(self.G, nx.DiGraph):
            info_text += "🔹 Type : Graphe orienté\n"
        else:
            info_text += "🔹 Type : Graphe non orienté\n"

        if any("weight" in d for _, _, d in self.G.edges(data=True)) or len(self.directed_weights) > 0:
            info_text += "🔹 Pondéré : Oui"
        else:
            info_text += "🔹 Pondéré : Non"

        tk.Label(
            win,
            text=info_text,
            bg="#f5f6fa",
            fg="#2f3640",
            font=("Arial", 11, "italic")
        ).pack(pady=5)

        # --- Bouton Export CSV optionnel ---
        def export_csv():
            file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if file:
                with open(file, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([""] + [f"S{i+1}" for i in range(n)])
                    for i, row in enumerate(matrix):
                        writer.writerow([f"S{i+1}"] + list(row))
                messagebox.showinfo("Succès", "Matrice exportée avec succès ✅")

        tk.Button(
            win,
            text="💾 Exporter en CSV",
            bg="#9c88ff",
            fg="white",
            font=("Arial", 11, "bold"),
            command=export_csv
        ).pack(pady=5)
        # ======================  FONCTION SPÉCIALE POUR TP4 =======================
def run_and_return_graph():
    """Ouvre TP1 dans une fenêtre modale et retourne (G, positions) une fois validé."""
    win = tk.Tk()
    win.title("Dessiner un graphe (TP1) depuis TP4")
    app = GraphApp(win)

    result = {"G": None, "pos": None}

    def validate_and_close():
        G = app.G
        if G is None or len(G.nodes) == 0:
            messagebox.showerror("Erreur", "Aucun graphe dessiné !")
            return
        positions = {nid: info["pos"] for nid, info in app.nodes.items()}
        result["G"] = G.copy()
        result["pos"] = positions
        win.destroy()

    # زر يظهر فقط عند فتح TP1 من TP4
    tk.Button(
        win,
        text="✔ Valider et envoyer le graphe à TP4",
        bg="#44bd32",
        fg="white",
        font=("Arial", 13, "bold"),
        command=validate_and_close
    ).pack(pady=10)

    win.mainloop()
    return result["G"], result["pos"]

#======================  MAIN =======================
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()

