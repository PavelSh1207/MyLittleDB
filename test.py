from main import EditDB, CreateEmptyDB, LoadDB, Table

# TESTS

CreateEmptyDB()
db = LoadDB("default.xlsx").load()

"""REWRITE ReadDB class"""

edit_db = EditDB(db, "Main")
edit_db.add_column("Name", "Pavel")
edit_db.add_column("Age", 1)
edit_db.add_row({"ID":1, "Name":"Pavel", "Age": 110})
edit_db.add_row({"ID":2, "Name":"Ania", "Age": 111})
edit_db.add_row({"ID":3, "Name":"Yegor", "Age": 13})
edit_db.update_row(1, "Age", 12)
edit_db.update_column_name("Age", "age")
# edit_db.drop_row(2)
# edit_db.drop_column("age")
edit_db.find_by_col("age", 12)
edit_db.find_by_row_number(2)
edit_db.show()
edit_db.sync_and_save()

Table(db).add_table("new")





