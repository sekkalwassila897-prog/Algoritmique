import tkinter as tk
from tkinter import messagebox
from math import ceil

# Couleurs
COLOR_BG = "white"
COLOR_NODE = "#E8E8E8"       # default node background
COLOR_SPLIT = "#FFB6C1"      # rose (division highlight)
COLOR_COMPARE = "#FF99CC"    # rose plus clair for comparisons
COLOR_MERGED = "#98FB98"     # pistache (merged)
COLOR_TEXT = "black"

CANVAS_W = 1000
CANVAS_H = 520
LEVEL_HEIGHT = 80
NODE_W = 70
NODE_H = 30
MARGIN_X = 40

class MergeSortTreeSteps:
    def __init__(self, master):
        self.master = master
        master.title("Visualisation tri fusion - étape par étape (dynamique)")
        self.array = []
        self.steps = []               # liste d'étapes (tuples)
        self.current_step = 0

        # UI Top : saisie
        top = tk.Frame(master)
        top.pack(pady=8)

        tk.Label(top, text="Entrer valeurs (séparées par espace ou virgule) :").pack(side=tk.LEFT)
        self.entry = tk.Entry(top, width=30)
        self.entry.pack(side=tk.LEFT, padx=6)
        tk.Button(top, text="Charger", bg="#4CAF50", fg="white", command=self.load_array).pack(side=tk.LEFT, padx=6)
        tk.Button(top, text="Valider et générer étapes", bg="#2196F3", fg="white", command=self.validate_and_generate).pack(side=tk.LEFT, padx=6)

        # canvas central
        self.canvas = tk.Canvas(master, width=CANVAS_W, height=CANVAS_H, bg=COLOR_BG)
        self.canvas.pack(padx=10, pady=6)

        # info / tableau courant
        self.info_label = tk.Label(master, text="Tableau : []", font=("Arial", 12))
        self.info_label.pack(pady=4)

        # bas : boutons navigation
        bottom = tk.Frame(master)
        bottom.pack(pady=6)
        self.prev_btn = tk.Button(bottom, text="Précédent", bg="#9E9E9E", fg="white", state=tk.DISABLED, command=self.prev_step)
        self.prev_btn.pack(side=tk.LEFT, padx=6)
        self.next_btn = tk.Button(bottom, text="Étape suivante", bg="#FF9800", fg="white", state=tk.DISABLED, command=self.next_step)
        self.next_btn.pack(side=tk.LEFT, padx=6)
        self.reset_btn = tk.Button(bottom, text="Réinitialiser", bg="#9E9E9E", fg="white", command=self.reset_all)
        self.reset_btn.pack(side=tk.LEFT, padx=6)

        # structures pour dessiner l'arbre
        self.node_positions = {}   # key=(l,r) -> (x,y)
        self.max_level = 0
        self.node_state = {}       # key=(l,r) -> dict {label:list, color:..., visible:bool}

    def load_array(self):
        raw = self.entry.get().strip()
        if not raw:
            messagebox.showinfo("Erreur", "Entrez des valeurs.")
            return
        # split by comma or space
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

        # Draw simple top-level array representation
        self.draw_initial_array()

    def draw_initial_array(self):
        self.canvas.delete("all")
        # show top array boxes centered
        arr = self.array
        n = len(arr)
        if n == 0:
            return
        # draw small boxes horizontally near top
        y = 20
        total_w = max(300, n*50)
        start_x = (CANVAS_W - total_w)//2 + 20
        box_w = 40
        gap = 10
        x = start_x
        for v in arr:
            self.canvas.create_rectangle(x, y, x+box_w, y+30, fill=COLOR_NODE, outline="black")
            self.canvas.create_text(x+box_w/2, y+15, text=str(v))
            x += box_w + gap

    def validate_and_generate(self):
        if not self.array:
            messagebox.showinfo("Erreur", "Aucun tableau chargé.")
            return
        # build node positions for the full binary split structure
        self.node_positions.clear()
        self.node_state.clear()
        self.steps.clear()
        self.current_step = 0
        n = len(self.array)
        # list all nodes ranges using recursion to know levels
        self.max_level = 0
        self._collect_nodes(0, n-1, 0)
        # compute leaf positions equally spaced
        leaves = [i for i in range(n)]
        leaf_x = {}
        if n == 1:
            leaf_x[0] = CANVAS_W//2
        else:
            span = CANVAS_W - 2*MARGIN_X
            for idx, i in enumerate(leaves):
                leaf_x[i] = MARGIN_X + idx * (span / (n-1))
        # now set positions for all nodes: node x = average of leaf x inside range
        for (l,r), level in list(self.node_positions.items()):
            # compute avg x of leaves l..r
            xs = [leaf_x[i] for i in range(l, r+1)]
            x = sum(xs)/len(xs)
            y = 40 + level * LEVEL_HEIGHT
            self.node_positions[(l,r)] = (x, y)
            # initialize node state empty label
            self.node_state[(l,r)] = {"label": None, "color": COLOR_NODE, "visible": True}

        # generate detailed steps (split then merge with comparisons)
        self.generate_steps(self.array, 0, n-1)

        # draw initial tree (all nodes as grey boxes)
        self.draw_full_tree()
        self.info_label.config(text=f"Tableau : {self.array}  — étapes générées : {len(self.steps)}")
        self.next_btn.config(state=tk.NORMAL)
        self.prev_btn.config(state=tk.DISABLED)

    def _collect_nodes(self, l, r, level):
        # store node and children ranges to compute level depth
        self.node_positions[(l,r)] = level
        if level > self.max_level:
            self.max_level = level
        if l >= r:
            return
        mid = (l+r)//2
        self._collect_nodes(l, mid, level+1)
        self._collect_nodes(mid+1, r, level+1)

    # generate steps with type tags:
    # ('split', (l,r))  -> when we split a node (division highlight)
    # ('compare', (l,r), left_val, right_val, merged_so_far)
    # ('merge_complete', (l,r), merged_array)
    def generate_steps(self, arr, left, right):
        if left > right:
            return []
        if left == right:
          
            self.steps.append(('leaf', (left,right), [arr[left]]))
            return [arr[left]]

        self.steps.append(('split', (left,right), arr[left:right+1].copy()))
        mid = (left+right)//2
        L = self.generate_steps(arr, left, mid)
        R = self.generate_steps(arr, mid+1, right)
        
        i = j = 0
        merged = []
        while i < len(L) and j < len(R):
           
            self.steps.append(('compare', (left,right), L[i], R[j], merged.copy()))
            if L[i] <= R[j]:
                merged.append(L[i]); i += 1
            else:
                merged.append(R[j]); j += 1
        
        while i < len(L):
            self.steps.append(('compare', (left,right), L[i], None, merged.copy()))
            merged.append(L[i]); i += 1
        while j < len(R):
            self.steps.append(('compare', (left,right), None, R[j], merged.copy()))
            merged.append(R[j]); j += 1
        
        self.steps.append(('merge_complete', (left,right), merged.copy()))
        return merged

    # Navigation
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
        # go back one step by reinitializing and replaying up to current_step-1
        if self.current_step == 0:
            return
        self.current_step -= 1
        # reset node_state
        for k in self.node_state:
            self.node_state[k]["label"] = None
            self.node_state[k]["color"] = COLOR_NODE
        # replay all steps up to current_step-1
        for i in range(self.current_step):
            self.apply_step(self.steps[i], replay=True)
        # draw tree according to current states
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
            # draw
            if not replay:
                self.draw_full_tree(highlight_nodes=[rng])
        elif typ == 'split':
            rng = step[1]
            arr = step[2]
            # mark node with split color and label the current subarray
            self.node_state[rng]["label"] = arr
            self.node_state[rng]["color"] = COLOR_SPLIT
            if not replay:
                self.draw_full_tree(highlight_nodes=[rng])
        elif typ == 'compare':
            rng = step[1]
            lv = step[2]   # may be None
            rv = step[3]   # may be None
            merged = step[4]
            # set children highlight: children are (l,mid) and (mid+1,r)
            l, r = rng
            if l==r:
                left_child = (l,r)
                right_child = None
            else:
                mid = (l+r)//2
                left_child = (l, mid)
                right_child = (mid+1, r)
            # set parent label to merged (partial)
            self.node_state[rng]["label"] = merged.copy()
            self.node_state[rng]["color"] = COLOR_MERGED if merged else COLOR_NODE
            # highlight children compared
            # If lv present, find the leaf node or node that currently holds lv:
            highlight = []
            if lv is not None and left_child in self.node_state:
                # color left_child compare color (we won't change label)
                highlight.append(left_child)
            if rv is not None and right_child in self.node_state:
                highlight.append(right_child)
            if not replay:
                self.draw_full_tree(highlight_nodes=highlight, compare_pair=(lv,rv), parent_partial=(rng, merged.copy()))
        elif typ == 'merge_complete':
            rng = step[1]
            merged = step[2]
            self.node_state[rng]["label"] = merged.copy()
            self.node_state[rng]["color"] = COLOR_MERGED
            if not replay:
                self.draw_full_tree(highlight_nodes=[rng])

    # Drawing helpers
    def draw_full_tree(self, highlight_nodes=None, compare_pair=None, parent_partial=None):
        """
        highlight_nodes: list of (l,r) nodes to emphasize (pink)
        compare_pair: tuple (lv,rv) to display near children comparison
        parent_partial: ( (l,r), merged_list ) to show merged partial
        """
        self.canvas.delete("all")
        # Draw lines first (connections)
        for (l,r), (x,y) in self.node_positions.items():
            if l < r:
                mid = (l+r)//2
                left = (l, mid)
                right = (mid+1, r)
                if left in self.node_positions:
                    lx, ly = self.node_positions[left]
                    self.canvas.create_line(x, y+15, lx, ly-15, width=1)
                if right in self.node_positions:
                    rx, ry = self.node_positions[right]
                    self.canvas.create_line(x, y+15, rx, ry-15, width=1)
        # Draw nodes (boxes)
        for (l,r), (x,y) in self.node_positions.items():
            state = self.node_state.get((l,r), {"label":None, "color":COLOR_NODE})
            color = state["color"]
            label = state["label"]
            # if this node is highlighted for comparison, override color
            if highlight_nodes and (l,r) in highlight_nodes:
                color = COLOR_COMPARE
            # draw rectangle
            leftx = x - NODE_W/2
            topy = y - NODE_H/2
            rightx = x + NODE_W/2
            boty = y + NODE_H/2
            self.canvas.create_rectangle(leftx, topy, rightx, boty, fill=color, outline="black")
            # label text: if label is list -> show like [3 27], else show value
            txt = ""
            if label is None:
                txt = f"{l}-{r}"
            else:
                if isinstance(label, list):
                    txt = " ".join(str(v) for v in label)
                else:
                    txt = str(label)
            self.canvas.create_text(x, y, text=txt, fill=COLOR_TEXT)
        # If compare_pair given, draw small texts near children showing values compared
        if compare_pair:
            lv, rv = compare_pair
            # find leftmost node that contains lv and rightmost for rv among highlighted nodes (approx)
            # We'll try to draw near the parent children positions
            if parent_partial:
                (prange, merged) = parent_partial
                l, r = prange
                mid = (l+r)//2
                left = (l, mid)
                right = (mid+1, r)
                if left in self.node_positions and lv is not None:
                    lx, ly = self.node_positions[left]
                    self.canvas.create_text(lx, ly-30, text=f"{lv}", fill="red", font=("Arial", 10, "bold"))
                if right in self.node_positions and rv is not None:
                    rx, ry = self.node_positions[right]
                    self.canvas.create_text(rx, ry-30, text=f"{rv}", fill="red", font=("Arial", 10, "bold"))
                # show parent merged partial near parent
                px, py = self.node_positions[prange]
                self.canvas.create_text(px, py+30, text="merged: " + (" ".join(map(str, merged)) if merged else "[]"), fill="darkgreen", font=("Arial", 10))
        # bottom: show final merged array so far (if current step produced top-level merged)
        # compute top-level label if exists
        top_label = self.node_state.get((0, len(self.array)-1), {}).get("label", None)
        if top_label:
            self.canvas.create_text(CANVAS_W/2, CANVAS_H-20, text="Résultat courant (racine) : " + " ".join(map(str, top_label)), font=("Arial", 12, "bold"), fill="blue")
        else:
            self.canvas.create_text(CANVAS_W/2, CANVAS_H-20, text="Résultat courant (racine) : -", font=("Arial", 12), fill="gray")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = MergeSortTreeSteps(root)
    root.mainloop()

