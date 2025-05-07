import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from _tower_cliente import UserTower
from _tower_model import ItemTower

class Recommender:
    def __init__(self, user_data_path='../dataframes/avaliacaofisica.csv', item_data_path='../dataframes/desafios.csv'):
        self.user_tower = UserTower(user_data_path)
        self.item_tower = ItemTower(item_data_path)

        # Obtenção de embeddings para usuários e desafios
        self.user_embeddings_df = self.user_tower.get_all_embeddings()
        self.item_embeddings_df = self.item_tower.get_all_embeddings()

    def recommend_for_user(self, cliente_codigo):
        # Obtenção do vetor do usuário
        user_vector = self.user_tower.get_user_embedding(cliente_codigo)

        if user_vector is None:
            return "Usuário não encontrado."

        # Obtenção dos vetores de todos os itens (desafios)
        item_vectors = np.array([embedding for embedding in self.item_embeddings_df['embedding']])

        # Cálculo da similaridade do cosseno entre o usuário e todos os itens
        sims = cosine_similarity([user_vector], item_vectors)[0]

        # Obtenção dos índices dos itens mais similares
        item_indices = np.argsort(sims)[::-1]

        # Retorna as recomendações com os desafios mais similares
        recommendations = []
        for idx in item_indices[:5]:  # Top 5 recomendações
            desafio_codigo = self.item_embeddings_df.iloc[idx]['desafio_codigo']
            similarity_score = sims[idx]
            recommendations.append({'desafio_codigo': desafio_codigo, 'similarity': similarity_score})

        return recommendations

# Exemplo de uso
if __name__ == "__main__":
    rec = Recommender()
    cliente_codigo = 590  # ID do cliente
    recomendacoes = rec.recommend_for_user(cliente_codigo)
    print(recomendacoes)
