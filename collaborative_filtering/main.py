import os
import sys

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from tensorflow.keras import models
from tensorflow.keras import layers
from tensorflow.keras import optimizers
from tensorflow.keras import losses
from tensorflow.keras import regularizers
from tensorflow.keras import metrics
from tensorflow.keras.utils import plot_model
from tensorflow.keras.datasets import imdb
from tensorflow.keras.preprocessing.text import text_to_word_sequence
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences


# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.data_loader import load_csv

def main():
    # Load data
    movies = load_csv('src/data/movies.csv')
    ratings = load_csv('src/data/ratings.csv')

    # Check if data is loaded correctly
    if movies is None or ratings is None:
        print("Error loading data.")
        sys.exit(1)

    pivot_table = pd.crosstab(ratings.userId, ratings.movieId).head()

    k = 15
    g = ratings.groupby('userId')['rating'].count()
    top_users = g.sort_values(ascending=False)[:k]

    g = ratings.groupby('movieId')['rating'].count()
    top_movies = g.sort_values(ascending=False)[:k]

    top_r = ratings.join(top_users, rsuffix='_r', how='inner', on='userId')
    top_r = top_r.join(top_movies, rsuffix='_m', how='inner', on='movieId')

    pivot_table = pd.crosstab(top_r.userId, top_r.movieId, top_r.rating, aggfunc=np.sum)


    user_encoder = LabelEncoder()
    ratings['userId_encoded'] = user_encoder.fit_transform(ratings['userId'])
    n_users = ratings['userId_encoded'].nunique()
  
    movie_encoder = LabelEncoder()
    ratings['movieId_encoded'] = movie_encoder.fit_transform(ratings['movieId'])
    n_movies = ratings['movieId_encoded'].nunique()

    ratings['rating'] = ratings['rating'].astype(np.float32)
    min_rating = ratings['rating'].min()
    max_rating = ratings['rating'].max()

    # Building the collaborative filtering model, using keras Embedding and Dot layers

    emb_sz = 50

    user = layers.Input(shape=(1,), name='user_id')
    user_embedding = layers.Embedding(n_users, emb_sz, embeddings_regularizer=regularizers.l2(1e-6), name='user_embedding')(user)
    user_embedding = layers.Reshape((emb_sz,))(user_embedding)

    movie = layers.Input(shape=(1,), name='movie_id')
    movie_embedding = layers.Embedding(n_movies, emb_sz, embeddings_regularizer=regularizers.l2(1e-6), name='movie_embedding')(movie)
    movie_embedding = layers.Reshape((emb_sz,))(movie_embedding)

    rating = layers.Dot(axes=1, normalize=True, name='rating')([user_embedding, movie_embedding])

    model = models.Model(inputs=[user, movie], outputs=rating)

    #model compile
    model.compile(loss=losses.MeanSquaredError(), metrics=[metrics.RootMeanSquaredError()],
                  optimizer=optimizers.Adam(learning_rate=0.001))


    model.summary()
    plot_model(model, to_file='collaborative_filtering_model.png', show_shapes=True)
    
    X = ratings[['userId_encoded', 'movieId_encoded']].values
    y = ratings['rating'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    
    # Train the model
    model.fit(x=[X_train[:,0], X_train[:,1]], y=y_train, 
              batch_size=64, epochs=5, verbose=1,
              validation_data=([X_test[:,0], X_test[:,1]], y_test))
    
    predictions = model.predict([X_test[:,0], X_test[:,1]])

    results = np.column_stack((X_test, predictions))

    print("Predictions:")
    print(results[:10])

    results_df = pd.DataFrame(results, columns=['userId', 'movieId', 'predicted_rating'])
    print("Results DataFrame:")
    print(results_df.head(3))

if __name__ == "__main__":
    main()

    
