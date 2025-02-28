from openai import OpenAI



class CommentAnalysisAgent:
    def __init__(self, openai_key, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=openai_key)
        self.model = model

        self.comment_analyze_prompt = self.get_comment_analyze_prompt()

    def one_shot(self, text):
        completion = self.client.chat.completions.create(
            model=self.model,
            store=True,
            messages=[
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content
    
    def comment_analyze(self, comment):
        task_text = self.comment_analyze_prompt + "'" + comment + "'"
        response = self.one_shot(task_text)
        return response

    def get_comment_analyze_prompt(self):
        prompt = '''你是一个评论分析师。现在有个任务是根据买家的评论，提取出里面的好评点和差评点。你需要按照评论提及的点的顺序，依次输出是好评还是差评+评论角度；输出格式为 {'好评点1': 'xxx', ..., '好评点n': 'xxx'}，如果没有信息点则输出{}
评论的角度有：<安装难度>，<说明书内容>，<安装时长>，<搬运难度>，<包装保护性>，<抽屉滑轨顺畅度>，<抽屉大小>，<整体收纳空间>，<错件情况>，<附加电源USB插座>，<柜门开合顺畅度>，<客服质量>，<螺丝孔位匹配度>，<气味情况>，<缺件情况>，<使用噪音>，<腿部空间大小>，<五金件损坏情况>，<物流速度>，<桌体破损情况>，<桌板材质>，<桌板厚度>，<桌面防水性>，<桌腿防滑性>，<稳定性>，<美观度>，<桌面边缘处理>，<需拼装组件数量>，<桌面材质>，<易清洁性质>，<耐脏性>，<螺丝钉外观>，<线缆管理>，<金属零部件变形情况>，<多板平齐情况>，<退货运输费用>，<运输货品完好度>
Example1: comment='Wonderful desk! Wonderful people to work with. Thank you'; output={}
Example2: comment='It’s a nice desk was pretty easy to assemble'; output={'好评点1': '安装难度'}
Example3: comment='The desk is beautiful looking although it is a little bit deceiving. Kinda wish I ordered a different one. I agree with other reviews that the set up takes forever and there are SO MANY PARTS! I am petite/5’3 and bought a computer chair that is equivalent to the height of a dining room table chair, nothing special and I have a hard time putting my legs under so I do wish it was taller. Also, the drawers aren’t as deep as the desk is so that’s a bummer they are so small. It’s just big enough to fit a 8 x 10 sheet of paper. Overall looks beautiful but functionality can be improved.'; output={'好评点1': '美观度', '差评点1': '安装时长', '差评点2': '需拼装组件数量', '差评点3': '腿部空间大小', '差评点4': '抽屉大小'}
Now do: comment='''
        return prompt