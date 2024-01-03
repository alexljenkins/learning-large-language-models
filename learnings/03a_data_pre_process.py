"""
Generic transformation of the text files into a
pandas dataframe and sqlite database
for further analysis.
Creating a single line of dialogue as a df row - with additional metadata.
"""
import glob
import pandas as pd
import os
import sqlite3


def get_txt_files(folder_path):
    filepaths = glob.glob(f"{folder_path}/*.txt")
    filepaths.sort()
    return filepaths

def txt_to_df(folder_path):
    data = []
    # Glob over all text files in the folder
    for file_path in get_txt_files(folder_path):
        with open(file_path, 'r') as file:
            filename = os.path.splitext(os.path.basename(file_path))[0]

            for line_number, line in enumerate(file, start=1):
                processed_line = process_line(line)
                if processed_line:
                    processed_line += [filename, line_number]
                    data.append(processed_line)
    
    return pd.DataFrame(data, columns=["Character", "Text", "Episode", "LineNumber"])


def process_line(line):
    line = line.strip()
    if not line:
        return None

    # character is speaking
    if ":" in line:
        character, text = line.split(":", 1)
        character = character.strip()
    else:
        # some errors in here when multi-line talking with or without directions
        character = "DIRECTION"
        text = line
    # this will put tripple quotes around the text to avoid the need for escape keys
    return [character, '"' + text.strip(' "') + '"']


def save_df_to_sqlite(df, db_name):
    conn = sqlite3.connect(f'{db_name}.db')
    df.to_sql(name='script', con=conn, if_exists='replace', index=False)
    conn.close()

folder_path = "datasets/rick_data/txt/"
df = txt_to_df(folder_path)
save_df_to_sqlite(df, "datasets/rick_data/full_script")
df.to_csv("datasets/rick_data/full_script.csv", index=False)
