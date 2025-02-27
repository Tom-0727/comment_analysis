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

'''
O1: 2025行政桌发现 3-4个亿 机会发现；亚马逊，真实销量1.5-2亿
O2: 升降桌2025年全球年销量 > 50万/台。找到路径&实现闭环
O3: Tribesign 分析机会识别 > 1亿，运营利润
O4: 独立站行政中端商业机会（品牌机会）

'''
'''感觉-画面-认知-做到-悟到'''
'''
方向到OKR（目标怎么清洗）
现状 - 目标
 成功要素｜主要阻碍 KR：核心问题 - 关键结果
用户价值 - 新体验 - 旧体验 - 成本
这些怎么找？

交付的是 标准&验收方案

周 跟进 - 进度
月 检视（市场，或者相对宏观的变动） - 策略
季 通晒（阶段性，实现了为什么，没实现为什么） - 结算
颗粒度 - 节奏 同频
'''

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

