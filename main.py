import os
import pandas as pd
# from tabulate import tabulate
from dataclasses import dataclass, field

# constante path discribtion
DATA_DIR = "data"

# data base object description
@dataclass
class ObjectDB:
    book_path: str | None = None
    tables: dict = field(default_factory = dict)

    def list_tables(self): # sheet list discription
        return list(self.tables.keys())

class CreateEmptyDB:

    def __init__(self, nameDB: str = "default.xlsx", sheet_name: str = "Main"):
        if not nameDB.lower().endswith(".xlsx"):
            nameDB += ".xlsx"
        os.makedirs(DATA_DIR, exist_ok=True)
        self.path = os.path.join(DATA_DIR, nameDB)
        self.emptyDB = pd.DataFrame(columns=['ID'])
        self.emptyDB.to_excel(self.path, sheet_name=sheet_name, index = False)

class LoadDB:

    def __init__(self, filename: str):
        self.path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Brak pliku: {self.path}")

    def load(self) -> ObjectDB:
        db = ObjectDB(book_path=self.path)
        try:
            xls = pd.ExcelFile(self.path)
            db.tables = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
            return db
        except Exception as e:
            raise RuntimeError(f"Nie udało się wczytać pliku {self.path}: {e}") from e

class ReadDB:

    def __init__(self,db:ObjectDB):
        self.db = db

    def list_tables(self) -> list[str]:
        return self.db.list_tables()

    def get_table(self, table: str) -> pd.DataFrame:
        if table not in self.db.tables:
            raise ValueError(f"Nie ma tabeli/arkusza: {table}")
        return self.db.tables[table]

    def show(self, table: str, n: int = 10) -> None:
        return self.get_table(table).head(n)

    def describe(self, table: str) -> dict:
        df = self.get_table(table)
        return {
            "rows": len(df),
            "cols": len(df.columns),
            "columns": list(df.columns),
        }

class SaveDB:

    def __init__(self, db: ObjectDB):
        self.db = db

    def save(self, out_filename: str | None = None):
        if self.db.book_path is None:
            raise RuntimeError("Brak book_path — nie wiadomo gdzie zapisać.")

        out_path = self.db.book_path if out_filename is None else os.path.join(DATA_DIR, out_filename)

        with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
            for sheet_name, df in self.db.tables.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

class EditDB:

    def __init__(self, db: ObjectDB, table_name: str,):
        self.table_name = table_name
        self.db = db

        try:
            self.df = self.db.tables[self.table_name]  # catch our table

        except KeyError:
            print(f"{self.table_name} takiej tabeli nie ma w danej bazie dannych")

    def add_row(self, row_data: dict):


        row_cols = set(row_data.keys())
        df_cols = set(self.df.columns)

        """Check correction of keys (columns) input"""
        if row_cols != df_cols:
            raise ValueError(f"Hie zgodność kolumn! Brakuje {df_cols - row_cols}; Nadmiar {row_cols-df_cols}")

        new_row = pd.DataFrame([row_data]) # save new row as new data frame

        try:
            """Concatenation main df with new_rof data frame"""
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            self.db.tables[self.table_name] = self.df
            print(f"Wiersz {new_row} został dodany") # message about adding row

        except Exception as e:
            print(f"Błąd w dodowaniu wiersza: {e}")


    def add_column(self, new_column_name:str, default_value=None):

        if new_column_name in self.df.columns:
            print(f"Kolumna{new_column_name} już istnieje")
            return None

        try:
            self.df[new_column_name] = default_value
            self.db.tables[self.table_name] = self.df
            print(f"Kolumna {new_column_name} była pomyślenie stworzona i dodana")

        except Exception as e:
            print(f"Błąd przy dodowanie kolumny: {e}")

        return None

    def update_row(self, row_number: int, column_name: str, update_value):
        try:
            _ = self.df.iloc[row_number]
            _ = self.df[column_name]
            col_idx = self.df.columns.get_loc(column_name)

            """Updating"""
            self.df.iloc[row_number, col_idx] = update_value

            """Save update to our open data base"""
            self.db.tables[self.table_name] = self.df

            print(f"Zmiana {update_value} w wierszu {row_number} i kolumnie {column_name}, została wprowadzona")

        except IndexError:
            print(f"w tabeli nie ma {row_number} wiersza")

        except KeyError:
            print(f"W tabeli nie ma kolumny {column_name}")

        except Exception as e:
            print(f"Błąd {e}")

    def update_column_name(self, column_name: str, new_column_name: str):
        if new_column_name in self.df.columns:
            print(f"Kolumna{new_column_name} już istnieje")
            return None

        try:
            _ = self.df[column_name]
            self.df = self.df.rename(columns={column_name: new_column_name})
            self.db.tables[self.table_name] = self.df
            print(f"Nazwa kolumny {column_name} została zmieniona na {new_column_name}")

        except KeyError:
            print(f"W tabeli nie ma kolumny {column_name}")

        except Exception as e:
            print(f"Błąd {e}")

    def drop_row(self, row_number:int):
        try:
            self.df = self.df.drop(self.df.index[row_number]) # dropping
            self.db.tables[self.table_name] = self.df # save
            print(f"Wiersz {row_number}, został usunięty z tabeli {self.table_name}") # message

        except IndexError:
            print(f"w tabeli nie ma {row_number} wiersza")

        except Exception as e:
            print(f"Błąd {e}")

    def drop_column(self, column_name:str):
        try:
            self.df = self.df.drop(columns=column_name) # dropping column
            self.db.tables[self.table_name] = self.df # save changes to data base
            print(f"Kolumna {column_name}, została usunięta z tabeli {self.table_name}") # message

        except ValueError:
            print(f"Brak kolumny {column_name} w tabeli {self.table_name}")

        except Exception as e:
            print(f"Błąd: {e}")

    def find_by_col(self, column_name: str, value):
        try:
            mask = self.df[column_name] == value
            find_result = self.df[mask]
            if find_result.empty:
                print(f"W kolumnie {column_name} nie wartości {value}")
            print(find_result)

        except ValueError:
            print(f"Brak kolumny {column_name} w tabeli {self.table_name}")

        except Exception as e:
            print(f"Błąd: {e}")

    def find_by_row_number(self, row_number: int):
        try:
            find_result = self.df.iloc[[row_number]]
            print(find_result)

        except IndexError:
            print(f"w tabeli nie ma {row_number} wiersza")

        except Exception as e:
            print(f"Błąd: {e}")

    def sync_and_save(self):
        try:
            """Synchronization"""
            self.db.tables[self.table_name] = self.df

            """Saving"""
            with pd.ExcelWriter(self.db.book_path, engine="openpyxl") as writer:
                for sheet_name, df in self.db.tables.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            print("Zmiany w bazie danych zostały zapisane pomyślenie ")

        except PermissionError:
            print("!!! BŁĄD ZAPISU: Plik Excel jest otwarty w innym programie. Zamknij go i spróbuj ponownie.")

        except Exception as e:
            print(f"Błąd0: {e}")



