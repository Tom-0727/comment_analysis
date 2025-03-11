import requests
import re


# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-2171de8cfeb64f6a821f4a5ed73619b4"  # 替换为你的 DeepSeek API 密钥
DEEPSEEK_API_URL = "https://api.deepseek.com/beta/completions"  # 使用 Beta 版本的 API 端点
DEEPSEEK_MODEL = "deepseek-chat"  # 替换为 DeepSeek 的有效模型名称

# 示例评论数据
reviews = [
    "Instructions were not clear many pieces. Hard to put together"
]

# 生成具体标签的函数
def extract_detailed_labels(text):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = (
        f"Analyze the following review about a desk and generate multiple detailed and specific labels. "
        f"Each label should focus on a different aspect of the review, the label should be formal and descriptive, and it should reflect the key aspects mentioned in the review,such as 'stability', 'installation time', 'aesthetics', 'price', 'material quality', or 'customer service'. "
        f"Generate at least 2-3 labels per review, ensuring they are formal, descriptive, and standardized. "
        f"Each label must be a noun or noun phrase of 1-3 words only. "
        f"Any mention of stability-related issues, such as 'leg stability', 'desk stability', or 'wobble issue', should be labeled as 'stability'. "
        f"Any mention of instructions, should be labeled as 'manual clarity' "
        f"Standardize similar concepts into a single representative label. For example, 'dowel installation' and 'peg installation' should be labeled as 'installation difficulty'. "
        f"Do not generate complete sentences, verbs, adjectives, or other non-noun words. "
        f"Do not include conjunctions such as 'but', 'and', 'so', 'however', or similar words in the labels. "
        f"Here are some examples of valid labels: 'stability', 'aesthetics', 'number of assembly parts', 'surface damage', 'great value'. "
        f"Invalid examples: 'The desk is very sturdy', 'It took a long time to assemble', 'but the price is high'. "
        f"Separate the labels with commas:\n\n"
        f"Review: {text}\nLabels:"
    )
    data = {
        "model": DEEPSEEK_MODEL,  # 使用正确的模型名称
        "prompt": prompt,
        "max_tokens": 50,  # 增加生成的长度限制
        "temperature": 0.3  # 降低随机性，使输出更稳定
    }
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    response_data = response.json()
    
    # 打印 API 响应，用于调试
    #print("API Response:", response_data)
    
    # 检查是否有错误
    if "error" in response_data:
        print(f"Error: {response_data['error']['message']}")
        return ["unknown"]  # 如果出错，返回默认值
    
    # 根据实际 API 响应调整字段名
    if "choices" in response_data and len(response_data["choices"]) > 0:
        labels = response_data["choices"][0]["text"].strip().split("\n")[-1].replace("Labels:", "").strip()
        labels = [label.strip() for label in labels.split(",")]  # 将标签拆分为列表
    else:
        labels = ["unknown"]  # 如果字段名不匹配，返回默认值
    
    # 过滤掉不符合要求的标签
    labels = filter_labels(labels)
    return labels

# 过滤标签的函数
def filter_labels(labels):
    """
    过滤掉不符合要求的标签（如超过 3 个单词的标签或包含连词的标签）。
    """
    filtered_labels = []
    conjunctions = {"but", "and", "so", "however", "although", "though", "yet", "because", "since", "unless"}  # 连词列表
    
    for label in labels:
        # 检查标签的单词数量
        if len(label.split()) > 3:
            continue
        
        # 检查是否包含连词
        if any(conj in label.lower() for conj in conjunctions):
            continue
        
        # 使用正则表达式检查是否为名词短语（简单规则）
        if re.match(r"^[A-Za-z]+(?:\s[A-Za-z]+){0,2}$", label):
            filtered_labels.append(label)
    return filtered_labels

# 情感分析的函数
def analyze_sentiment(text):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": DEEPSEEK_MODEL,  # 使用正确的模型名称
        "prompt": (
            f"Analyze the sentiment of the following review. "
            #f"Consider both positive and negative aspects mentioned in the review. "
            #f"If the review is neutral or lacks clear sentiment, respond with 'NEUTRAL'. "
            f"Respond with only one word: 'POSITIVE' ,'NEUTRAL'or 'NEGATIVE':\n\n"
            f"Review: {text}\nSentiment:"
        ),
        "max_tokens": 10,  # 限制生成的长度
        "temperature": 0.0  # 控制生成结果的随机性
    }
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    response_data = response.json()
    
    # 打印 API 响应，用于调试
    #print("API Response:", response_data)
    
    # 检查是否有错误
    if "error" in response_data:
        print(f"Error: {response_data['error']['message']}")
        return "unknown"  # 如果出错，返回默认值
    
    # 根据实际 API 响应调整字段名
    if "choices" in response_data and len(response_data["choices"]) > 0:
        sentiment = response_data["choices"][0]["text"].strip().split("\n")[-1].replace("Sentiment:", "").strip()
    else:
        sentiment = "unknown"  # 如果字段名不匹配，返回默认值
    
    return sentiment

# 生成标签的函数
def generate_labels(reviews):
    all_labels = {}  # 存储所有评论的标签
    review_index = 1  # 评论编号
    
    for review in reviews:
        # 初始化当前评论的标签存储
        labels = {}
        pos_count, neg_count,neu_count = 1, 1 ,1 # 每条评论的标签从 1 开始计数
        
        # 提取具体标签
        detailed_labels = extract_detailed_labels(review)
        
        # 分析情感
        sentiment = analyze_sentiment(review)
        
        # 根据情感生成标签
        if sentiment == "POSITIVE":
            for label in detailed_labels:
                if label == "installation time":  # 安装时间默认为中性
                    labels[f"Neu{neu_count}"] = label
                    neu_count += 1
                else:
                    labels[f"Pos{pos_count}"] = label
                    pos_count += 1
        elif sentiment == "NEGATIVE":
            for label in detailed_labels:
                if label == "installation time":  # 安装时间默认为中性
                    labels[f"Neu{neu_count}"] = label
                    neu_count += 1
                else:
                    labels[f"Neg{neg_count}"] = label
                    neg_count += 1
        elif sentiment == "NEUTRAL":
            for label in detailed_labels:
                labels[f"Neu{neu_count}"] = label
                neu_count += 1
        elif sentiment == "MIXED":
            # 对于混合情感，根据关键词进一步分类
            for label in detailed_labels:
                if label == "installation time":  # 安装时间默认为中性
                    labels[f"Neu{neu_count}"] = label
                    neu_count += 1
                elif "hard" in label.lower() or "take long" in label.lower():  # 消极关键词
                    labels[f"Neg{neg_count}"] = label
                    neg_count += 1
                else:  # 默认归类为积极
                    labels[f"Pos{pos_count}"] = label
                    pos_count += 1
        
        # 将当前评论的标签添加到所有评论的标签中
        all_labels[f"Review {review_index}"] = labels
        review_index += 1
    
    return all_labels

# 生成标签
labels = generate_labels(reviews)

# 输出结果
print("生成的标签:")
for review, tags in labels.items():
    # 将标签拼接为一个字符串
    tags_str = ", ".join([f"{tag}: {value}" for tag, value in tags.items()])
    print(f"{review}: {tags_str}")