import os
import re
import yaml
import argparse
import pandas as pd
from tqdm import tqdm

from modules.agent import OpenAICommentAnalysisAgent



def read_file(file_path):
    df = pd.read_csv(file_path, sep='\t')
    print(f"读取文件: {file_path}")
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


def openai_infer(comment_analyzor, dataframe, save_path):
    df = dataframe

    length = len(dataframe) 
    for i in tqdm(range(length)):
        comment = df.iloc[i]['内容']
        if not isinstance(comment, str):
            continue
        df.loc[i, '英文评论'] = comment

        # 分析评论
        analysis = comment_analyzor.comment_analyze(comment)
        df.loc[i, '英文分析'] = analysis
        #print(f"分析结果: {analysis}")

        # 提取结果
        extracted_output = extract_output(analysis)
        df.loc[i, '分析结果'] = ''.join(extracted_output)
        #print(f"提取结果: {extracted_output}")

        # 翻译评论
        # translated_comment = comment_analyzor.translate(comment)
        # df.loc[i, '中文评论'] = translated_comment
        #print(f"原: {comment}\n翻译评论: {translated_comment}")

        # 翻译分析
        # translated_analysis = comment_analyzor.translate(analysis)
        # df.loc[i, '中文分析'] = translated_analysis
        #print(f"翻译分析: {translated_analysis}")

        # 反审查
        break

    df.to_csv(save_path, sep='\t', index=False)


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
        openai_infer(comment_analyzor=comment_analyzor, dataframe=dataframe, save_path=args.output_path)

