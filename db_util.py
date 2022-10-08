import psycopg2


class Database:
    def __init__(self):
        self.con = psycopg2.connect(
            dbname="films_db",
            user="postgres",
            password="2502",
            host="localhost",
            port=5432
        )
        self.cur = self.con.cursor()

    def select(self, query):
        self.cur.execute(query)
        data = self.prepare_data(self.cur.fetchall())

        return data

    def insert(self, query):
        self.cur.execute(query)
        self.con.commit()

    def prepare_data(self, data):
        films = []
        if len(data):
            column_names = [desc[0] for desc in self.cur.description]
            for row in data:
                films += [{col_name: row[key] for key, col_name in enumerate(column_names)}]

        return films


if __name__ == "__main__":
    d = {'2': 2}
    print(**d)
