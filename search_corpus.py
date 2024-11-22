"""
Code to quickly find strings in the bot corpus,
so that it is easy to make any replacements, corrections or additions.
"""
import os
import yaml

def find(folder_path, search_string):
    '''
    Searches for a string in all .yml files in a folder
    specifies and returns the files and lines where it appears.

    Parameters
    ----------
    folder_path : str
        The path to the folder containing the .yml files.
    search_string : str
        The string to search for.

    Returns
    -------
    results : list of tuples
        A list of tuples, each containing:
        - The name of the file
        - The line (line number) where the string was found
    '''
    results = []
    
    # Scan all files in the folder
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.yml'):
                file_path = os.path.join(root, file)
                
                try:
                    # Open the file and read the lines
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    # Search for the string in each line
                    for line_number, line in enumerate(lines, start=1):
                        if search_string in line:
                            results.append((file, line_number))
                
                except yaml.YAMLError as e:
                    print(f"Errore nel parsing del file {file_path}: {e}")
                except Exception as e:
                    print(f"Errore nel leggere il file {file_path}: {e}")
    
    return results


if __name__ == "__main__":

    folder_path = "corpus"
    search_string = "cucuzze"
    matches = find(folder_path, search_string)

    if matches:
        print("Stringa trovata in:")
        for file, line in matches:
            print(f" {file}, linea {line}")
    else:
        print("Stringa non trovata.")
