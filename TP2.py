import tkinter as tk
from tkinter import ttk, messagebox
from b_arbre_star import BStarTree
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

arbre = None  

# إنشاء النافذة الرئيسية
root = tk.Tk()
root.title("Visualisation B-Arbre et B-Arbre*")
root.geometry("900x650")
root.configure(bg="#1e1e1e")

# متغير لتحديد نوع الشجرة المختارة
type_arbre = tk.StringVar(value="B-Arbre")

# ==== الإطار العلوي لاختيار نوع الشجرة ====
frame_top = tk.Frame(root, bg="#1e1e1e")
frame_top.pack(pady=15)

lbl_type = tk.Label(frame_top, text="Choisissez le type d'arbre :", fg="white", bg="#1e1e1e", font=("Arial", 11, "bold"))
lbl_type.grid(row=0, column=0, padx=10)

radio_barbre = ttk.Radiobutton(frame_top, text="B-Arbre", value="B-Arbre", variable=type_arbre)
radio_barbre.grid(row=0, column=1, padx=10)

radio_barbre_etoile = ttk.Radiobutton(frame_top, text="B-Arbre*", value="B-Arbre*", variable=type_arbre)
radio_barbre_etoile.grid(row=0, column=2, padx=10)

# ==== إدخال order ====
frame_order = tk.Frame(root, bg="#1e1e1e")
frame_order.pack(pady=10)

lbl_order = tk.Label(frame_order, text="Order :", fg="white", bg="#1e1e1e")
lbl_order.grid(row=0, column=0, padx=5)

entry_order = ttk.Entry(frame_order, width=10)
entry_order.grid(row=0, column=1, padx=5)

def verifier_order():
    if not type_arbre.get():
        messagebox.showwarning("Attention", "Veuillez d'abord sélectionner le type d'arbre.")
        return False
    
    val = entry_order.get().strip()
    if not val.isdigit():
        messagebox.showerror("Erreur", "Veuillez entrer un nombre valide pour l'ordre.")
        return False
    
    order = int(val)
    if order < 3:
        messagebox.showerror("Erreur", "L'ordre minimal doit être 3.")
        return False
    
    if type_arbre.get() == "B-Arbre" and order % 2 == 0:
        messagebox.showerror("Erreur", "Pour un B-Arbre, l'ordre doit être impair.")
        return False
    
    return True

# ==== إدخال liste d’arbre ====
frame_list = tk.Frame(root, bg="#1e1e1e")
frame_list.pack(pady=10)

lbl_list = tk.Label(frame_list, text="Liste d'arbre :", fg="white", bg="#1e1e1e")
lbl_list.grid(row=0, column=0, padx=5)

entry_list = ttk.Entry(frame_list, width=50)
entry_list.grid(row=0, column=1, padx=5)

def creer_arbre():
    global arbre
    if not verifier_order():
        return
    
    order = int(entry_order.get())
    liste = entry_list.get().strip()

    # إنشاء الشجرة حسب النوع
    if type_arbre.get() == "B-Arbre*":
        arbre = BStarTree(order)
    else:
        from b_arbre import bTree
        arbre = bTree(order)

    # إدراج المفاتيح المبدئية مع التحقق من التكرار
    if liste:
        try:
            cles = [int(x) for x in liste.split(",") if x.strip() != ""]
            for cle in cles:
                if type_arbre.get() == "B-Arbre*":
                    node, idx = arbre.search(cle)
                else:
                    node_idx = arbre.search(cle)
                    node = node_idx[0] if node_idx else None

                if not node:
                    arbre.insert(cle)
                else:
                    messagebox.showwarning("Attention", f"La clé {cle} existe déjà et n'a pas été ajoutée.")
        except ValueError:
            messagebox.showerror("Erreur", "Liste doit contenir des nombres séparés par des virgules")
            return
    
    update_plot()
    entry_cle.focus_set()
    entry_cle.select_range(0, tk.END)

btn_creer = ttk.Button(frame_list, text="Créer l'arbre", command=creer_arbre)
btn_creer.grid(row=0, column=2, padx=5)

# ==== إدخال clé وأزرار العمليات ====
frame_ops = tk.Frame(root, bg="#1e1e1e")
frame_ops.pack(pady=15)

lbl_cle = tk.Label(frame_ops, text="Clé :", fg="white", bg="#1e1e1e")
lbl_cle.grid(row=0, column=0, padx=5)

entry_cle = ttk.Entry(frame_ops, width=15)
entry_cle.grid(row=0, column=1, padx=5)

def inserer_cle():
    global arbre
    if not verifier_order():
        return

    cle = entry_cle.get().strip()
    if cle == "":
        messagebox.showwarning("Attention", "Veuillez entrer une clé à insérer.")
        entry_cle.focus_set()
        return

    try:
        cle = int(cle)

        # إنشاء الشجرة تلقائيًا إذا لم تكن موجودة
        if arbre is None:
            order = int(entry_order.get())
            if type_arbre.get() == "B-Arbre*":
                arbre = BStarTree(order)
            else:
                from b_arbre import bTree
                arbre = bTree(order)

        # تحقق التكرار
        if type_arbre.get() == "B-Arbre*":
            node, idx = arbre.search(cle)
        else:
            node_idx = arbre.search(cle)
            node = node_idx[0] if node_idx else None

        if node:
            messagebox.showwarning("Attention", f"La clé {cle} existe déjà.")
        else:
            arbre.insert(cle)
            update_plot()

        entry_cle.focus_set()
        entry_cle.select_range(0, tk.END)

    except ValueError:
        messagebox.showerror("Erreur", "La clé doit être un entier.")
        entry_cle.focus_set()

def supprimer_cle():
    global arbre
    if arbre is None:
        messagebox.showwarning("Attention", "Veuillez d'abord créer l'arbre.")
        entry_cle.focus_set()
        return

    cle = entry_cle.get().strip()
    if cle == "":
        messagebox.showwarning("Attention", "Veuillez entrer une clé à supprimer.")
        entry_cle.focus_set()
        return

    try:
        cle = int(cle)
        if type_arbre.get() == "B-Arbre*":
            node, idx = arbre.search(cle)
        else:
            node_idx = arbre.search(cle)
            node = node_idx[0] if node_idx else None

        if node:
            arbre.delete(cle)
            update_plot()
        else:
            messagebox.showwarning("Attention", f"La clé {cle} n'existe pas dans l'arbre.")

        entry_cle.focus_set()
        entry_cle.select_range(0, tk.END)

    except ValueError:
        messagebox.showerror("Erreur", "La clé doit être un entier.")
        entry_cle.focus_set()

def rechercher_cle():
    global arbre
    if arbre is None:
        messagebox.showwarning("Attention", "Veuillez d'abord créer l'arbre.")
        entry_cle.focus_set()
        return

    cle = entry_cle.get().strip()
    if cle == "":
        messagebox.showwarning("Attention", "Veuillez entrer une clé à rechercher.")
        entry_cle.focus_set()
        return

    try:
        cle = int(cle)
        if type_arbre.get() == "B-Arbre*":
            node, idx = arbre.search(cle)
        else:
            node_idx = arbre.search(cle)
            node = node_idx[0] if node_idx else None

        if node:
            messagebox.showinfo("Recherche", f"Clé {cle} trouvée dans le noeud {node.keys}.")
        else:
            messagebox.showinfo("Recherche", f"Clé {cle} non trouvée.")

        entry_cle.focus_set()
        entry_cle.select_range(0, tk.END)

    except ValueError:
        messagebox.showerror("Erreur", "La clé doit être un entier.")
        entry_cle.focus_set()

def reinitialiser():
    global arbre
    arbre = None
    entry_order.delete(0, tk.END)
    entry_list.delete(0, tk.END)
    entry_cle.delete(0, tk.END)
    update_plot()
    messagebox.showinfo("Réinitialisé", "Arbre réinitialisé.")
    entry_cle.focus_set()

btn_inserer = ttk.Button(frame_ops, text="Insérer", command=inserer_cle)
btn_inserer.grid(row=0, column=2, padx=5)
btn_supprimer = ttk.Button(frame_ops, text="Supprimer", command=supprimer_cle)
btn_supprimer.grid(row=0, column=3, padx=5)
btn_rechercher = ttk.Button(frame_ops, text="Rechercher", command=rechercher_cle)
btn_rechercher.grid(row=0, column=4, padx=5)
btn_reset = ttk.Button(frame_ops, text="Réinitialiser", command=reinitialiser)
btn_reset.grid(row=0, column=5, padx=5)

# ==== الرسم ====
fig, ax = plt.subplots(figsize=(12, 5))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(pady=20, fill="both", expand=True)

def _compute_positions(node, positions, depth=0, next_x=[0]):
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
            _compute_positions(child, positions, depth + 1, next_x)
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

def update_plot():
    ax.clear()
    ax.axis('off')
    if arbre is None :
        ax.text(0.5, 0.5, "Ici apparaîtra le dessin de l'arbre", color="white",
                ha="center", va="center", transform=ax.transAxes)
        canvas.draw()
        return

    positions = {}
    _compute_positions(arbre.root, positions, 0, [0])

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
                    ax.plot([px, cx], [py, cy], 'k-', lw=1)

    for node, info in positions.items():
        label = "|".join(str(k) for k in node.keys)
        color = "#b3e5fc" if node.leaf else "#ffe0b2"
        ax.text((info['center'] + offset) * scale, info['y'], f"[{label}]",
                ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.3",
                          facecolor=color, edgecolor="#00796b"))

    min_x = min(info['center'] for info in positions.values()) + offset
    max_x = max(info['center'] for info in positions.values()) + offset
    ax.set_xlim(min_x * scale - 3, max_x * scale + 3)
    ax.set_ylim(-len(positions) - 1, 2)

    canvas.draw()

root.mainloop()
