import re
import yaml
import argparse
import pandas as pd

from tqdm import tqdm
from modules.agent import TranslationAgent



def read_csv(testset_path, version='default'):
    # 读取测试集
    df = pd.read_csv(testset_path, sep='\t')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    #df.drop(columns=['version', 'v1', 'v1_4o', 'v1_4o_mini'], inplace=True)
    
    df[version] = ''
    print(df.columns)
    return df


def translate(robot, testset, testset_path, version):

    length = len(testset)
    for i in tqdm(range(length)):
        comment = testset.iloc[i]['内容']
        if not isinstance(comment, str):
            continue

        response = robot.comment_analyze(comment)
        testset.loc[i, version] = response
    
    testset.to_csv(testset_path, index=False, sep='\t')

    return testset


def one_shot(robot):
    # with open("./buffer/translate_samples.txt", "r", encoding="utf-8") as file:
    #     text = file.read()
    
    # # parse
    # comment_pattern = r"comment\s*=\s*'''(.*?)'''"
    # comments = re.findall(comment_pattern, text, re.DOTALL)
    # response_pattern = r"response\s*=\s*'''(.*?)'''"
    # responses = re.findall(response_pattern, text, re.DOTALL)

    # translated_comment = []
    # translated_response = []
    # ans = ""
    # for i in range(len(comments)):
    #     comment = comments[i]
    #     response = responses[i]
    #     tc = robot.translate(comment)
    #     tr = robot.translate(response)
    #     translated_comment.append(tc)
    #     translated_response.append(tr)
    #     ans += f"----------------------------\n#{i+1}\ncomment = '''{comment}'''\n评论 = '''{tc}'''\nresponse = '''{response}'''\n分析 = '''{tr}'''\n\n"

    # with open("./buffer/translate_results.txt", "w", encoding="utf-8") as file:
    #     file.write(ans)
    comment = "The desk is beautiful looking although it is a little bit deceiving. Kinda wish I ordered a different one. I agree with other reviews that the set up takes forever and there are SO MANY PARTS! I am petite/5'3 and bought a computer chair that is equivalent to the height of a dining room table chair, nothing special and I have a hard time putting my legs under so I do wish it was taller. Also, the drawers aren't as deep as the desk is so that's a bummer they are so small. It's just big enough to fit a 8 x 10 sheet of paper. Overall looks beautiful but functionality can be improved."
    print(robot.translate(comment))
    




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
    #testset = read_csv(testset_path, version)

    
    with open(args.api_key_yaml_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    my_key = data['openai']['key']
    robot = TranslationAgent(openai_key=my_key, model=args.model)  # gpt-4o-2024-08-06  gpt-4o-mini-2024-07-18

    if args.mode == "one-shot":
        one_shot(robot)
    #testset = evaluate(robot, testset, testset_path, version)

    