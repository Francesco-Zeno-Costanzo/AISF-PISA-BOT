"""
Code to test the chabot by talking to it
"""
import os
import yaml
import joblib
import numpy as np

from pre_process import preprocess_text

# Path for saving conversations
conversation_file = "corpus/user_corpus.yml"
# Dictionary for unprocessed reply
response_map = np.load('corpus/map.npy', allow_pickle='TRUE').item()
# Load model
chatbot = joblib.load(r'/home/francesco/GitHub/AISF-PISA-BOT/mod.sav')


def chatbot_response(question):
    '''
    Function that gives the bot's response

    Parameters
    ----------
    question : string
        user's message
    
    Return
    ------
    response : string
        bot's response
    '''

    # Predici utilizzando il modello
    try:
        # Preprocess the user's question
        preprocessed_question = preprocess_text(question)
        # Predicts the answer
        response = chatbot.predict([preprocessed_question])
        # go back to the original answer as in the raw data
        response = response_map.get(response[0], "Non capisco.")
        # Save convesations
        save_conversation(question, str(response), conversation_file)

        return str(response)
    
    except Exception as e:
        print(f"Errore: {e}")
        return "Non ho capito. Puoi riformulare?"


def save_conversation(question, response, filename):
    '''
    Function to save the conversation in a .yml file in
    order to expand the corpus for subsequent training

    Parameters
    ----------
    question : string
        user's message
    response : string
        bot's response
    filename : string
        path of the .yml file
    '''
    conversation_data = {"conversations": [[question, response]]}
    
    # If the file already exists, upload and update
    if os.path.exists(filename):
        # Open file
        with open(filename, 'r', encoding='utf-8') as file:
            try:
                existing_data = yaml.safe_load(file) or {}
            except yaml.YAMLError as e:
                print(f"Error in loading YAML file: {e}")
                existing_data = {}
            
            # Append
            if 'conversations' in existing_data:
                existing_data['conversations'].extend(conversation_data['conversations'])
            # Create
            else:
                existing_data['conversations'] = conversation_data['conversations']
        conversation_data = existing_data

    # Write and save data
    with open(filename, 'w', encoding='utf-8') as file:
        yaml.dump(conversation_data, file, allow_unicode=True, default_flow_style=False)


if __name__ == "__main__":
    # Loop del chatbot
    while True:
        user_input = input("Tu: ")
        if user_input.lower() == "esci":
            print("Chatbot: Ciao!")
            break
        
        # Genera la risposta del chatbot
        bot_response = chatbot_response(user_input)
        print("Chatbot:", bot_response)