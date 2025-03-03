from openai import OpenAI
from classes import ENGLISH_POINTS, CHINESE_POINTS


class CommentAnalysisAgent:
    def __init__(self, openai_key, model="gpt-4o-2024-08-06"):
        self.client = OpenAI(api_key=openai_key)
        self.model = model

        self.comment_analyze_prompt = self.get_comment_analyze_prompt()

    def preprocess(self, text):
        text = text.replace('\n', ' ')
        text = text.replace('"', "")
        return text
    
    def comment_analyze(self, comment):
        comment = self.preprocess(comment)
        task_text = self.comment_analyze_prompt + '"' + comment + '"; 输出：'
        response = self.one_shot(task_text)
        return response

    def get_comment_analyze_prompt(self):
        chinese_points = '<' + '>，<'.join(CHINESE_POINTS) + '>'
        chinese_prompt = '''你是评论分析师。你的任务是从客户评论中提取观点，这些观点可以是正面的、负面的或中性的。按照评论中提到的顺序输出每个观点是正面、负面还是中性观点，以及评论的角度。输出格式应为：{'Pos1': 'xxx', ..., 'PosN': 'xxx', 'Neg1': 'xxx', ..., 'NegN': 'xxx', 'Neu1': 'xxx', 'NeuN': 'xxx'}，Pos=正面，Neg=负面，Neu=中性。如果没有相关观点，则输出 `{}`。
- 提取评论观点的角度包括：''' + chinese_points + '''
- 像“桌子很不错”、“质量很好”这样的表述不应被视为任何观点。只考虑能对应上面角度列表里具体观点。
- 评论必须有明确的情感倾向才能被视为正面或负面，否则是中性。
示例1：comment="很棒的桌子！很棒的合作伙伴。谢谢你们。"；输出：{}
示例2：comment="一旦组装完成，这是一款外观很棒的产品。有很多螺丝，所以在将框架拧到桌面板上时要小心，以防止螺丝穿透面板。请仔细检查螺丝的尺寸。"；输出：{'Pos1': '美观性', 'Neu1': '需拼装组件数量'}
示例3：comment="这张桌子外观很漂亮，但有点让人失望。有点希望我订购了另一张。我同意其他评论，安装过程非常漫长，而且有太多的零件！我身材娇小，身高5'3，买了一把相当于餐桌椅高度的电脑椅，没什么特别的，但我很难把腿放进去，所以我希望它能更高一些。此外，抽屉的深度不如桌子那么深，所以它们很小，这有点遗憾。它刚好能放下一张8 x 10的纸。总的来说，外观很漂亮，但功能性可以改进。"；输出：{'Pos1': '美观度', 'Neg1': '安装时长', 'Neg2': '需拼装组件数量', 'Neg3': '腿部空间大小', 'Neg4': '抽屉大小'}
！**只提取评论中明确提到的观点，不要做任何假设。不要换行，展示推理分析过程，最后按格式输出提取的观点。**
现在开始分析：comment='''
        english_points = '<' + '>, <'.join(ENGLISH_POINTS) + '>'
        english_prompt = '''You are a review analyst. Your task is to extract aspects from customer reviews, which can be positive, negative or neutral. Follow the order in which the points are mentioned in the review and output whether each point is a positive, negative or neutral aspect along with the review angle. The output format should be:{'Pos1': 'xxx', ..., 'PosN': 'xxx', 'Neg1': 'xxx', ..., 'NegN': 'xxx', 'Neu1': 'xxx', 'NeuN': 'xxx'}, If there are no relevant points, output `{}`.
- The angles for extracting positive and negative review points include: ''' + english_points + '''
- Statement like 'the desk is nice/good', 'Good quality' should not be considered as any aspect. Only consider the specific points mentioned in the review.
- A review should have a clear emotional bias to be considered positive or negative.
Example1: comment="Wonderful desk! Wonderful people to work with. Thank you"; output={}
Example2: comment="It's a great looking product once it is all put together. There are a lot of screws, so be careful when screwing the frame to the desk top panels to prevent screws penetrating through the panels. Double check the screw sizes."; output={'Pos1': 'Aesthetics', 'Neu1': 'Number of Assembly Parts'}
Example3: comment="The desk is beautiful looking although it is a little bit deceiving. Kinda wish I ordered a different one. I agree with other reviews that the set up takes forever and there are SO MANY PARTS! I am petite/5'3 and bought a computer chair that is equivalent to the height of a dining room table chair, nothing special and I have a hard time putting my legs under so I do wish it was taller. Also, the drawers aren't as deep as the desk is so that's a bummer they are so small. It's just big enough to fit a 8 x 10 sheet of paper. Overall looks beautiful but functionality can be improved."; output={'Pos1': 'Aesthetics', 'Neg1': 'Installation Time', 'Neg2': 'Number of Assembly Parts', 'Neg3': 'Legroom Space', 'Neg4': 'Drawer Size'}
!Extract only the points explicitly mentioned in the comments, without making any assumptions or inferences. Show the reasoning process without break line and then output the extracted aspects.
Now do: comment='''
        return english_prompt
    
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
    


class CommentTranslateAgent:
    def __init__(self, openai_key, model="gpt-4o-2024-08-06"):
        self.client = OpenAI(api_key=openai_key)
        self.model = model

    def preprocess(self, text):
        text = text.replace('\n', ' ')
        text = text.replace('"', "")
        return text
    
    def translate(self, text):
        text = self.preprocess(text)
        task_text =  "下面的英文发生在商品评论的场景:\n" + text + "\n将上面的英文原样翻译为中文："
        response = self.one_shot(task_text)

        return response
    
    def one_shot(self, text):
        completion = self.client.chat.completions.create(
            model=self.model,
            store=True,
            temperature=0,
            messages=[
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content
    


if __name__ == '__main__':
    robot = CommentAnalysisAgent(openai_key='xxx', model="gpt-4o-2024-08-06")
    print(robot.get_comment_analyze_prompt())