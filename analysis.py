import ast
import json
import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta



def cal_importance(df):
    # 使用defaultdict来简化计数
    value_counts = defaultdict(int)
    total_comments = 0
    
    # 遍历'分析结果'列
    for analysis in df['好差评结果']:
        # 将字符串转换为字典，使用json.loads
        analysis = str(analysis)
        try:
            # 将单引号替换为双引号以符合JSON格式
            analysis_dict = json.loads(analysis.replace("'", "\""))
        except json.JSONDecodeError:
            # 忽略无法解析的JSON字符串
            print('-')
            continue
        
        # 增加评论计数
        total_comments += 1
        
        # 提取值并更新计数
        for value in analysis_dict.values():
            value_counts[value] += 1

    # 计算频率
    if total_comments > 0:
        frequency = {k: round(v / total_comments, 4) for k, v in value_counts.items()}
    else:
        frequency = {}
    
    return frequency


def cal_satisfaction(df):
    # 初始化满意度的字典
    satisfaction = {}
    for i in range(len(df)):
        a = df.iloc[i]['好差评结果']
        a = str(a)
        try:
            # 将单引号替换为双引号以符合JSON格式
            analysis_result = json.loads(a.replace("'", "\""))
        except json.JSONDecodeError:
            # 忽略无法解析的JSON字符串
            print('-')
            continue
        score = float(df.iloc[i]['评分'])
        
        for key in analysis_result.keys():
            value = analysis_result[key]
            key = key.lower()
            
            if key.startswith('pos'):
                if value in satisfaction:
                    satisfaction[value].append(score)
                else:
                    satisfaction[value] = [score]
            elif key.startswith('neg'):
                if value in satisfaction:
                    satisfaction[value].append(score - 6)
                else:
                    satisfaction[value] = [score - 6]
    
    # 计算满意度和分歧度
    satisfaction_result = {}
    diversity_result = {}
    # print(satisfaction)
    
    for key, scores in satisfaction.items():
        mean_score = round(float(np.mean(scores)), 4)
        if len(scores) > 1:
            std_dev = round(float(np.std(scores, ddof=1)), 4)
        else:
            std_dev = 0
        satisfaction_result[key] = mean_score
        diversity_result[key] = std_dev
    
    return satisfaction_result, diversity_result



if __name__ == '__main__':
    file_path = './buffer/standing_samples2.csv'
    output_path = './buffer/tmp_ana.xlsx'
    criteria_path = './docs/standing_desk_criteria.csv'
    
    now = datetime.now()
    half_year_ago = now - timedelta(days=365/2)
    half_year_date = half_year_ago.strftime('%Y-%m-%d')
    one_year_ago = now - timedelta(days=365)
    one_year_date = one_year_ago.strftime('%Y-%m-%d')
    two_years_ago = now - timedelta(days=365*2)
    two_years_date = two_years_ago.strftime('%Y-%m-%d')
    time_stamps = {
        '近半年数据分析': half_year_date,
        '近一年数据分析': one_year_date,
        '近两年数据分析': two_years_date
    }
    # print(two_years_date)

    df = pd.read_csv(file_path, sep=None, engine='python')
    # df = pd.read_excel(file_path, sheet_name='升降桌测试')
    # print(df.columns)
    df['评论时间'] = pd.to_datetime(df['评论时间'])
    df = df.dropna(subset=['好差评结果'])

    criteria_df = pd.read_csv(criteria_path, sep=None, engine='python')
    e2c_dict = dict(zip(criteria_df['体验点二级分类英文'].apply(str.lower), criteria_df['体验点二级分类']))

    df['好评'] = ''
    df['差评'] = ''
    df['中评'] = ''
    for i in range(len(df)):
        ext_pts = df.iloc[i]['好差评结果']
        try:
            ext_pts = eval(ext_pts)
        except:
            print(ext_pts)
            continue
        pos = []
        neg = []
        neu = []
        for k in ext_pts.keys():
            if 'Pos' in k or 'pos' in k:
                ch = ext_pts[k]
                ch = ch.strip().lower()
                ch = e2c_dict[ch]
                pos.append(ch)
            elif 'Neg' in k or 'neg' in k:
                ch = ext_pts[k]
                ch = ch.strip().lower()
                ch = e2c_dict[ch]
                neg.append(ch)
            elif 'Neu' in k or 'neu' in k:
                ch = ext_pts[k]
                ch = ch.strip().lower()
                ch = e2c_dict[ch]
                neu.append(ch)
        df.loc[i, '好评'] = str(pos)
        df.loc[i, '差评'] = str(neg)
        df.loc[i, '中评'] = str(neu)

    with pd.ExcelWriter(output_path) as writer:
        # 将每个DataFrame写入不同的工作表
        df.to_excel(writer, sheet_name='好差评打标', index=False)
        criteria_df.to_excel(writer, sheet_name='体验点分类标准', index=False)
        

        for stamp in time_stamps.keys():
            # 使用条件筛选来选择大于cutoff_date的样本
            filtered_df = df[df['评论时间'] > time_stamps[stamp]]

            importance = cal_importance(filtered_df)
            satisfaction, diversity = cal_satisfaction(filtered_df)

            data = {
                '重要度': importance,
                '满意度': satisfaction,
                '分歧度': diversity
            }

            analysis_df = pd.DataFrame(data)
            analysis_df.reset_index(inplace=True)
            analysis_df.rename(columns={'index': '体验点'}, inplace=True)

            analysis_df['质量改进优先度'] = analysis_df['重要度'] * (6 - analysis_df['满意度'])

            for i in range(len(analysis_df)):
                analysis_df.loc[i, '体验点'] = e2c_dict[analysis_df.iloc[i]['体验点'].lower()]
            analysis_df['评论条数'] = ''
            analysis_df.loc[0, '评论条数'] = len(filtered_df)
            analysis_df.to_excel(writer, sheet_name=stamp, index=False)
        
        

    
        



