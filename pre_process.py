"""
Code for data pre-processing.
The file reads the entire "corpus" folder and creates the bot training dataset.
The dataset is saved to the file, as is a dictionary that links the preprocessed output
to the clean output so that after prediction the bot can return the clean output.
"""
import os
import yaml
import nltk
import string
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Some of these words are considered stopwords and should therefore be removed,
# but it is better to take them into account in order to ensure a better conversation
no_sw = {"stai", "come", "tu", 'sei', 'fai', 'non', 'una', 'la'}


def preprocess_text(text):
    """
    Preprocess text for training or use in chatbots:
    - Convert to lowercase
    - Tokenize and remove punctuation
    - Remove custom stopwords
    - Lemmatize tokens

    Parameters
    ----------
    text : string
        message to preprocess
   
    Returns
    -------
    tokens : sting
        tokens of initial text
    """
    # Convert to lowercase
    text = text.lower()

    # Tokenize the text
    tokens = nltk.word_tokenize(text)

    # Remove punctuation and special characters
    tokens = [token for token in tokens if token not in string.punctuation]

    # Remove custom stopwords
    custom_stopwords = set(stopwords.words('italian')) - no_sw  # Personalizza la lista
    tokens = [token for token in tokens if token not in custom_stopwords  or token in no_sw]

    # Lemmatize tokens
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    # Rebuild the text
    return " ".join(tokens)


def load_corpus(dir):
    """
    Carica e preprocessa tutti i file .yml che costituiscono il corpus.

    Parameters
    ----------
    dir : path
        path to the directory containing all .yml files
    
    Return
    ------
    Conversations : list
        list of all conversations
    """
    conversations = []
    for root, _, files in os.walk(dir):     # Scan all subfolders
        for filename in files:              # Loop over all files
            if filename.endswith('.yml'):   # Select only *.yml file

                # Open the file
                filepath = os.path.join(root, filename)
                with open(filepath, 'r', encoding='utf-8') as file:
                    try:
                        # Read the data
                        data = yaml.safe_load(file)

                        # Select the "conversations" keyword
                        for conv in data.get('conversations', []):
                            # Read the questions and the answers from the conversation
                            input_text    = conv[0]
                            response_text = conv[1]
                            conversations.append((input_text, response_text))

                    except yaml.YAMLError as e:
                        print(f"Error in {filepath}: {e}")

    return conversations

# Test del preprocessing
if __name__ == "__main__":

    # Scarica risorse NLTK (esegui solo la prima volta)
    if 1:
        nltk.download('punkt_tab')
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('stopwords')

    # Test di esempio
    test_sentences = [
        "Ciao, come stai?", "Cosa ti piace fare?",
        "Tutto bene grazie, tu come stai?", "che noia",
        "che fai?", "come stai?", "Non sto bene",
        "Ascolti musica", "come ti chiami?", "Allora",
        "differenza fra una e la storia", "un'altra"
    ]


    for sentence in test_sentences:
        preprocessed = preprocess_text(sentence)
        print(f"Original:     {sentence}")
        print(f"Preprocessed: {preprocessed}")
    
    # Root path of the corpus
    corpus_dir = "corpus"
    
    # Load and preprocess all conversations
    dataset = load_corpus(corpus_dir)

    # Check the number of conversations loaded
    print(f"Total conversations loaded: {len(dataset)}")

    # Divide dataset into questions and answers
    X_train_p = [preprocess_text(item[0]) for item in dataset]
    y_train   = [item[1]                  for item in dataset]
    y_train_p = [preprocess_text(item[1]) for item in dataset]

    # Create a map to keep the answers connected
    correspondence = {yp : y  for yp, y in zip(y_train_p, y_train)}

    # Save data
    np.savez('corpus/train_dataset', X=X_train_p, y=y_train_p)
    np.save('corpus/map', correspondence)

