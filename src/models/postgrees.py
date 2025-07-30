import psycopg2

class DatabaseInitializer:
    def __init__(self, host, dbname, user, password):
        self.conn = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()

    def create_tables(self):
        create_avaliacao = """
        CREATE TABLE IF NOT EXISTS avaliacao (
            id TEXT,
            Data_Hora_Avaliacao TIMESTAMP,
            Recomendacao_Exercicio TEXT,
            Recomendacao_Equipamento TEXT,
            success BOOLEAN,
            streak INTEGER,
            progress_pct FLOAT,
            rating INTEGER,
            time INTEGER
        );
        """

        create_recomendacao = """
        CREATE TABLE IF NOT EXISTS recomendacao (
            id TEXT,
            Data_Hora TIMESTAMP,
            usuario TEXT,
            Sexo INTEGER,
            Idade FLOAT,
            Altura FLOAT,
            Peso FLOAT,
            Hipertensao INTEGER,
            Diabetes INTEGER,
            IMC FLOAT,
            Nivel INTEGER,
            Objetivo INTEGER,
            Tipo_Fitness INTEGER,
            persona_primaria TEXT,
            persona_secundaria TEXT,
            importancia_amigos INTEGER,
            importancia_resultados INTEGER,
            importancia_diversao INTEGER,
            Recomendacao_Exercicio TEXT,
            Recomendacao_Equipamento TEXT,
            Recomendacao_Fixa_Usada BOOLEAN
        );
        """

        self.cursor.execute(create_avaliacao)
        self.cursor.execute(create_recomendacao)
        self.conn.commit()
        print("Tabelas criadas com sucesso!")

    def close(self):
        self.cursor.close()
        self.conn.close()

    def inserir_avaliacao(self, dados):
        query = """
        INSERT INTO avaliacao (
            id, Data_Hora_Avaliacao, Recomendacao_Exercicio,
            Recomendacao_Equipamento, success, streak,
            progress_pct, rating, time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        self.cursor.execute(query, dados)
        self.conn.commit()
        print("Registro inserido na tabela 'avaliacao' com sucesso.")

    def inserir_varias_avaliacoes(self, dataframe):
        query = """
                INSERT INTO avaliacao (id, Data_Hora_Avaliacao, Recomendacao_Exercicio, \
                                       Recomendacao_Equipamento, success, streak, \
                                       progress_pct, rating, time) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s); \
                """
        dados = [tuple(row) for _, row in dataframe.iterrows()]
        self.cursor.executemany(query, dados)
        self.conn.commit()
        print(f"{len(dados)} registros inseridos na tabela 'avaliacao'.")

if __name__ == "__main__":
    db = DatabaseInitializer(
        host="localhost",
        dbname="gameficacao",
        user="admin",
        password="admin"
    )
    db.create_tables()
    db.close()
