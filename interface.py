import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from main import ObjectDB, LoadDB, EditDB, Table, SaveDB, CreateEmptyDB
import os


class DatabaseApp:
    def __init__(self, root: tk.Tk):
        self.root: tk.Tk = root
        self.root.title("Excel Database")
        self.root.geometry("1100x700")

        self.db: ObjectDB | None = None
        self.current_editor: EditDB | None = None

        self._setup_ui()

    def _setup_ui(self):

        # TOP PANEL
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.pack(fill=tk.X)

        ttk.Button(top_frame, text="📂 Otwórz", command=self.load_action).pack(side=tk.LEFT, padx=5)
        # Wewnątrz metody _setup_ui, w sekcji TOP TOOLBAR:
        # ttk.Button(top_frame, text="✨ Nowa Baza", command=self.create_new_db_action).pack(side=tk.LEFT, padx=5)

        self.sheet_combo = ttk.Combobox(top_frame, state="readonly")
        self.sheet_combo.pack(side=tk.LEFT, padx=5)
        self.sheet_combo.bind("<<ComboboxSelected>>", self.switch_table_action)

        ttk.Button(top_frame, text="➕ Nowy Arkusz", command=self.add_table_action).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="❌ Usuń Arkusz", command=self.delete_table_action).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="💾 ZAPISZ PLIK", command=self.save_to_disk_action).pack(side=tk.RIGHT, padx=5)

        # SEARCH PANEL
        search_frame = ttk.LabelFrame(self.root, text=" Wyszukiwanie i Podświetlanie ", padding="5")
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        # Wybór kolumny
        ttk.Label(search_frame, text="Kolumna:").pack(side=tk.LEFT, padx=5)
        self.search_col_combo = ttk.Combobox(search_frame, state="readonly", width=15)
        self.search_col_combo.pack(side=tk.LEFT, padx=5)

        # Pole wartości
        ttk.Label(search_frame, text="Szukana fraza:").pack(side=tk.LEFT, padx=5)
        self.search_val_entry = ttk.Entry(search_frame, width=20)
        self.search_val_entry.pack(side=tk.LEFT, padx=5)

        # Przycisk 1: Szukaj w kolumnie
        ttk.Button(search_frame, text="🔍 Podświetl Kolumnę/Wiersze",
                   command=self.search_and_highlight_col).pack(side=tk.LEFT, padx=5)

        # Przycisk 2: Szukaj po indeksie
        ttk.Button(search_frame, text="🔢 Idź do Indeksu",
                   command=self.highlight_index_action).pack(side=tk.LEFT, padx=5)

        # Przycisk 3: Reset podświetlenia
        ttk.Button(search_frame, text="🔄 Reset Widoku",
                   command=self._refresh_grid).pack(side=tk.LEFT, padx=5)

        # GRID
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(self.tree_frame, show="headings")
        self.tree.tag_configure('highlight', background='yellow')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrolly = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollx = ttk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)

        scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        scrollx.pack(fill=tk.X)

        # --- Panel Akcji na Danych ---
        action_frame = ttk.LabelFrame(self.root, text=" Operacje na tabeli ", padding="10")
        action_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(action_frame, text="➕ Dodaj Wiersz", command=self.add_row_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="➖ Usuń Wiersz", command=self.delete_row_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📊 Dodaj Kolumnę", command=self.add_column_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🗑️ Usuń Kolumnę", command=self.delete_column_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📝 Edytuj Wiersz", command=self.update_row_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="✏️ Zmień nazwę kolumny", command=self.update_column_action).pack(side=tk.LEFT,
                                                                                                        padx=5)

    # --- LOGIKA PRZYCISKÓW ---
    """
    def create_new_db_action(self):
        # 1. Pytamy o nazwę nowej bazy
        db_name = simpledialog.askstring("Nowa Baza", "Podaj nazwę dla nowej bazy danych:")

        if db_name:
            try:

                # Tworzymy fizyczny plik Excel
                creator = CreateEmptyDB(nameDB=db_name, sheet_name="Main")
                full_path = creator.path

                if os.path.exists(full_path):
                    # Tutaj ładujemy bazę do głównego obiektu aplikacji
                    self.current_edit_db = LoadDB(full_path).load()

                    # Ustawiamy pierwszy arkusz jako aktywny (Twoja klasa CreateEmptyDB tworzy "Main")
                    self.current_editor = self.current_edit_db.open_table("Main")

                    # 4. Odświeżamy interfejs
                    self._update_sheet_list()
                    self._refresh_grid()
                    messagebox.showinfo("Sukces", f"Baza utworzona w:\n{full_path}")
                else:
                    raise FileNotFoundError(f"System nie odnalazł pliku w: {full_path}")

                messagebox.showinfo("Sukces", f"Baza '{db_name}' została utworzona w folderze danych!")

            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się utworzyć bazy: {e}")
    """

    def load_action(self):
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if path:
            self.db = LoadDB(path).load()
            self._update_sheet_list()

    def _update_sheet_list(self):
        """Odświeża listę arkuszy w rozwijanym menu"""
        tables = self.db.list_tables()
        self.sheet_combo['values'] = tables
        if tables:
            self.sheet_combo.current(0)
            self.switch_table_action()

    def switch_table_action(self, event=None):
        if not self.db: return
        name = self.sheet_combo.get()
        self.current_editor = EditDB(self.db, name)
        self._refresh_grid()

    def _refresh_grid(self):
        """Kluczowa metoda: czyści grid i rysuje go od nowa z danych Pandas"""
        self.tree.delete(*self.tree.get_children())
        df = self.current_editor.df
        self.tree["columns"] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        for idx, row in df.iterrows():
            self.tree.insert("", tk.END, iid=idx, values=list(row))

    def add_row_action(self):
        # 1. Strażnik - sprawdza czy tabela jest wybrana
        if not self.current_editor:
            return

        # 2. Tworzenie okna popup
        popup = tk.Toplevel(self.root)
        popup.title("Dodaj nowy wiersz")
        popup.grab_set()  # Sprawia, że okno jest "nad" głównym (modalne)

        # Słownik na obiekty Entry, żeby móc z nich potem wyciągnąć tekst
        entry_widgets = {}
        cols = self.current_editor.df.columns

        # 3. Dynamiczne tworzenie pól dla każdej kolumny
        for i, col in enumerate(cols):
            ttk.Label(popup, text=f"{col}:").grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ttk.Entry(popup)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry_widgets[col] = entry  # Zapamiętujemy pole Entry

        # 4. Funkcja wywoływana po kliknięciu "Zatwierdź"
        def submit():
            # Pobieramy tekst z każdego pola Entry
            row_data = {col: entry.get() for col, entry in entry_widgets.items()}

            for col, entry in entry_widgets.items():
                val = entry.get()

                # --- Mechanizm rozpoznawania liczb ---
                # 1. Sprawdzamy czy to liczba całkowita (np. 123)
                if val.isdigit():
                    row_data[col] = int(val)
                else:
                    try:
                        # 2. Sprawdzamy czy to liczba zmiennoprzecinkowa (np. 12.5)
                        # Zamieniamy przecinek na kropkę, jeśli użytkownik wpisał po polsku
                        clean_val = val.replace(',', '.')
                        row_data[col] = float(clean_val)
                    except ValueError:
                        # 3. Jeśli to nie liczba, zostawiamy jako tekst
                        row_data[col] = val

            try:
                # Wywołujemy logikę z Core (Plik A)
                self.current_editor.add_row(row_data)
                # Odświeżamy tabelę w głównym oknie (Plik B)
                self._refresh_grid()
                # Zamykamy popup
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się dodać wiersza: {e}")

        # 5. Przycisk zatwierdzający na dole okna popup
        submit_btn = ttk.Button(popup, text="Dodaj Rekord", command=submit)
        submit_btn.grid(row=len(cols), column=0, columnspan=2, pady=15)

    def delete_row_action(self):
        selected = self.tree.selection()
        if selected:
            self.current_editor.drop_row(int(selected[0]))
            self._refresh_grid()

    def add_column_action(self):
        if not self.current_editor: return
        new_col = simpledialog.askstring("Kolumna", "Nazwa nowej kolumny:")
        if new_col:
            self.current_editor.add_column(new_col)
            self._refresh_grid()

    def add_table_action(self):
        if not self.db: return
        name = simpledialog.askstring("Arkusz", "Nazwa nowego arkusza:")
        if name:
            Table(self.db).add_table(name)
            self._update_sheet_list()

    def delete_table_action(self):
        if not self.db: return
        name = self.sheet_combo.get()
        if messagebox.askyesno("Usuwanie", f"Czy usunąć arkusz {name}?"):
            Table(self.db).delete_table(name)
            self._update_sheet_list()

    def save_to_disk_action(self):
        if self.db:
            SaveDB(self.db).save(self.db.book_path)
            messagebox.showinfo("Zapis", "Plik Excel został zaktualizowany!")

    def delete_column_action(self):
        # Sprawdzamy "strażnika", czy tabela jest otwarta
        if not self.current_editor:
            return

        # Pytamy użytkownika, którą kolumnę usunąć
        col_to_delete = simpledialog.askstring("Usuwanie kolumny",
                                               "Wpisz dokładną nazwę kolumny do usunięcia:")

        if col_to_delete:
            # Potwierdzenie, bo to operacja nieodwracalna (do momentu zapisu)
            confirm = messagebox.askyesno("Potwierdzenie",
                                          f"Czy na pewno chcesz usunąć kolumnę '{col_to_delete}'?")
            if confirm:
                try:
                    self.current_editor.drop_column(col_to_delete)
                    # KLUCZOWE: Odświeżamy grid, żeby kolumna zniknęła z ekranu
                    self._refresh_grid()
                except ValueError as e:
                    messagebox.showerror("Błąd", str(e))

    def update_column_action(self):
        if not self.current_editor:
            return

            # Tworzymy dedykowane okno
        popup = tk.Toplevel(self.root)
        popup.title("Zmień nazwę kolumny")
        popup.geometry("350x200")
        popup.grab_set()  # Okno modalne

        # Pobieramy aktualne kolumny
        current_cols = list(self.current_editor.df.columns)

        # UI wewnątrz okna
        ttk.Label(popup, text="Wybierz kolumnę:").pack(pady=(15, 0))
        col_to_change = ttk.Combobox(popup, values=current_cols, state="readonly", width=30)
        col_to_change.pack(pady=5)
        if current_cols: col_to_change.current(0)

        ttk.Label(popup, text="Nowa nazwa:").pack(pady=(10, 0))
        new_name_entry = ttk.Entry(popup, width=33)
        new_name_entry.pack(pady=5)
        new_name_entry.focus_set()  # Ustaw kursor od razu w polu tekstowym

        def submit():
            old_n = col_to_change.get()
            new_n = new_name_entry.get().strip()

            try:
                # Próba wykonania zmiany w Core
                self.current_editor.update_column_name(old_n, new_n)
                # Jeśli się udało -> odświeżamy i zamykamy
                self._refresh_grid()
                popup.destroy()
                messagebox.showinfo("Sukces", f"Zmieniono nazwę '{old_n}' na '{new_n}'")
            except ValueError as e:
                # Tutaj przechwytujemy nasz wyjątek z Core i pokazujemy go użytkownikowi
                messagebox.showerror("Błąd walidacji", str(e))

        # Przyciski
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Zmień nazwę", command=submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Anuluj", command=popup.destroy).pack(side=tk.LEFT, padx=5)

    def update_row_action(self):
        selected = self.tree.selection()
        if not selected or not self.current_editor:
            messagebox.showwarning("Uwaga", "Zaznacz wiersz do edycji!")
            return

        idx = int(selected[0])
        current_values = self.current_editor.df.iloc[idx].to_dict()

        popup = tk.Toplevel(self.root)
        popup.title(f"Edycja wiersza {idx}")

        entry_widgets = {}
        for i, (col, val) in enumerate(current_values.items()):
            ttk.Label(popup, text=f"{col}:").grid(row=i, column=0, padx=10, pady=5)
            e = ttk.Entry(popup)
            e.insert(0, str(val))  # Wstawiamy obecną wartość
            e.grid(row=i, column=1, padx=10, pady=5)
            entry_widgets[col] = e

        def submit():
            updated_data = {}
            for col, entry in entry_widgets.items():
                val = entry.get()
                # Próba konwersji na liczbę (identyczna logika jak przy dodawaniu)
                if val.isdigit():
                    updated_data[col] = int(val)
                else:
                    try:
                        updated_data[col] = float(val.replace(',', '.'))
                    except ValueError:
                        updated_data[col] = val

            self.current_editor.update_row(idx, updated_data)
            self._refresh_grid()
            popup.destroy()

        ttk.Button(popup, text="Zapisz zmiany", command=submit).grid(row=len(current_values), columnspan=2, pady=10)

    def search_and_highlight_col(self):
        """Podświetla kolumnę i pasujące wiersze"""
        if not self.current_editor:
            return

        target_col = self.search_col_combo.get()
        search_val = self.search_val_entry.get().strip().lower()

        if not target_col:
            messagebox.showwarning("Uwaga", "Wybierz kolumnę!")
            return

        # 1. Reset widoku (nagłówki i tagi)
        for col in self.current_editor.df.columns:
            self.tree.heading(col, text=col)
        for item in self.tree.get_children():
            self.tree.item(item, tags=())

        # 2. Wyróżnienie nagłówka
        self.tree.heading(target_col, text=f"➔ {target_col.upper()} ➔")

        # 3. Podświetlanie
        if not search_val: return

        col_idx = list(self.current_editor.df.columns).index(target_col)
        found = False

        for item in self.tree.get_children():
            row_values = self.tree.item(item, 'values')
            if str(row_values[col_idx]).lower() == search_val:
                self.tree.item(item, tags=('highlight',))
                if not found:
                    self.tree.see(item)
                    found = True

    def highlight_index_action(self):
        """Podświetla wiersz po jego numerze (ID)"""
        if not self.current_editor: return
        val = self.search_val_entry.get().strip()

        # Reset tagów
        for item in self.tree.get_children():
            self.tree.item(item, tags=())

        if self.tree.exists(val):
            self.tree.item(val, tags=('highlight',))
            self.tree.see(val)
        else:
            messagebox.showinfo("Błąd", "Nie znaleziono takiego indeksu")

    def _refresh_grid(self):
        """Pamiętaj, aby tutaj dodać tag_configure!"""
        self.tree.delete(*self.tree.get_children())
        # Konfiguracja koloru (bez tego żółty tło nie zadziała)
        self.tree.tag_configure('highlight', background='yellow')

        df = self.current_editor.df
        self.tree["columns"] = list(df.columns)

        # Aktualizacja listy kolumn w wyszukiwarce
        self.search_col_combo['values'] = list(df.columns)

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        for idx, row in df.iterrows():
            self.tree.insert("", tk.END, iid=idx, values=list(row))

if __name__ == "__main__":
    app_root = tk.Tk()
    app = DatabaseApp(app_root)
    app_root.mainloop()