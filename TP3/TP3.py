import tkinter as tk
from tkinter import messagebox
from math import ceil

# Couleurs
COLOR_BG = "white"
COLOR_NODE = "#E8E8E8"
COLOR_SPLIT = "#FFB6C1"
COLOR_COMPARE = "#FF99CC"
COLOR_MERGED = "#98FB98"
COLOR_TEXT = "black"

CANVAS_W = 1000
CANVAS_H = 520
LEVEL_HEIGHT = 80
NODE_W = 70
NODE_H = 30
MARGIN_X = 40


class MergeSortTreeSteps:
    def __init__(self, parent):
        # ===== Frame principal pour intégrer dans index =====
        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # ===== Éléments de l’interface (anciennement master) =====
        self.array = []
        self.steps = []
        self.current_step = 0

        # UI Top : saisie
        top = tk.Frame(self.frame, bg="white")
        top.pack(pady=8)

        tk.Label(top, text="Entrer valeurs (séparées par espace ou virgule) :", bg="white").pack(side=tk.LEFT)
        self.entry = tk.Entry(top, width=30)
        self.entry.pack(side=tk.LEFT, padx=6)
        tk.Button(top, text="Charger", bg="#4CAF50", fg="white", command=self.load_array).pack(side=tk.LEFT, padx=6)
        tk.Button(top, text="Valider et générer étapes", bg="#2196F3", fg="white", command=self.validate_and_generate).pack(side=tk.LEFT, padx=6)

        # canvas
        self.canvas = tk.Canvas(self.frame, width=CANVAS_W, height=CANVAS_H, bg=COLOR_BG)
        self.canvas.pack(padx=10, pady=6)

        # info
        self.info_label = tk.Label(self.frame, text="Tableau : []", font=("Arial", 12), bg="white")
        self.info_label.pack(pady=4)

        # navigation
        bottom = tk.Frame(self.frame, bg="white")
        bottom.pack(pady=6)

        self.prev_btn = tk.Button(bottom, text="Précédent", bg="#9E9E9E", fg="white", state=tk.DISABLED, command=self.prev_step)
        self.prev_btn.pack(side=tk.LEFT, padx=6)

        self.next_btn = tk.Button(bottom, text="Étape suivante", bg="#FF9800", fg="white", state=tk.DISABLED, command=self.next_step)
        self.next_btn.pack(side=tk.LEFT, padx=6)

        self.reset_btn = tk.Button(bottom, text="Réinitialiser", bg="#9E9E9E", fg="white", command=self.reset_all)
        self.reset_btn.pack(side=tk.LEFT, padx=6)

        # structures
        self.node_positions = {}
        self.max_level = 0
        self.node_state = {}

    # ============================================
    #               LOGIQUE / FONCTIONS
    # ============================================

    def load_array(self):
        raw = self.entry.get().strip()
        if not raw:
            messagebox.showinfo("Erreur", "Entrez des valeurs.")
            return

        parts = [p for p in raw.replace(",", " ").split() if p != ""]

        try:
            arr = [int(p) for p in parts]
        except:
            messagebox.showinfo("Erreur", "Entrez des nombres entiers séparés par espaces ou virgules.")
            return

        self.array = arr
        self.info_label.config(text=f"Tableau : {self.array}")
        self.canvas.delete("all")
        self.node_positions.clear()
        self.node_state.clear()
        self.steps.clear()
        self.current_step = 0
        self.next_btn.config(state=tk.DISABLED)
        self.prev_btn.config(state=tk.DISABLED)

        self.draw_initial_array()

    def draw_initial_array(self):
        self.canvas.delete("all")

        arr = self.array
        n = len(arr)
        if n == 0:
            return

        y = 20
        total_w = max(300, n * 50)
        start_x = (CANVAS_W - total_w) // 2 + 20
        box_w = 40
        gap = 10
        x = start_x

        for v in arr:
            self.canvas.create_rectangle(x, y, x + box_w, y + 30, fill=COLOR_NODE, outline="black")
            self.canvas.create_text(x + box_w / 2, y + 15, text=str(v))
            x += box_w + gap

    def validate_and_generate(self):
        if not self.array:
            messagebox.showinfo("Erreur", "Aucun tableau chargé.")
            return

        self.node_positions.clear()
        self.node_state.clear()
        self.steps.clear()
        self.current_step = 0
        n = len(self.array)

        self.max_level = 0
        self._collect_nodes(0, n - 1, 0)

        leaves = [i for i in range(n)]
        leaf_x = {}

        if n == 1:
            leaf_x[0] = CANVAS_W // 2
        else:
            span = CANVAS_W - 2 * MARGIN_X
            for idx, i in enumerate(leaves):
                leaf_x[i] = MARGIN_X + idx * (span / (n - 1))

        for (l, r), level in list(self.node_positions.items()):
            xs = [leaf_x[i] for i in range(l, r + 1)]
            x = sum(xs) / len(xs)
            y = 40 + level * LEVEL_HEIGHT
            self.node_positions[(l, r)] = (x, y)
            self.node_state[(l, r)] = {"label": None, "color": COLOR_NODE, "visible": True}

        self.generate_steps(self.array, 0, n - 1)

        self.draw_full_tree()
        self.info_label.config(text=f"Tableau : {self.array}  — étapes générées : {len(self.steps)}")

        self.next_btn.config(state=tk.NORMAL)
        self.prev_btn.config(state=tk.DISABLED)

    def _collect_nodes(self, l, r, level):
        self.node_positions[(l, r)] = level
        if level > self.max_level:
            self.max_level = level
        if l >= r:
            return
        mid = (l + r) // 2
        self._collect_nodes(l, mid, level + 1)
        self._collect_nodes(mid + 1, r, level + 1)

    def generate_steps(self, arr, left, right):
        if left > right:
            return []
        if left == right:
            self.steps.append(('leaf', (left, right), [arr[left]]))
            return [arr[left]]

        self.steps.append(('split', (left, right), arr[left:right + 1].copy()))
        mid = (left + right) // 2
        L = self.generate_steps(arr, left, mid)
        R = self.generate_steps(arr, mid + 1, right)

        i = j = 0
        merged = []

        while i < len(L) and j < len(R):
            self.steps.append(('compare', (left, right), L[i], R[j], merged.copy()))
            if L[i] <= R[j]:
                merged.append(L[i])
                i += 1
            else:
                merged.append(R[j])
                j += 1

        while i < len(L):
            self.steps.append(('compare', (left, right), L[i], None, merged.copy()))
            merged.append(L[i])
            i += 1

        while j < len(R):
            self.steps.append(('compare', (left, right), None, R[j], merged.copy()))
            merged.append(R[j])
            j += 1

        self.steps.append(('merge_complete', (left, right), merged.copy()))
        return merged

    def next_step(self):
        if self.current_step >= len(self.steps):
            messagebox.showinfo("Info", "Fin des étapes (tri terminé).")
            return

        step = self.steps[self.current_step]
        self.apply_step(step)
        self.current_step += 1
        self.prev_btn.config(state=tk.NORMAL)

        if self.current_step >= len(self.steps):
            self.next_btn.config(state=tk.DISABLED)

    def prev_step(self):
        if self.current_step == 0:
            return

        self.current_step -= 1

        for k in self.node_state:
            self.node_state[k]["label"] = None
            self.node_state[k]["color"] = COLOR_NODE

        for i in range(self.current_step):
            self.apply_step(self.steps[i], replay=True)

        self.draw_full_tree()

        if self.current_step == 0:
            self.prev_btn.config(state=tk.DISABLED)

        self.next_btn.config(state=tk.NORMAL)

    def apply_step(self, step, replay=False):
        typ = step[0]

        if typ == 'leaf':
            rng = step[1]
            val = step[2]
            self.node_state[rng]["label"] = val
            self.node_state[rng]["color"] = COLOR_MERGED
            if not replay:
                self.draw_full_tree(highlight_nodes=[rng])

        elif typ == 'split':
            rng = step[1]
            arr = step[2]
            self.node_state[rng]["label"] = arr
            self.node_state[rng]["color"] = COLOR_SPLIT
            if not replay:
                self.draw_full_tree(highlight_nodes=[rng])

        elif typ == 'compare':
            rng = step[1]
            lv = step[2]
            rv = step[3]
            merged = step[4]

            l, r = rng
            mid = (l + r) // 2
            left_child = (l, mid)
            right_child = (mid + 1, r)

            self.node_state[rng]["label"] = merged.copy()
            self.node_state[rng]["color"] = COLOR_MERGED if merged else COLOR_NODE

            highlight = []
            if lv is not None and left_child in self.node_state:
                highlight.append(left_child)
            if rv is not None and right_child in self.node_state:
                highlight.append(right_child)

            if not replay:
                self.draw_full_tree(highlight_nodes=highlight, compare_pair=(lv, rv), parent_partial=(rng, merged.copy()))

        elif typ == 'merge_complete':
            rng = step[1]
            merged = step[2]
            self.node_state[rng]["label"] = merged.copy()
            self.node_state[rng]["color"] = COLOR_MERGED
            if not replay:
                self.draw_full_tree(highlight_nodes=[rng])

    def draw_full_tree(self, highlight_nodes=None, compare_pair=None, parent_partial=None):
        self.canvas.delete("all")

        for (l, r), (x, y) in self.node_positions.items():
            if l < r:
                mid = (l + r) // 2
                left = (l, mid)
                right = (mid + 1, r)
                if left in self.node_positions:
                    lx, ly = self.node_positions[left]
                    self.canvas.create_line(x, y + 15, lx, ly - 15)
                if right in self.node_positions:
                    rx, ry = self.node_positions[right]
                    self.canvas.create_line(x, y + 15, rx, ry - 15)

        for (l, r), (x, y) in self.node_positions.items():
            state = self.node_state.get((l, r), {"label": None, "color": COLOR_NODE})
            color = state["color"]
            label = state["label"]

            if highlight_nodes and (l, r) in highlight_nodes:
                color = COLOR_COMPARE

            leftx = x - NODE_W / 2
            topy = y - NODE_H / 2
            rightx = x + NODE_W / 2
            boty = y + NODE_H / 2

            self.canvas.create_rectangle(leftx, topy, rightx, boty, fill=color, outline="black")

            if label is None:
                txt = f"{l}-{r}"
            else:
                txt = " ".join(str(v) for v in label) if isinstance(label, list) else str(label)

            self.canvas.create_text(x, y, text=txt, fill=COLOR_TEXT)

        if compare_pair:
            lv, rv = compare_pair
            if parent_partial:
                (prange, merged) = parent_partial
                l, r = prange
                mid = (l + r) // 2
                left = (l, mid)
                right = (mid + 1, r)

                if left in self.node_positions and lv is not None:
                    lx, ly = self.node_positions[left]
                    self.canvas.create_text(lx, ly - 30, text=str(lv), fill="red", font=("Arial", 10, "bold"))

                if right in self.node_positions and rv is not None:
                    rx, ry = self.node_positions[right]
                    self.canvas.create_text(rx, ry - 30, text=str(rv), fill="red", font=("Arial", 10, "bold"))

                px, py = self.node_positions[prange]
                self.canvas.create_text(px, py + 30, text="merged: " + (" ".join(map(str, merged)) if merged else "[]"),
                                        fill="darkgreen", font=("Arial", 10))

        top_label = self.node_state.get((0, len(self.array) - 1), {}).get("label", None)
        if top_label:
            self.canvas.create_text(CANVAS_W / 2, CANVAS_H - 20, text="Résultat courant (racine) : " +
                                   " ".join(map(str, top_label)), font=("Arial", 12, "bold"), fill="blue")
        else:
            self.canvas.create_text(CANVAS_W / 2, CANVAS_H - 20, text="Résultat courant (racine) : -",
                                   font=("Arial", 12), fill="gray")

    def reset_all(self):
        self.array = []
        self.steps = []
        self.current_step = 0
        self.node_positions.clear()
        self.node_state.clear()
        self.canvas.delete("all")
        self.info_label.config(text="Tableau : []")
        self.entry.delete(0, tk.END)
        self.next_btn.config(state=tk.DISABLED)
        self.prev_btn.config(state=tk.DISABLED)
