import tkinter as tk
from tkinter import ttk, messagebox
from TP2.b_arbre_star import BStarTree
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class BTreeApp:
    def __init__(self, parent):
        self.arbre = None
        self.parent = parent

        # الإطار الرئيسي داخل content_frame
        self.frame = tk.Frame(parent, bg="#1e1e1e")
        self.frame.pack(fill="both", expand=True)

        # نوع الشجرة
        self.type_arbre = tk.StringVar(value="B-Arbre")

        # =============================== الإطار العلوي ===============================

        frame_top = tk.Frame(self.frame, bg="#1e1e1e")
        frame_top.pack(pady=15)

        lbl_type = tk.Label(frame_top, text="Choisissez le type d'arbre :", fg="white",
                            bg="#1e1e1e", font=("Arial", 11, "bold"))
        lbl_type.grid(row=0, column=0, padx=10)

        radio_barbre = ttk.Radiobutton(frame_top, text="B-Arbre", value="B-Arbre",
                                       variable=self.type_arbre)
        radio_barbre.grid(row=0, column=1, padx=10)

        radio_barbre_etoile = ttk.Radiobutton(frame_top, text="B-Arbre*", value="B-Arbre*",
                                              variable=self.type_arbre)
        radio_barbre_etoile.grid(row=0, column=2, padx=10)

        # =============================== order ===============================

        frame_order = tk.Frame(self.frame, bg="#1e1e1e")
        frame_order.pack(pady=10)

        lbl_order = tk.Label(frame_order, text="Order :", fg="white", bg="#1e1e1e")
        lbl_order.grid(row=0, column=0, padx=5)

        self.entry_order = ttk.Entry(frame_order, width=10)
        self.entry_order.grid(row=0, column=1, padx=5)

        # =============================== Liste d’arbre ===============================

        frame_list = tk.Frame(self.frame, bg="#1e1e1e")
        frame_list.pack(pady=10)

        lbl_list = tk.Label(frame_list, text="Liste d'arbre :", fg="white", bg="#1e1e1e")
        lbl_list.grid(row=0, column=0, padx=5)

        self.entry_list = ttk.Entry(frame_list, width=50)
        self.entry_list.grid(row=0, column=1, padx=5)

        btn_creer = ttk.Button(frame_list, text="Créer l'arbre", command=self.creer_arbre)
        btn_creer.grid(row=0, column=2, padx=5)

        # =============================== clé و العمليات ===============================

        frame_ops = tk.Frame(self.frame, bg="#1e1e1e")
        frame_ops.pack(pady=15)

        lbl_cle = tk.Label(frame_ops, text="Clé :", fg="white", bg="#1e1e1e")
        lbl_cle.grid(row=0, column=0, padx=5)

        self.entry_cle = ttk.Entry(frame_ops, width=15)
        self.entry_cle.grid(row=0, column=1, padx=5)

        btn_inserer = ttk.Button(frame_ops, text="Insérer", command=self.inserer_cle)
        btn_inserer.grid(row=0, column=2, padx=5)

        btn_supprimer = ttk.Button(frame_ops, text="Supprimer", command=self.supprimer_cle)
        btn_supprimer.grid(row=0, column=3, padx=5)

        btn_rechercher = ttk.Button(frame_ops, text="Rechercher", command=self.rechercher_cle)
        btn_rechercher.grid(row=0, column=4, padx=5)

        btn_reset = ttk.Button(frame_ops, text="Réinitialiser", command=self.reinitialiser)
        btn_reset.grid(row=0, column=5, padx=5)

        # =============================== الرسم ===============================

        self.fig, self.ax = plt.subplots(figsize=(12, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=20, fill="both", expand=True)

        self.update_plot()

    # =============================== Vérifier order ===============================

    def verifier_order(self):
        if not self.type_arbre.get():
            messagebox.showwarning("Attention", "Veuillez d'abord sélectionner le type d'arbre.")
            return False

        val = self.entry_order.get().strip()
        if not val.isdigit():
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide pour l'ordre.")
            return False

        order = int(val)
        if order < 3:
            messagebox.showerror("Erreur", "L'ordre minimal doit être 3.")
            return False

        if self.type_arbre.get() == "B-Arbre" and order % 2 == 0:
            messagebox.showerror("Erreur", "Pour un B-Arbre, l'ordre doit être impair.")
            return False

        return True

    # =============================== Créer arbre ===============================

    def creer_arbre(self):
        if not self.verifier_order():
            return

        order = int(self.entry_order.get())
        liste = self.entry_list.get().strip()

        if self.type_arbre.get() == "B-Arbre*":
            self.arbre = BStarTree(order)
        else:
            from TP2.b_arbre import bTree
            self.arbre = bTree(order)

        if liste:
            try:
                cles = [int(x) for x in liste.split(",") if x.strip() != ""]
                for cle in cles:

                    if self.type_arbre.get() == "B-Arbre*":
                        node, idx = self.arbre.search(cle)
                    else:
                        node_idx = self.arbre.search(cle)
                        node = node_idx[0] if node_idx else None

                    if not node:
                        self.arbre.insert(cle)
                    else:
                        messagebox.showwarning("Attention",
                                               f"La clé {cle} existe déjà et n'a pas été ajoutée.")
            except ValueError:
                messagebox.showerror("Erreur", "Liste doit contenir des nombres séparés par des virgules")
                return

        self.update_plot()
        self.entry_cle.focus_set()
        self.entry_cle.select_range(0, tk.END)

    # =============================== Insertion ===============================

    def inserer_cle(self):
        if not self.verifier_order():
            return

        cle = self.entry_cle.get().strip()
        if cle == "":
            messagebox.showwarning("Attention", "Veuillez entrer une clé à insérer.")
            self.entry_cle.focus_set()
            return

        try:
            cle = int(cle)

            if self.arbre is None:
                order = int(self.entry_order.get())
                if self.type_arbre.get() == "B-Arbre*":
                    self.arbre = BStarTree(order)
                else:
                    from TP2.b_arbre import bTree
                    self.arbre = bTree(order)

            if self.type_arbre.get() == "B-Arbre*":
                node, idx = self.arbre.search(cle)
            else:
                node_idx = self.arbre.search(cle)
                node = node_idx[0] if node_idx else None

            if node:
                messagebox.showwarning("Attention", f"La clé {cle} existe déjà.")
            else:
                self.arbre.insert(cle)
                self.update_plot()

            self.entry_cle.focus_set()
            self.entry_cle.select_range(0, tk.END)

        except ValueError:
            messagebox.showerror("Erreur", "La clé doit être un entier.")
            self.entry_cle.focus_set()

    # =============================== Suppression ===============================

    def supprimer_cle(self):
        if self.arbre is None:
            messagebox.showwarning("Attention", "Veuillez d'abord créer l'arbre.")
            self.entry_cle.focus_set()
            return

        cle = self.entry_cle.get().strip()
        if cle == "":
            messagebox.showwarning("Attention", "Veuillez entrer une clé à supprimer.")
            self.entry_cle.focus_set()
            return

        try:
            cle = int(cle)

            if self.type_arbre.get() == "B-Arbre*":
                node, idx = self.arbre.search(cle)
            else:
                node_idx = self.arbre.search(cle)
                node = node_idx[0] if node_idx else None

            if node:
                self.arbre.delete(cle)
                self.update_plot()
            else:
                messagebox.showwarning("Attention", f"La clé {cle} n'existe pas dans l'arbre.")

            self.entry_cle.focus_set()
            self.entry_cle.select_range(0, tk.END)

        except ValueError:
            messagebox.showerror("Erreur", "La clé doit être un entier.")
            self.entry_cle.focus_set()

    # =============================== Recherche ===============================

    def rechercher_cle(self):
        if self.arbre is None:
            messagebox.showwarning("Attention", "Veuillez d'abord créer l'arbre.")
            self.entry_cle.focus_set()
            return

        cle = self.entry_cle.get().strip()
        if cle == "":
            messagebox.showwarning("Attention", "Veuillez entrer une clé à rechercher.")
            self.entry_cle.focus_set()
            return

        try:
            cle = int(cle)

            if self.type_arbre.get() == "B-Arbre*":
                node, idx = self.arbre.search(cle)
            else:
                node_idx = self.arbre.search(cle)
                node = node_idx[0] if node_idx else None

            if node:
                messagebox.showinfo("Recherche", f"Clé {cle} trouvée dans le noeud {node.keys}.")
            else:
                messagebox.showinfo("Recherche", f"Clé {cle} non trouvée.")

            self.entry_cle.focus_set()
            self.entry_cle.select_range(0, tk.END)

        except ValueError:
            messagebox.showerror("Erreur", "La clé doit être un entier.")
            self.entry_cle.focus_set()

    # =============================== Réinitialisation ===============================

    def reinitialiser(self):
        self.arbre = None
        self.entry_order.delete(0, tk.END)
        self.entry_list.delete(0, tk.END)
        self.entry_cle.delete(0, tk.END)
        self.update_plot()
        messagebox.showinfo("Réinitialisé", "Arbre réinitialisé.")
        self.entry_cle.focus_set()

    # =============================== رسم الشجرة ===============================

    def _compute_positions(self, node, positions, depth=0, next_x=[0]):
        y = -depth * 3.0
        if node is None or (not node.keys and not node.children):
            return positions
        if node.leaf:
            key_xs = []
            for _ in node.keys:
                x = next_x[0]
                key_xs.append(x)
                next_x[0] += 1
            center = sum(key_xs) / len(key_xs) if key_xs else next_x[0]
            positions[node] = {'center': center, 'y': y, 'key_x': key_xs}
            return positions

        children_ranges = []
        for child in node.children:
            if child and (child.keys or child.children):
                self._compute_positions(child, positions, depth + 1, next_x)
                child_xs = positions[child]['key_x']
                if child_xs:
                    children_ranges.append((min(child_xs), max(child_xs)))

        if not children_ranges:
            return positions

        key_xs = []
        for i in range(len(node.keys)):
            if i < len(children_ranges) - 1:
                l_range = children_ranges[i]
                r_range = children_ranges[i + 1]
                mid = (l_range[1] + r_range[0]) / 2.0
                key_xs.append(mid)

        if not key_xs:
            key_xs = [sum(r for l, r in children_ranges) / len(children_ranges)]

        center = sum(key_xs) / len(key_xs)
        positions[node] = {'center': center, 'y': y, 'key_x': key_xs}
        return positions

    def update_plot(self):
        self.ax.clear()
        self.ax.axis('off')

        if self.arbre is None:
            self.ax.text(0.5, 0.5, "Ici apparaîtra le dessin de l'arbre", color="white",
                         ha="center", va="center", transform=self.ax.transAxes)
            self.canvas.draw()
            return

        positions = {}
        self._compute_positions(self.arbre.root, positions, 0, [0])

        centers = [info['center'] for info in positions.values()]
        avg_center = (max(centers) + min(centers)) / 2 if centers else 0
        offset = -avg_center

        total_keys = sum(len(n.keys) for n in positions.keys())
        if total_keys < 10:
            scale = 1.5
        elif total_keys < 25:
            scale = 1.2
        elif total_keys < 50:
            scale = 1.0
        else:
            scale = 0.8

        for node, info in positions.items():
            if not node.leaf:
                for child in node.children:
                    if child in positions:
                        cx = (positions[child]['center'] + offset) * scale
                        cy = positions[child]['y']
                        px = (info['center'] + offset) * scale
                        py = info['y']
                        self.ax.plot([px, cx], [py, cy], 'k-', lw=1)

        for node, info in positions.items():
            label = "|".join(str(k) for k in node.keys)
            color = "#b3e5fc" if node.leaf else "#ffe0b2"
            self.ax.text((info['center'] + offset) * scale, info['y'], f"[{label}]",
                         ha='center', va='center',
                         bbox=dict(boxstyle="round,pad=0.3",
                                   facecolor=color, edgecolor="#00796b"))

        min_x = min(info['center'] for info in positions.values()) + offset
        max_x = max(info['center'] for info in positions.values()) + offset
        self.ax.set_xlim(min_x * scale - 3, max_x * scale + 3)
        self.ax.set_ylim(-len(positions) - 1, 2)

        self.canvas.draw()
