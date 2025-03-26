import requests
import re
from concurrent.futures import ThreadPoolExecutor

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-2171de8cfeb64f6a821f4a5ed73619b4"  
DEEPSEEK_API_URL = "https://api.deepseek.com/beta/completions"  
DEEPSEEK_MODEL = "deepseek-chat" 

# 示例评论数据
reviews = [
    "I’ve assembled many desks and random pieces of furniture, and this is by far the worst.  Poor setup, poor “directions” if you can even call them that. And terrible manufacturing.  Majority of the predrilled holes don’t line up with what they’re supposed to.  If I hadn’t already started setting this up I would 100 percent return."
]

# 将评论拆分为单句
def split_into_sentences(text):
    """
    将评论拆分为单句。
    """
    sentences = re.split(r'(?<=[.!?]) +', text)  # 按句号、感叹号、问号拆分，试过用逗号拆分但是效果不好，还在想办法
    return sentences

# 生成具体标签、情感分析和情感原因的详细描述
def extract_labels_and_sentiment(text):
    """
    通过一次 API 调用生成标签、情感分析和情感原因的详细描述。
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = (
        f"Analyze the following sentence about a desk and generate multiple detailed and specific labels. "
        f"Each label should focus on a different aspect of the sentence, the label should be formal and descriptive, and it should reflect the key aspects mentioned in the sentence, such as 'stability', 'installation time', 'aesthetics', 'price', 'material quality', or 'customer service'. "
        f"Generate at least 1-2 labels per sentence, ensuring they are formal, descriptive, and standardized. "
        f"Each label must be a noun or noun phrase of 1-3 words only. "
        f"Any mention of stability-related issues, such as 'leg stability', 'desk stability', or 'wobble issue', should be labeled as 'stability'. "
        f"Any mention of time,such as 'hours','a long time',or 'days',should be labeled as 'installation time'."
        f"Any mention of instructions, should be labeled as 'manual clarity' "
        f"Standardize similar concepts into a single representative label. For example, 'dowel installation' and 'peg installation' should be labeled as 'installation difficulty'. "
        f"Do not generate complete sentences, verbs, adjectives, or other non-noun words. "
        f"Do not include conjunctions such as 'but', 'and', 'so', 'however', or similar words in the labels. "
        f"Here are some examples of valid labels: 'stability', 'aesthetics', 'number of assembly parts', 'surface damage', 'installation time'. "
        f"Invalid examples: 'The desk is very sturdy', 'It took a long time to assemble', 'but the price is high'. "
        f"After generating the labels, analyze the sentiment of the sentence. "
        f"Consider both positive and negative aspects mentioned in the sentence. "
        f"If the sentence contains both positive and negative aspects, respond with 'MIXED'. "
        f"If the sentence is mostly positive, respond with 'POSITIVE'. "
        f"If the sentence is mostly negative, respond with 'NEGATIVE'. "
        f"If the sentence is neutral or lacks clear sentiment, respond with 'NEUTRAL'. "
        f"Respond with only one word: 'POSITIVE', 'NEGATIVE', 'NEUTRAL'. "
        f"For each label, provide a brief description explaining why the sentiment is assigned. "
        f"Format the response as follows:\n\n"
        f"-Label1:label_name:{{Sentiment:'sentiment',Descriptions:Brief description of why this label has the assigned sentiment.}}\n"
        f"-Label2:label_name:{{Sentiment:'sentiment',Descriptions:Brief description of why this label has the assigned sentiment.}}\n"
        f"-Label3:label_name:{{Sentiment:'sentiment',Descriptions:Brief description of why this label has the assigned sentiment.}}\n\n"
        f"Sentence: {text}\n"
    )
    data = {
        "model": DEEPSEEK_MODEL,  
        "prompt": prompt,
        "max_tokens": 200,  
        "temperature": 0.3  
    }
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status() 
        response_data = response.json()
        
        # 根据实际 API 响应调整字段名
        if "choices" in response_data and len(response_data["choices"]) > 0:
            output = response_data["choices"][0]["text"].strip()
          
            
            # 提取标签、情感和描述
            labels = {}
            lines = output.split("\n")
            for line in lines:
                if line.startswith("-Label"):
                    parts = line.split(":", 2)
                    if len(parts) == 3:
                        label_name = parts[1].strip()
                        sentiment_desc = parts[2].strip().strip("{}")
                        sentiment = sentiment_desc.split(",")[0].split(":")[1].strip().strip("'")
                        description = sentiment_desc.split("Descriptions:")[1].strip()
                        sentiment_intensity = get_sentiment_intensity(sentiment, text)
                        labels[label_name] = {
                            "情感激烈程度": sentiment_intensity,  
                            "简要描述": description
                        }
            return labels
        else:
            return {"unknown": {"情感激烈程度": "unknown", "简要描述": "无描述"}}
    except requests.exceptions.RequestException as e:
        print(f"API 请求失败: {e}")
        return {"unknown": {"情感激烈程度": "unknown", "简要描述": "无描述"}}  # 如果出错，返回默认值

# 判断情感激烈程度
def get_sentiment_intensity(sentiment, text):
    """
    根据情感分类和文本内容判断情感激烈程度。
    """
    if sentiment == "POSITIVE":
        # 强烈正向词汇
        strong_positive_words = ["extremely", "fantastic", "excellent", "even","perfect", "amazing", "really", "pretty", "unparalleled", "flawless", "beyond expectations", "superb",'great', "top-notch"]
        if any(word in text for word in strong_positive_words):
            return "强烈正向"
        else:
            return "微弱正向"
    elif sentiment == "NEGATIVE":
        # 强烈负向词汇
        strong_negative_words = ["terrible", "extremely poor", "garbage","long", "even","really", "horrible", "utterly disappointing", "extremely", "unbearable", "absolutely", "completely", "frustrating"]
        if any(word in text for word in strong_negative_words):
            return "强烈负向"
        else:
            return "微弱负向"
            
    else:  # 中性
        return "中性"

# 过滤标签的函数
def filter_labels(labels):
    """
    过滤掉不符合要求的标签（如超过 3 个单词的标签或包含连词的标签）。
    """
    filtered_labels = []
    conjunctions = {"but", "and", "so", "however", "although", "though", "yet", "because", "since", "unless"}  # 连词列表
    
    for label in labels:
        if len(label.split()) > 3:
            continue
        

        if any(conj in label.lower() for conj in conjunctions):
            continue
        
        # 确保名词短语
        if re.match(r"^[A-Za-z]+(?:\s[A-Za-z]+){0,2}$", label):
            filtered_labels.append(label)
    return filtered_labels

# 生成标签的函数
def generate_labels(review):
    """
    处理单个评论并生成标签。
    """
  
    labels = {}
    sentences = split_into_sentences(review)
    
    # 逐句分析
    i = 0
    while i < len(sentences):
        sentence = sentences[i]
        
        # 提取具体标签、情感和描述
        detailed_labels = extract_labels_and_sentiment(sentence)
        
        # 如果当前句情感和标签无法完全确定，则合并当前句子与下一句
        if "unknown" in detailed_labels:
            if i + 1 < len(sentences):
                sentence += " " + sentences[i + 1]
                i += 1  
                detailed_labels = extract_labels_and_sentiment(sentence)
        
        # 生成标签
        for label, details in detailed_labels.items():
            labels[label] = {
                "情感激烈程度": details["情感激烈程度"],
                "简要描述": details["简要描述"]
            }
        
        i += 1
    
    return labels

# 主函数
def main():
    all_labels = {}  
    review_index = 1  # 评论编号
    
    # 加速，单线程太慢了
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(generate_labels, reviews))
    
    for result in results:
        all_labels[f"Review {review_index}"] = result
        review_index += 1
    
    # 输出结果
    for review, tags in all_labels.items():
        output = f"{review}: "
        # 确定输出格式
        for tag, details in tags.items():
            output += f"{tag}:{{情感激烈程度：{details['情感激烈程度']}，简要描述：{details['简要描述']}}}；\n"
        output = output.rstrip("；")
        print(output)


# 运行主函数
if __name__ == "__main__":
    main()
