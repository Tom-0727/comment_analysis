import os
import re
import yaml
import time
import argparse
import pandas as pd
from tqdm import tqdm

from modules.utils import csv_enter, amz_xlsx_enter
from modules.agent import OpenAICommentAnalysisAgent, API2DCommentAnalysisAgent, QwenCommentAnalysisAgent



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


def infer(comment_analyzor, dataframe, save_path, to_translate, to_inspect):
    dataframe['英文分析'] = ''
    dataframe['好差评结果'] = ''
    dataframe['中文评论'] = ''
    dataframe['审查结果'] = ''
    df = dataframe

    if not os.path.exists(save_path):
        dataframe.iloc[:0].to_csv(save_path, sep='\t', index=False)
    df_to_save = pd.read_csv(save_path, sep='\t')
    start_index = len(df_to_save)

    length = len(dataframe)
    assert length > start_index, 'The save file length is more than dataframe to do comment analysis'

    for i in tqdm(range(start_index, length)):
        comment = df.iloc[i]['评论内容']
        if not isinstance(comment, str):
            continue
        
        row = dataframe.iloc[[i]].copy()

        # 分析评论
        analysis = comment_analyzor.comment_analyze(comment)
        row.loc[i, '英文分析'] = analysis
        #print(f"分析结果: {analysis}")

        # 提取结果
        extracted_output = extract_output(analysis)
        extracted_output = ''.join(extracted_output)
        extracted_output = eval(extracted_output)
        extracted_output = remove_duplicate_values(extracted_output)
        row.loc[i, '好差评结果'] = str(extracted_output)
        #print(f"提取结果: {extracted_output}")

        # 翻译评论
        if to_translate:
            translated_comment = comment_analyzor.translate(comment)
            row.loc[i, '中文评论'] = translated_comment
        # # print(f"原: {comment}\n翻译评论: {translated_comment}")

        # # 反审查
        if to_inspect:
            check_result = comment_analyzor.inspect(comment, str(extracted_output))
            row.loc[i, '审查结果'] = check_result

        # 保存结果
        row.to_csv(save_path, sep='\t', mode='a', header=False, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key_yaml_path", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--arch", type=str, required=True)
    parser.add_argument("--criteria", type=str, required=True)
    parser.add_argument("--template", type=str, required=True)
    parser.add_argument("--read_mode", type=str, required=True)
    parser.add_argument("--file_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--to_translate", type=str, default='False')
    parser.add_argument("--to_inspect", type=str, default='False')
    args = parser.parse_args()

    with open(args.api_key_yaml_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    my_key = data[args.arch]['key']
    
    if args.read_mode == 'csv':
        dataframe = csv_enter(args.file_path)
    elif args.read_mode == 'amz_xlsx':
        dataframe = amz_xlsx_enter(args.file_path)

    if args.arch == 'openai':
        comment_analyzor = OpenAICommentAnalysisAgent(openai_key=my_key, criteria=args.criteria, model=args.model, template=args.template)
    elif args.arch == 'api2d':
        comment_analyzor = API2DCommentAnalysisAgent(forward_key=my_key, criteria=args.criteria, model=args.model, template=args.template)
    elif args.arch == 'qwen':
        comment_analyzor = QwenCommentAnalysisAgent(key=my_key, criteria=args.criteria, model=args.model, template=args.template)

    yes_range = ['True', 'true', '1', 'yes', 'Yes']
    to_translate = args.to_translate in yes_range
    to_inspect = args.to_inspect in yes_range


    infer(comment_analyzor=comment_analyzor, dataframe=dataframe, save_path=args.output_path, to_translate=to_translate, to_inspect=to_inspect)

