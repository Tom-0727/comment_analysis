'''
文件说明：这里实现大模型agent的接口，包括OpenAI、API2D、Qwen等，以及agent的基类。
agent的基类：
- 初始化：初始化agent的参数，包括大模型、提示词模板、体验点分类标准等。
- 评论分析：根据评论和体验点分类标准，分析评论的体验点。
- 体验点提取：根据评论和体验点分类标准，提取评论的体验点。
- 二次审查：根据评论和体验点分类标准，二次审查评论的体验点。
- 无监督体验点提取：根据评论和体验点分类标准，无监督提取评论的体验点。
- 大模型调用：调用大模型，实现评论分析、体验点提取、二次审查、无监督体验点提取。
'''
import json
import http.client

from openai import OpenAI
from modules.classes import POINTS
from modules.examples.comment_analyze import COMMANA_DICT
from modules.examples.points_extract import POINTSEXT_DICT
from modules.examples.inspect import INSPECT_DICT



class CommentAnalysisAgent:
    def __init__(self, criteria, template):
        self.points = POINTS[criteria]
        self.comment_analyze_prompt = self.get_comment_analyze_prompt(template)
        self.points_extract_prompt = self.get_points_extract_prompt(template)
        self.inspect_prompt = self.get_inspect_prompt(template)

    def get_comment_analyze_prompt(self, template):
        points = str(self.points)
        prompt = '''You are a review analyst. Your task is to extract aspects from customer reviews, which can be positive, negative or neutral. Follow the order in which the points are mentioned in the review and output whether each point is a positive, negative or neutral aspect along with the review angle. The output format should be:{'Pos1': 'xxx', ..., 'PosN': 'xxx', 'Neg1': 'xxx', ..., 'NegN': 'xxx', 'Neu1': 'xxx', 'NeuN': 'xxx'}, If there are no relevant points, output `{}`.
- The angles for extracting positive and negative review points include: ''' + points + '''
- A review should have a clear emotional bias to be considered positive or negative. A statement like "sturdy" should be considered for its positive aspect of "stability", but a statement like "it's nice" should not.''' + COMMANA_DICT[template] + '''
!Extract only the points explicitly mentioned in the comments, without making any assumptions or inferences. Show the reasoning process without break line and then output the extracted aspects.
Now do: comment='''
        return prompt

    def get_points_extract_prompt(self, template):
        prompt = '''You are a review analyst. You task is to extract customers' experience points from customer reviews. These are all reviews for a product. The answer format should be {'point1': 'simple description of what reviewer talked', ...}.
- When categorizing user feedback on experience points, the definitions should be as specific and informative as possible. For example, a comment like "This table is good" is too vague and lacks specific information. In contrast, "This table looks good" provides a clear point, indicating the table's aesthetic appeal. Therefore, clear definitions can help us better understand the users' actual experiences.''' + POINTSEXT_DICT[template] + '''
Now do: comment='''
        return prompt
    
    def get_inspect_prompt(self, template):
        prompt = '''You are a comment analyst. You will have a comment and a dict of points in the form of {'Pos1': 'xxx', ..., 'PosN': 'xxx', 'Neg1': 'xxx', ..., 'NegN': 'xxx', 'Neu1': 'xxx', 'NeuN': 'xxx'}, where the key of dict is emotion bias, and the value of dict is the point.
You task is to check whether the points are actually in the comment or not, and check whether the emotional bias is correct. You should show your analysis process and output {'Integrity': 'True/False'}.''' + INSPECT_DICT[template] + ''' 
Now do: comment='''
        return prompt
    
    def preprocess(self, text):
        text = text.replace('\n', ' ')
        text = text.replace('"', "")
        return text
    
    def translate(self, text):
        text = self.preprocess(text)
        task_text =  "下面的文本发生在商品评论的场景:\n" + text + "\n将上面的文本原样翻译为中文："
        response = self.one_shot(task_text)
        return response
    
    def comment_analyze(self, comment):
        comment = self.preprocess(comment)
        task_text = self.comment_analyze_prompt + '"' + comment + '"; output='
        response = self.one_shot(task_text)
        return response
    
    def points_extract(self, comment):
        comment = self.preprocess(comment)
        task_text = self.points_extract_prompt + '"' + comment + '"; output='
        response = self.one_shot(task_text)
        return response

    def inspect(self, comment, pre_points):
        comment = self.preprocess(comment)
        task_text = self.inspect_prompt + '"' + comment + '"'+'; points='+ pre_points +'; output='
        response = self.one_shot(task_text)
        return response

    def one_shot(self, text):
        raise NotImplementedError("Subclass must implement this method")


class OpenAICommentAnalysisAgent(CommentAnalysisAgent):
    def __init__(self, openai_key, criteria, template, model="gpt-4o-2024-08-06"):
        self.client = OpenAI(api_key=openai_key)
        self.model = model
        super().__init__(criteria, template)

    def one_shot(self, text):
        completion = self.client.chat.completions.create(
            model=self.model,
            store=True,
            temperature=0.175,
            messages=[
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content


class API2DCommentAnalysisAgent(CommentAnalysisAgent):
    def __init__(self, forward_key, criteria, template, model="gpt-4o-2024-08-06"):
        self.conn = http.client.HTTPSConnection("oa.api2d.net")
        self.model = model
        self.headers = {
            'Authorization': f'Bearer {forward_key}',
            'Content-Type': 'application/json'
        }
        super().__init__(criteria, template)

    def one_shot(self, text):
        payload = json.dumps({
            "model": self.model,
            "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": text},
                        ],
                    },
                ],
            "safe_mode": False
        })
        self.conn.request("POST", "/v1/chat/completions", payload, self.headers)
        res = self.conn.getresponse()
        data = res.read()
        resp = data.decode("utf-8")
        resp = eval(resp.replace('null', '0'))

        return resp['choices'][0]['message']['content']
    

class QwenCommentAnalysisAgent(CommentAnalysisAgent):
    def __init__(self, key, criteria, template, model="qwen-plus"):
        self.client = OpenAI(
            api_key=key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = model
        super().__init__(criteria, template)

    def one_shot(self, text):
        completion = self.client.chat.completions.create(
            model=self.model, # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': text}
                ]
        )

        return completion.choices[0].message.content
