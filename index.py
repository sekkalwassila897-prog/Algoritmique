import tkinter as tk
from tkinter import ttk
from TP1 import GraphApp

# ===== نافذة رئيسية =====
root = tk.Tk()
root.title("TP Algorithmique - Ingénierie Logiciel")
root.geometry("950x600")

# 👑 لوحة أزرق ملكي احترافية
HEADER_COLOR  = "#0A1F44"   # أزرق ملكي غامق للرأس
SIDEBAR_COLOR = "#0A1F44"   # أزرق متوسط للقائمة الجانبية
BUTTON_COLOR  = "#1E4DB7"   # أزرق ملكي ناصع للأزرار
BUTTON_HOVER  = "#3C6EE8"   # أزرق فاتح لامع عند المرور
TEXT_COLOR    = "#FFFFFF"   # أبيض نقي للنصوص
ACCENT_COLOR  = "#AFCBFF"   # أزرق سماوي فاتح للعناوين الثانوية
# FROM MEHDI 
# ===== العنوان في الأعلى =====
header = tk.Label(root, text="Matière : Algorithmique Avancée & Complexité", font=("Arial", 18, "bold"),
                  bg=HEADER_COLOR, fg="white", pady=10)
header.pack(fill=tk.X)

# ===== الإطار الرئيسي =====
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# ===== القائمة الجانبية =====
menu_frame = tk.Frame(main_frame, bg=SIDEBAR_COLOR, width=180)
menu_frame.pack(side=tk.LEFT, fill=tk.Y)

# ===== الإطار الذي سيعرض محتوى كل TP =====
content_frame = tk.Frame(main_frame, bg="white")
content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# ===== دالة عرض المحتوى =====
def show_tp_content(tp_number):
    for widget in content_frame.winfo_children():
        widget.destroy()

    if tp_number == 1:
        GraphApp(content_frame)
    elif tp_number == 2:
        BTreeApp(content_frame)
    else:
        label = tk.Label(content_frame, text=f"Contenu du TP{tp_number}",
                         font=("Arial", 16), bg="white", fg=TEXT_COLOR)
        label.pack(pady=30)

# ===== تأثير اللون عند المرور =====
def on_enter(e):
    e.widget["bg"] = BUTTON_HOVER

def on_leave(e):
    e.widget["bg"] = BUTTON_COLOR

# ===== أسماء الـ TP =====
tp_names = [
    "TP1 – Explorer et dessiner des arbres et des graphes",
    "TP2 - Manipuler les arbres equilibrés",
    "TP3 - Algorithmes de tri",
    "TP4 - Algorithmes classiques sur les graphes",
    "TP5 - Déploiement des projets avec Git , Github et un service d'hébergement web"
]

# ===== أزرار الـ TP =====
for i, name in enumerate(tp_names, start=1):
    btn = tk.Button(menu_frame, text=name, font=("Arial", 11, "bold"),
                    bg=BUTTON_COLOR, fg=TEXT_COLOR, relief="flat",
                    anchor="w", padx=10, pady=5, wraplength=160,
                    command=lambda i=i: show_tp_content(i))
    btn.pack(fill=tk.X, padx=10, pady=6)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

root.mainloop()
