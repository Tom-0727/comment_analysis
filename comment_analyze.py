import os
import yaml
import argparse
import pandas as pd

from tqdm import tqdm
from modules.agent import CommentAnalysisAgent



def read_xlsx(folder_path):
    dfs = []
    files = []
    files_lis = os.listdir(folder_path)
    have_done = []

    for file in files_lis:
        if file.endswith("_done.xlsx"):
                have_done.append(file.replace("_done.xlsx", ''))

    for file in files_lis:
        if file.endswith(".xlsx"):
            if file.endswith("_done.xlsx"):
                have_done.append(file.replace("_done.xlsx", ''))
                continue
            
            if file.replace('.xlsx', '') in have_done:
                continue

            file_path = os.path.join(folder_path, file)
            df = pd.read_excel(file_path, engine="openpyxl")  # 读取文件
            print(f"读取文件: {file}")

            # ----
            df['origin_outcome'] = ''

            dfs.append(df)
            files.append(file_path)
    return dfs, files


def save_xlsx(df):
    pass


def infer(robot, dfs, files):

    for j in range(len(dfs)):
        df = dfs[j]
        file = files[j]
        length = len(df)

        for i in tqdm(range(length)):
            comment = df.iloc[i]['内容']
            if not isinstance(comment, str):
                continue
            output = robot.comment_analyze(comment)
            df.loc[i, 'origin_outcome'] = output
            try:
                output = eval(output)
                # 遍历 output，将数据存入 DataFrame
                for key, value in output.items():
                    if key not in df.columns:  # 如果 DataFrame 里没有这个列，就新建
                        df[key] = ''  # 先创建列，填充 NaN
                    df.at[i, key] = value  # 填充数据
            except:
                pass
        df.to_excel(file.replace('.xlsx', '_done.xlsx'), index=False, engine="openpyxl")
            


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="一个简单的 argparse 示例")
    parser.add_argument("--folder_path", type=str, required=True)
    args = parser.parse_args()

    dfs, files = read_xlsx(args.folder_path)
    with open("openai_keys.yaml", "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    my_key = data['tom']['key']
    robot = CommentAnalysisAgent(openai_key=my_key, model="gpt-4o-mini-2024-07-18")  # gpt-4o-2024-08-06  gpt-4o-mini-2024-07-18

    infer(robot, dfs, files)

