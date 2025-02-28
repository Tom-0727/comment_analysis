import yaml
import argparse
import pandas as pd

from tqdm import tqdm
from modules.agent import CommentAnalysisAgent
from modules.evaluator import metric_calculate



def read_csv(testset_path, version='default'):
    # 读取测试集
    df = pd.read_csv(testset_path, sep='\t')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.drop(columns=['version', 'v1', 'v1_4o', 'v1_4o_mini'], inplace=True)
    df[version] = ''
    print(df.columns)
    return df


def evaluate(robot, testset, testset_path, version):

    length = len(testset)
    for i in tqdm(range(length)):
        comment = testset.iloc[i]['内容']
        if not isinstance(comment, str):
            continue

        response = robot.comment_analyze(comment)
        testset.loc[i, version] = response
    
    testset.to_csv(testset_path, index=False, sep='\t')

    return testset



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key_yaml_path", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--version", type=str, required=True)
    parser.add_argument("--mode", type=str, required=True)
    parser.add_argument("--testset_path", type=str, required=True)
    args = parser.parse_args()

    version = args.version
    testset_path = args.testset_path
    testset = read_csv(testset_path, version)

    if args.mode == 'run_and_eval':
        with open(args.api_key_yaml_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        my_key = data['openai']['key']
        robot = CommentAnalysisAgent(openai_key=my_key, model=args.model)  # gpt-4o-2024-08-06  gpt-4o-mini-2024-07-18

        testset = evaluate(robot, testset, testset_path, version)

    print('version: ', version)
    precision, recall = metric_calculate(testset, version)