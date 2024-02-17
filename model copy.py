import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Embedding, LSTM, Dense, Input
from datasets import load_dataset
import numpy as np

# Chargement du dataset de génération de texte du projet Gutenberg
dataset_gutenberg = load_dataset("gutenberg")

# Choisissez un livre du corpus du projet Gutenberg (par exemple, "War and Peace" de Léon Tolstoï)
book_id = 2600
text = dataset_gutenberg['train'][book_id]['text'].replace('\n', ' ')

# Prétraitement des données pour la génération de texte
chars_text = sorted(list(set(text)))
char_to_idx_text = {char: idx for idx, char in enumerate(chars_text)}
idx_to_char_text = {idx: char for idx, char in enumerate(chars_text)}

max_len_text = 100  # Longueur maximale de la séquence
step_text = 3  # Pas de déplacement lors de la création des séquences
sentences_text = []
next_chars_text = []

for i in range(0, len(text) - max_len_text, step_text):
    sentences_text.append(text[i:i + max_len_text])
    next_chars_text.append(text[i + max_len_text])

x_text = np.zeros((len(sentences_text), max_len_text, len(chars_text)), dtype=np.bool)
y_text = np.zeros((len(sentences_text), len(chars_text)), dtype=np.bool)

for i, sentence in enumerate(sentences_text):
    for t, char in enumerate(sentence):
        x_text[i, t, char_to_idx_text[char]] = 1
    y_text[i, char_to_idx_text[next_chars_text[i]]] = 1


# Chargement du dataset de discussion Persona-Chat de ConvAI2
dataset_persona_chat = load_dataset("convaai/convai2")

# Prétraitement des données pour la discussion
dialogues = dataset_persona_chat['train']['dialog']

max_len_dialogue = 20  # Longueur maximale du dialogue
step_dialogue = 2  # Pas de déplacement lors de la création des dialogues
dialogue_sequences = []
next_lines = []

for dialogue in range(0, len(dialogues) - max_len_dialogue, step_dialogue):
    dialogue_sequences.append(dialogues[dialogue:dialogue + max_len_dialogue])
    next_lines.append(dialogues[dialogue + max_len_dialogue])

x_discussion = []
y_discussion = []

for i, dialogue_sequence in enumerate(dialogue_sequences):
    x_discussion.append(dialogue_sequence)
    y_discussion.append(next_lines[i])

# Créez une couche d'embedding partagée
embedding_layer = Embedding(max(len(chars_text), len(dialogues)), 50, input_length=max_len_text)

# Créez la branche de génération de texte
input_text = Input(shape=(max_len_text,))
embedded_text = embedding_layer(input_text)
lstm_text = LSTM(128)(embedded_text)
output_text = Dense(len(chars_text), activation='softmax')(lstm_text)

# Créez la branche de discussion
input_discussion = Input(shape=(max_len_dialogue,))
embedded_discussion = embedding_layer(input_discussion)
lstm_discussion = LSTM(128)(embedded_discussion)
output_discussion = Dense(len(dialogues), activation='softmax')(lstm_discussion)

# Créez le modèle complet
model = Model(inputs=[input_text, input_discussion], outputs=[output_text, output_discussion])

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Entraînez le modèle avec les deux tâches
model.fit([x_text, x_discussion], [y_text, y_discussion], epochs=10, batch_size=128)

# Enregistrez le modèle
model.save('kaka.h5')