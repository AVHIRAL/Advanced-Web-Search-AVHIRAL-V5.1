import tkinter as tk
from tkinter import ttk
import webbrowser
import googlesearch as gs
import time
import requests
from bs4 import BeautifulSoup
import platform

# Détection du système d'exploitation pour définir la couleur par défaut du bouton
if platform.system() == "Windows":
    DEFAULT_BUTTON_COLOR = "SystemButtonFace"
else:
    DEFAULT_BUTTON_COLOR = "#d9d9d9"  # Une approximation de la couleur par défaut sur Linux

class AdvancedSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Web Search AVHIRAL V5.1 VERSION LINUX")

        self.top_frame = tk.Frame(root)
        self.top_frame.pack(pady=10, fill='x')

        self.label = tk.Label(self.top_frame, text="Entrez un mot-clé:")
        self.label.pack(side='left')

        self.entry = tk.Entry(self.top_frame, width=70)
        self.entry.pack(side='left', padx=10)

        self.button = tk.Button(self.top_frame, text="Rechercher", command=self.search)
        self.button.pack(side='left', padx=10)

        self.clear_button = tk.Button(self.top_frame, text="Clear", command=self.clear_content)
        self.clear_button.pack(side='left', padx=10)

        self.led = tk.Label(self.top_frame, text="●", fg="green", font=("Arial", 16))
        self.led.pack(side='left', padx=5)

        self.scrollbar = tk.Scrollbar(root)
        self.results_text = tk.Text(root, wrap=tk.WORD, cursor="arrow", yscrollcommand=self.scrollbar.set)
        self.results_text.pack(expand=True, fill='both', side='left')
        self.scrollbar.pack(side='left', fill='y')
        self.scrollbar.config(command=self.results_text.yview)

        self.results_text.tag_configure("url_hover", foreground="darkblue", underline=True)
        self.results_text.tag_configure("url", foreground="black")

        self.results = []  
        self.current_index = 0

        # Ajout du label "Recherche en cours..."
        self.status_label = tk.Label(self.top_frame, text="", foreground="red", font=("Arial", 12))
        self.status_label.pack(side='left', padx=10)
        self.root.after(1000, self.blink_status_label)

    def clear_content(self):
        self.entry.delete(0, tk.END)  # Efface le contenu de l'entrée
        self.results_text.delete(1.0, tk.END)  # Efface le texte des résultats
        self.results = []  # Vide la liste des résultats
        self.current_index = 0  # Réinitialise l'index courant

    def search(self):
        # Modifiez l'apparence du bouton pendant la recherche
        self.button.config(bg="red", text="Recherche en cours...")
        self.led.config(fg="red")
        self.status_label.config(text="Recherche en cours...")
        self.root.update()
        
        keyword = self.entry.get()
        self.results_text.delete(1.0, tk.END)

        for result in gs.search(keyword, lang='uk', stop=500):
            self.make_links_clickable(result)
            self.results.append(result)
            self.root.update_idletasks()
        self.led.config(fg="green")

        # Rétablissez l'apparence du bouton après la recherche
        self.button.config(bg=DEFAULT_BUTTON_COLOR, text="Rechercher")
        self.led.config(fg="green")
        self.status_label.config(text="")

        # Bing search
        for result in self.bing_search(keyword, 500):
            self.make_links_clickable(result)
            self.results.append(result)
            self.root.update_idletasks()

        # DuckDuckGo search
        for result in self.duckduckgo_search(keyword, 500):
            self.make_links_clickable(result)
            self.results.append(result)
            self.root.update_idletasks()

    def bing_search(self, query, num_results=500):
        headers = {"User-Agent": "Mozilla/5.0"}
        search_url = f"https://www.bing.com/search?q={query}"
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        results = [link.get('href') for link in soup.find_all('a', href=True, class_='b_attribution')]
        return results[:num_results]

    def duckduckgo_search(self, query, num_results=500):
        headers = {"User-Agent": "Mozilla/5.0"}
        search_url = f"https://duckduckgo.com/html/?q={query}"
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        results = [link.get('href') for link in soup.find_all('a', href=True, class_='result__url')]
        return results[:num_results]
                 
    # Fonction pour faire clignoter le label "Recherche en cours..."
    def blink_status_label(self):
        if self.led.cget("fg") == "red":
            current_color = self.status_label.cget("foreground")
            next_color = "blue" if current_color == "red" else "red"
            self.status_label.config(foreground=next_color)
            self.root.after(1000, self.blink_status_label)

        # Rétablissez l'apparence du bouton après la recherche
        self.button.config(bg=DEFAULT_BUTTON_COLOR, text="Rechercher")
        self.led.config(fg="green")
        self.status_label.config(text="")
               
    def open_clicked_link(self, event):
        tag = self.results_text.tag_names(tk.CURRENT)[0]  
        clicked_range = self.results_text.tag_prevrange(tag, self.results_text.index(tk.CURRENT))
        url = self.results_text.get(clicked_range[0], clicked_range[1])
        webbrowser.open(url.strip())

    def change_cursor_to_hand(self, event, hover_tag):
        self.results_text.tag_add(hover_tag, self.results_text.index(tk.CURRENT), self.results_text.index(tk.CURRENT) + "+1c")
        self.results_text.config(cursor="hand2")

    def change_cursor_to_arrow(self, event, hover_tag=None):
        if hover_tag:
            self.results_text.tag_remove(hover_tag, "1.0", tk.END)
        self.results_text.config(cursor="arrow")

    def navigate_results(self, direction):
        if self.results:
            if direction == "next":
                self.current_index = (self.current_index + 1) % len(self.results)
            elif direction == "prev":
                self.current_index = (self.current_index - 1) % len(self.results)
            self.display_current_result()

    def display_results(self):
        self.results_text.delete(1.0, tk.END)
        for result in self.results:
            self.make_links_clickable(result)

    def make_links_clickable(self, text):
        tag = "url_" + str(self.results_text.index(tk.END))
        self.results_text.insert(tk.END, text + "\n", tag)
        self.results_text.tag_bind(tag, "<Button-1>", self.open_clicked_link)
        self.results_text.tag_bind(tag, "<Enter>", lambda event, t=tag: self.change_cursor_to_hand(event, t))
        self.results_text.tag_bind(tag, "<Leave>", lambda event, t=tag: self.change_cursor_to_arrow(event, t))

    def open_clicked_link(self, event):
        tag = self.results_text.tag_names(tk.CURRENT)[0]
        clicked_range = self.results_text.tag_prevrange(tag, self.results_text.index(tk.CURRENT))
        if clicked_range:
            url = self.results_text.get(clicked_range[0], clicked_range[1])
            webbrowser.open(url.strip())
    
    def change_cursor_to_hand(self, event, hover_tag):
        self.results_text.tag_add("url_hover", self.results_text.index(hover_tag + ".first"), self.results_text.index(hover_tag + ".last"))
        self.results_text.config(cursor="hand2")

    def change_cursor_to_arrow(self, event, hover_tag=None):
        if hover_tag:
            self.results_text.tag_remove("url_hover", "1.0", tk.END)
        self.results_text.config(cursor="arrow")

    def show_url_on_hover(self, url):
        self.url_label.config(text=url)

    def open_clicked_link(self, event):
        tag = self.results_text.tag_names(tk.CURRENT)[0]  # Obtenez le tag du lien cliqué
        clicked_range = self.results_text.tag_prevrange(tag, self.results_text.index(tk.CURRENT))
        url = self.results_text.get(clicked_range[0], clicked_range[1])
        webbrowser.open(url.strip())

    def display_current_result(self):
        self.results_text.delete(1.0, tk.END)
        if self.results:
            self.make_links_clickable(self.results[self.current_index])

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes('-zoomed', True)  # Maximise la fenêtre
    app = AdvancedSearchApp(root)

    # Ajouter une étiquette pour afficher l'URL lors du survol
    app.url_label = tk.Label(root, text="", foreground="blue")
    app.url_label.pack(pady=(0, 10), padx=10, anchor='w')

    root.mainloop()