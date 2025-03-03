from openai import OpenAI



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
        prompt = '''你是评论分析师。你的任务是从客户评论中提取观点，这些观点可以是正面的、负面的或中性的。按照评论中提到的顺序输出每个观点是正面、负面还是中性观点，以及评论的角度。输出格式应为：{'Pos1': 'xxx', ..., 'PosN': 'xxx', 'Neg1': 'xxx', ..., 'NegN': 'xxx', 'Neu1': 'xxx', 'NeuN': 'xxx'}，Pos=正面，Neg=负面，Neu=中性。如果没有相关观点，则输出 `{}`。
- 提取评论观点的角度包括：<安装难度>, <说明书内容>, <安装时长>, <搬运难度>, <包装保护性>, <抽屉滑轨顺畅度>, <抽屉大小>, <整体收纳空间>, <错件情况>, <附加电源USB插座>, <柜门开合顺畅度>, <客服质量>, <螺丝孔位匹配度>, <气味情况>, <缺件情况>, <使用噪音>, <腿部空间大小>, <五金件损坏情况>, <物流速度>, <桌体破损情况>, <桌板材质>, <桌板厚度>, <桌面防水性>, <防滑性>, <稳定性>, <美观度>, <桌面边缘处理>, <需拼装组件数量>, <桌面材质>, <易清洁性质>, <耐脏性>, <螺丝钉外观>, <线缆管理>, <金属零部件变形情况>, <多板平齐情况>, <退货运输费用>, <运输货品完好度>。
- 像“桌子很不错”、“质量很好”这样的表述不应被视为任何观点。只考虑能对应上面角度列表里具体观点。
- 评论必须有明确的情感倾向才能被视为正面或负面，否则是中性。
示例1：comment="很棒的桌子！很棒的合作伙伴。谢谢你们。"；输出：{}
示例2：comment="一旦组装完成，这是一款外观很棒的产品。有很多螺丝，所以在将框架拧到桌面板上时要小心，以防止螺丝穿透面板。请仔细检查螺丝的尺寸。"；输出：{'Pos1': '美观性', 'Neu1': '需拼装组件数量'}
示例3：comment="这张桌子外观很漂亮，但有点让人失望。有点希望我订购了另一张。我同意其他评论，安装过程非常漫长，而且有太多的零件！我身材娇小，身高5'3，买了一把相当于餐桌椅高度的电脑椅，没什么特别的，但我很难把腿放进去，所以我希望它能更高一些。此外，抽屉的深度不如桌子那么深，所以它们很小，这有点遗憾。它刚好能放下一张8 x 10的纸。总的来说，外观很漂亮，但功能性可以改进。"；输出：{'Pos1': '美观度', 'Neg1': '安装时长', 'Neg2': '需拼装组件数量', 'Neg3': '腿部空间大小', 'Neg4': '抽屉大小'}
！**只提取评论中明确提到的观点，不要做任何假设。不要换行，展示推理分析过程，最后按格式输出提取的观点。**
现在开始分析：comment='''
        return prompt
    
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