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

    def show(self, table: str, n: int = 10) -> pd.DataFrame:
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

    def __init__(self, db: ObjectDB):
        self.db = db

    def add_row(self, table_name: str, row_data: dict):

        try:
            df = self.db.tables[table_name] # catch our table
            row_cols = set(row_data.keys())
            df_cols = set(df.columns)

            """Check coorection of keys (columns) input"""
            if row_cols != df_cols:
                raise ValueError(f"Hie zgodność kolumn! Brakuje {df_cols - row_cols}; Nadmiar {row_cols-df_cols}")

            """Adding row"""
            new_row = pd.DataFrame([row_data]) # save new row as new data frame
            self.db.tables[table_name] = pd.concat([df, new_row], ignore_index=True) # concationatioin main df with new_rof data frame

            """Message about adding row"""
            print(f"Wiersz {new_row} został dodany")

            """Errors exception reworker"""

        except KeyError as key:
            print(f"{table_name} takiej tabeli nie ma w danej bazie dannych")

        except Exception as e:
            print(f"Błąd: {e}")