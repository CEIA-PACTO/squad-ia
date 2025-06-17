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

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns



# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.data_loader import load_csv

def plot_training_history(history):
    """Plot the training and validation loss curves"""
    plt.figure(figsize=(10, 6))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.plot(history.history['root_mean_squared_error'], label='Training RMSE')
    plt.plot(history.history['val_root_mean_squared_error'], label='Validation RMSE')
    plt.title('Model Training History')
    plt.ylabel('Loss / RMSE')
    plt.xlabel('Epoch')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.savefig('training_history.png')
    plt.show()

def plot_predictions(y_true, y_pred, title="Predicted vs Actual Ratings"):
    """Plot predicted vs actual ratings"""
    plt.figure(figsize=(12, 10))
    
    # Scatter plot of predicted vs actual
    plt.subplot(2, 2, 1)
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([1, 5], [1, 5], 'r--')  # Perfect prediction line
    plt.xlabel('Actual Rating')
    plt.ylabel('Predicted Rating')
    plt.title('Predicted vs Actual')
    plt.grid(True)
    plt.axis('equal')
    
    # Distribution of prediction errors
    plt.subplot(2, 2, 2)
    errors = y_pred - y_true
    plt.hist(errors, bins=20, alpha=0.7)
    plt.axvline(x=0, color='r', linestyle='--')
    plt.xlabel('Prediction Error')
    plt.ylabel('Count')
    plt.title('Error Distribution')
    plt.grid(True)
    
    # Distribution of actual ratings
    plt.subplot(2, 2, 3)
    plt.hist(y_true, bins=np.arange(0.5, 6, 1), alpha=0.7, color='green')
    plt.xlabel('Rating Value')
    plt.ylabel('Count')
    plt.title('Actual Rating Distribution')
    plt.grid(True)
    plt.xticks(range(1, 6))
    
    # Distribution of predicted ratings
    plt.subplot(2, 2, 4)
    plt.hist(y_pred, bins=15, alpha=0.7, color='orange')
    plt.xlabel('Rating Value')
    plt.ylabel('Count')
    plt.title('Predicted Rating Distribution')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('rating_predictions.png')
    plt.show()

def main():
    # Load data
    alunos = load_csv('/Users/orlow/dev/PACTO/Squad-ai/collaborative_filtering/src/data/challenge_ratings.csv')
    ratings = load_csv('/Users/orlow/dev/PACTO/Squad-ai/collaborative_filtering/src/data/interactions.csv')

    # Check if data is loaded correctly
    if alunos is None or ratings is None:
        print("Error loading data.")
        sys.exit(1)

    # Crosstab to create a pivot table - user_id as rows and challenge_id as columns
    pivot_table = pd.crosstab(ratings.user_id, ratings.challenge_id).head()
    print("Pivot Table (first 5 rows):")
    print(pivot_table)
    # Filter the top k users and challenges based on the number of ratings
    k = 15
    g = ratings.groupby('user_id')['rating'].count()
    top_users = g.sort_values(ascending=False)[:k]

    g = ratings.groupby('challenge_id')['rating'].count()
    top_challenges = g.sort_values(ascending=False)[:k]

    # Filter the ratings DataFrame to include only the top k users and challenges
    top_r = ratings.join(top_users, rsuffix='_r', how='inner', on='user_id')
    top_r = top_r.join(top_challenges, rsuffix='_m', how='inner', on='challenge_id')
    
    # Create a pivot table with the top k users and challenges
    pivot_table = pd.crosstab(top_r.user_id, top_r.challenge_id, top_r.rating, aggfunc=np.sum)

    # Encode user and challenge IDs
    user_encoder = LabelEncoder()
    ratings['user_id_encoded'] = user_encoder.fit_transform(ratings['user_id'])
    n_users = ratings['user_id_encoded'].nunique()
    
    challenge_encoder = LabelEncoder()
    ratings['challenge_id_encoded'] = challenge_encoder.fit_transform(ratings['challenge_id'])
    n_challenges = ratings['challenge_id_encoded'].nunique()

    # Ratings preprocessing
    ratings['rating'] = ratings['rating'].astype(np.float32)
    min_rating = ratings['rating'].min()
    max_rating = ratings['rating'].max()

    # Normalize ratings to the range [0, 1]
    ratings['rating'] = (ratings['rating'] - min_rating) / (max_rating - min_rating)
    ratings = ratings[['user_id_encoded', 'challenge_id_encoded', 'rating']]

    # Building the collaborative filtering model, using keras Embedding and Dot layers
    emb_sz = 50

    user = layers.Input(shape=(1,), name='user_id')
    user_embedding = layers.Embedding(n_users, emb_sz, embeddings_regularizer=regularizers.l2(1e-6), name='user_embedding')(user)
    user_embedding = layers.Reshape((emb_sz,))(user_embedding)

    challenge = layers.Input(shape=(1,), name='challenge_id')
    challenge_embedding = layers.Embedding(n_challenges, emb_sz, embeddings_regularizer=regularizers.l2(1e-6), name='challenge_embedding')(challenge)
    challenge_embedding = layers.Reshape((emb_sz,))(challenge_embedding)

    rating = layers.Dot(axes=1, normalize=True, name='rating')([user_embedding, challenge_embedding])
    output = layers.Dense(1, activation='sigmoid', name='output')(rating)

    model = models.Model(inputs=[user, challenge], outputs=output)

    #model compile
    model.compile(loss=losses.MeanSquaredError(), metrics=[metrics.RootMeanSquaredError()],
                  optimizer=optimizers.Adam(learning_rate=0.001))


    model.summary()
    plot_model(model, to_file='collaborative_filtering_model.png', show_shapes=True)

    X = ratings[['user_id_encoded', 'challenge_id_encoded']].values
    y = ratings['rating'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


    
    # Train the model
    history = model.fit(x=[X_train[:,0], X_train[:,1]], y=y_train, 
              batch_size=64, epochs=20, verbose=1,
              validation_data=([X_test[:,0], X_test[:,1]], y_test))
    plot_training_history(history)
    
    
    
    # Prediction
    user_ids_test = X_test[:, 0]
    item_ids_test = X_test[:, 1]
    normalized_pred = model.predict([user_ids_test, item_ids_test])

    original_scale_pred = normalized_pred * 4 + 1  # For [0,1] normal

    original_scale_pred = np.clip(original_scale_pred, 1, 5)

    results = np.column_stack((X_test, original_scale_pred))

    print("Predictions:")
    print(results[:10])

    results_df = pd.DataFrame(results, columns=['user_id', 'challenge_id', 'predicted_rating'])
    print("Results DataFrame:")
    print(results_df.head(3))

    # After prediction
    user_ids_test = X_test[:, 0]
    item_ids_test = X_test[:, 1]
    normalized_pred = model.predict([user_ids_test, item_ids_test])

    original_scale_pred = normalized_pred * 4 + 1  # For [0,1] normalization

    def denormalize(normalized_ratings):
        return normalized_ratings * 4 + 1

    # Visualization:
    y_true_original = denormalize(y_test)
    y_pred_original = denormalize(normalized_pred.flatten())
    plot_predictions(y_true_original, y_pred_original)


if __name__ == "__main__":
    main()


