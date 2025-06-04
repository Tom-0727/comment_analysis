'''
文件说明：这里实现一些工具函数，包括合并excel文件、合并csv文件等。
'''
import os
import pandas as pd



def merge_analyzed_xlsx(folder_path, save_path):
    """
    Merge all analyzed xlsx files in the given folder path into a single DataFrame.
    
    Args:
        folder_path (str): The path to the folder containing the analyzed xlsx files.
    
    Returns:
        pd.DataFrame: A DataFrame containing the merged data from all xlsx files.
    """
    # Get all xlsx files in the folder
    xlsx_files = [f for f in os.listdir(folder_path) if f.endswith('_analyzed.xlsx')]
    
    # Initialize an empty list to store DataFrames
    df_list = []
    
    # Loop through each file and read it into a DataFrame
    for file in xlsx_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_excel(file_path, sheet_name='好差评打标', engine='openpyxl')
        df_list.append(df)
    
    # Concatenate all DataFrames into a single DataFrame
    merged_df = pd.concat(df_list, ignore_index=True)
    
    merged_df.to_csv(save_path, index=False, sep='\t')


if __name__ == "__main__":
    merge_analyzed_xlsx(folder_path='/Users/youniverse/Documents/Codes/comment_analysis/buffer/卧室扇listing/整装', save_path='./buffer/卧室扇listing/.csv')
