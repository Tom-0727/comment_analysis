import os
import re
import yaml
import time
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.cluster import KMeans
from FlagEmbedding import BGEM3FlagModel
from sklearn.feature_extraction.text import TfidfVectorizer


from modules.utils import csv_enter, xlsx_enter
from modules.agent import OpenAICommentAnalysisAgent, API2DCommentAnalysisAgent



def extract_output(text):
    pattern = r'\{.*?\}'
    matches = re.findall(pattern, text, re.DOTALL)

    matches = [match.replace('\n', '') for match in matches]
    return matches


def point_extract(comment_analyzor, dataframe, save_path):
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

        points = comment_analyzor.points_extract(comment)
        row.loc[i, '体验点分析'] = str(points)
        # print(f"体验点分析: {points}")

        extract_points = extract_output(points)
        row.loc[i, '体验点'] = ''.join(extract_points)
        # print(extract_points)

        row.to_csv(save_path, sep='\t', mode='a', header=False, index=False)


def clustering(file_path, save_path):
    df = pd.read_csv(file_path, sep=None, engine='python')

    exp_dict = df['体验点'].tolist()  # 删除空值并转为列表
    exp_points = []
    exp_desc = []
    for i in range(len(exp_dict)):
        exp = eval(exp_dict[i])
        for point, des in exp.items():
            exp_desc.append(des)
            exp_points.append(point)

    model = BGEM3FlagModel('/home/tom/codes/models/bge-m3',  
                       use_fp16=True) # Setting use_fp16 to True speeds up computation with a slight performance degradation
    embeddings = model.encode(exp_desc, batch_size=12, max_length=1024)['dense_vecs']

    num_clusters = min(100, len(exp_desc) // 2)  # 设置聚类数目，最多100个簇
    km = KMeans(n_clusters=num_clusters)
    km.fit(embeddings)

    df = pd.DataFrame(columns=['簇编号', '簇大小', '体验描述', '体验点', '主题词'])

    # 获取聚类标签并整理各簇文本
    clusters = km.labels_.tolist()
    cluster_texts = {i: [] for i in range(num_clusters)}
    cluster_points = {i: [] for i in range(num_clusters)}
    for idx, label in enumerate(clusters):
        cluster_texts[label].append(exp_desc[idx])
        cluster_points[label].append(exp_points[idx])

    # 将每个簇的搜索词合并为一个"文档"
    cluster_documents = []
    for cluster_id in range(num_clusters):
        # 将簇内所有搜索词用空格连接，保留原始短语结构
        cluster_doc = " ".join(cluster_texts[cluster_id])
        cluster_documents.append(cluster_doc)

    # 全局TF-IDF计算
    tfidf_vectorizer = TfidfVectorizer(
        #stop_words=stop_words,
        ngram_range=(1, 3),  # 保持短语检测能力
        max_df=0.85,         # 过滤出现在85%以上簇中的常见词
        min_df=1             # 允许出现1次的词（小簇需要）
    )
    tfidf_matrix = tfidf_vectorizer.fit_transform(cluster_documents)
    feature_names = tfidf_vectorizer.get_feature_names_out()

    # 为每个簇提取主题词
    for cluster_id in range(num_clusters):
        try:
            # 获取当前簇的TF-IDF向量
            cluster_tfidf = tfidf_matrix[cluster_id].toarray().flatten()
            
            # 按TF-IDF值降序排序
            sorted_indices = np.argsort(cluster_tfidf)[::-1]
            
            # 提取前10个候选词
            top_candidates = [feature_names[i] for i in sorted_indices[:10]]
            
            # 验证候选词是否实际存在于原始搜索词中
            valid_keywords = []
            original_terms = " ".join(cluster_texts[cluster_id]).lower()
            for candidate in top_candidates:
                # 检查候选词是否作为完整短语或单词存在于原始搜索词
                if any(
                    candidate.lower() == term.lower() or 
                    candidate.lower() in term.lower().split()
                    for term in cluster_texts[cluster_id]
                ):
                    valid_keywords.append(candidate)
            
            # 最终取前5个有效词
            final_keywords = valid_keywords[:5]

            # 将结果存入DataFrame
            df.loc[len(df), '簇编号'] = cluster_id
            df.loc[len(df)-1, '簇大小'] = len(cluster_texts[cluster_id])
            df.loc[len(df)-1, '体验描述'] = ", ".join(cluster_texts[cluster_id])
            df.loc[len(df)-1, '体验点'] = ", ".join(cluster_points[cluster_id])
            df.loc[len(df)-1, '主题词'] = ", ".join(final_keywords)
        except Exception as e:
            print(f"处理簇 {cluster_id} 时发生错误: {str(e)}")

    df.to_csv(save_path.replace('.csv', '_cluster.csv'), sep='\t', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key_yaml_path", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--arch", type=str, required=True)
    parser.add_argument("--template", type=str, required=True)
    parser.add_argument("--read_mode", type=str, required=True)
    parser.add_argument("--file_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    args = parser.parse_args()

    with open(args.api_key_yaml_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    my_key = data[args.arch]['key']
    
    if args.read_mode == 'csv':
        dataframe = csv_enter(args.file_path)
    elif args.read_mode == 'xlsx':
        dataframe = xlsx_enter(args.file_path)

    if args.arch == 'openai':
        comment_analyzor = OpenAICommentAnalysisAgent(openai_key=my_key, criteria='stations_executive_desk', model=args.model, template=args.template)
    elif args.arch == 'api2d':
        comment_analyzor = API2DCommentAnalysisAgent(forward_key=my_key, criteria='stations_executive_desk', model=args.model, template=args.template)

    point_extract(comment_analyzor=comment_analyzor, dataframe=dataframe, save_path=args.output_path)
    clustering(file_path=args.output_path, save_path=args.output_path)