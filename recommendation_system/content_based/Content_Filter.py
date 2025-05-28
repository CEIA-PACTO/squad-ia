import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from _tower_model import ItemTower

class Recommender:
    def __init__(self, item_data_path='../dataframes/desafios.csv'):
        self.item_tower = ItemTower(item_data_path)
        self.item_embeddings_df = self.item_tower.get_all_embeddings()

    def recommend_for_persona(self, persona, top_k=5):
        # Filtra os desafios da persona
        persona_df = self.item_tower.df[self.item_tower.df['persona'] == persona]

        if persona_df.empty:
            return f"Nenhum desafio encontrado para persona: {persona}"

        # Calcula vetor médio do usuário simulado
        indices = persona_df.index
        item_vectors = np.array([embedding for embedding in self.item_embeddings_df['embedding']])
        user_vector = item_vectors[indices].mean(axis=0)

        # Similaridade com todos os desafios
        sims = cosine_similarity([user_vector], item_vectors)[0]
        top_indices = sims.argsort()[::-1][:top_k]

        recommendations = []
        for idx in top_indices:
            row = self.item_tower.df.iloc[idx]
            recommendations.append({
                'exercicio': row['exercicio'],
                'tipo': row['tipo'],
                'intensidade': row['intensidade'],
                'descricao': row['descricao'],
                'similarity': float(sims[idx])
            })

        return recommendations

if __name__ == "__main__":
    rec = Recommender()
    persona = "Executor"  # Pode testar com "Analista", "Planejador", "Comunicador"
    recomendacoes = rec.recommend_for_persona(persona)
    for r in recomendacoes:
        print(r)
