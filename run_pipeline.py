import os
import re
import yaml
import time
import argparse
import pandas as pd
from tqdm import tqdm

from modules.agent import OpenAICommentAnalysisAgent, API2DCommentAnalysisAgent



def read_file(file_path):
    # 使用 pandas 读取所有工作表
    print(f"读取文件: {file_path}")
    df = pd.read_csv(file_path)

    df['内容'] = df['productComments']
    
    print(df.columns)
    df['英文评论'] = ''
    df['中文评论'] = ''
    df['英文分析'] = ''
    df['中文分析'] = ''
    df['分析结果'] = ''
    df['反审查结果'] = ''
    return df


def extract_output(text):
    pattern = r'\{.*?\}'
    matches = re.findall(pattern, text, re.DOTALL)

    matches = [match.replace('\n', '') for match in matches]
    return matches


def remove_duplicate_values(input_dict):
    seen_values = set()  # 用于存储已经出现过的值
    output_dict = {}  # 用于存储最终的结果

    for key, value in input_dict.items():
        if value not in seen_values:
            seen_values.add(value)
            output_dict[key] = value

    return output_dict


def infer(comment_analyzor, dataframe, save_path):
    df = dataframe

    if not os.path.exists(save_path):
        dataframe.iloc[:0].to_csv(save_path, sep='\t', index=False)
    df_to_save = pd.read_csv(save_path, sep='\t')
    start_index = len(df_to_save)

    length = len(dataframe)
    assert length > start_index, 'The save file length is more than dataframe to do comment analysis'

    for i in tqdm(range(start_index, length)):
        comment = df.iloc[i]['内容']
        if not isinstance(comment, str):
            continue
        
        row = dataframe.iloc[[i]].copy()
        row.loc[i, '英文评论'] = comment

        # 分析评论
        analysis = comment_analyzor.comment_analyze(comment)
        row.loc[i, '英文分析'] = analysis
        #print(f"分析结果: {analysis}")

        # 提取结果
        extracted_output = extract_output(analysis)
        extracted_output = ''.join(extracted_output)
        extracted_output = eval(extracted_output)
        extracted_output = remove_duplicate_values(extracted_output)
        row.loc[i, '分析结果'] = str(extracted_output)
        #print(f"提取结果: {extracted_output}")

        # 翻译评论
        # translated_comment = comment_analyzor.translate(comment)
        # row.loc[i, '中文评论'] = translated_comment
        #print(f"原: {comment}\n翻译评论: {translated_comment}")

        # 翻译分析
        # translated_analysis = comment_analyzor.translate(analysis)
        # row.loc[i, '中文分析'] = translated_analysis
        #print(f"翻译分析: {translated_analysis}")

        # 反审查
        row.to_csv(save_path, sep='\t', mode='a', header=False, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key_yaml_path", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--arch", type=str, required=True)
    parser.add_argument("--file_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    args = parser.parse_args()

    with open(args.api_key_yaml_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    my_key = data[args.arch]['key']
    
    dataframe = read_file(args.file_path)

    if args.arch == 'openai':
        comment_analyzor = OpenAICommentAnalysisAgent(openai_key=my_key, model=args.model)
        
    elif args.arch == 'api2d':
        comment_analyzor = API2DCommentAnalysisAgent(forward_key=my_key, model=args.model)

    infer(comment_analyzor=comment_analyzor, dataframe=dataframe, save_path=args.output_path)

