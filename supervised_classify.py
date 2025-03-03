import os
import re
import yaml
import argparse
import pandas as pd

from tqdm import tqdm
from modules.agent import CommentAnalysisAgent, CommentTranslateAgent



def read_xlsx(folder_path):
    dfs = []
    files = []
    files_lis = os.listdir(folder_path)

    for file in files_lis:
        if file.endswith(".xlsx"):
            file_path = os.path.join(folder_path, file)
            df = pd.read_excel(file_path, engine="openpyxl")  # 读取文件
            print(f"读取文件: {file}")

            # ----
            df['英文评论'] = ''
            df['中文评论'] = ''
            df['分析结果'] = ''
            df['中文分析'] = ''
            df['提取结果'] = ''

            dfs.append(df)
            files.append(file_path)
    return dfs, files


def save_csv(df, file_name, save_path):
    save_path = os.path.join(save_path, file_name)
    df.to_csv(save_path, index=False, sep='\t')


def extract_output(text):
    pattern = r'\{.*?\}'
    matches = re.findall(pattern, text, re.DOTALL)

    matches = [match.replace('\n', '') for match in matches]
    return matches


def infer(comment_analyzor, comment_translator, dfs, files, save_path):

    for j in range(len(dfs)):
        df = dfs[j]
        file = files[j]
        length = len(df)

        for i in tqdm(range(length)):
            comment = df.iloc[i]['内容']
            if not isinstance(comment, str):
                continue
            
            # 分析评论
            analysis = comment_analyzor.comment_analyze(comment)
            df.loc[i, '分析结果'] = analysis
            #print(f"分析结果: {analysis}")

            # 提取结果
            extracted_output = extract_output(analysis)
            df.loc[i, '提取结果'] = ''.join(extracted_output)
            #print(f"提取结果: {extracted_output}")

            # 翻译评论
            translated_comment = comment_translator.translate(comment)
            df.loc[i, '中文评论'] = translated_comment
            #print(f"原: {comment}\n翻译评论: {translated_comment}")

            # 翻译分析
            translated_analysis = comment_translator.translate(analysis)
            df.loc[i, '中文分析'] = translated_analysis
            #print(f"翻译分析: {translated_analysis}")
        
        save_csv(df=df, file_name=file.replace('.xlsx', '.csv'), save_path=save_path)
        
            


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key_yaml_path", type=str, required=True)
    parser.add_argument("--folder_path", type=str, required=True)
    parser.add_argument("--save_path", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)
    args = parser.parse_args()

    dfs, files = read_xlsx(args.folder_path)
    with open(args.api_key_yaml_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    my_key = data['openai']['key']
    comment_analyzor = CommentAnalysisAgent(openai_key=my_key, model=args.model)
    comment_translator = CommentTranslateAgent(openai_key=my_key, model=args.model)
    infer(comment_analyzor=comment_analyzor, comment_translator=comment_translator, dfs=dfs, files=files, save_path=args.save_path)

