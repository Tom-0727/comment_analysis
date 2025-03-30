import json
import http.client

from openai import OpenAI
from modules.classes import POINTS



class CommentAnalysisAgent:
    def __init__(self, criteria):
        self.points = POINTS[criteria]
        self.comment_analyze_prompt = self.get_comment_analyze_prompt()
        self.points_extract_prompt = self.get_points_extract_prompt()
        self.inspect_prompt = self.get_inspect_prompt()

    def get_comment_analyze_prompt(self):
        points = str(self.points)
        prompt = '''You are a review analyst. Your task is to extract aspects from customer reviews, which can be positive, negative or neutral. Follow the order in which the points are mentioned in the review and output whether each point is a positive, negative or neutral aspect along with the review angle. The output format should be:{'Pos1': 'xxx', ..., 'PosN': 'xxx', 'Neg1': 'xxx', ..., 'NegN': 'xxx', 'Neu1': 'xxx', 'NeuN': 'xxx'}, If there are no relevant points, output `{}`.
- The angles for extracting positive and negative review points include: ''' + points + '''
- A review should have a clear emotional bias to be considered positive or negative. A statement like "sturdy" should be considered for its positive aspect of "stability", but a statement like "it's nice" should not.
Example1: comment="Wonderful desk! Wonderful people to work with. Thank you"; output={}
Example2: comment="It's a great looking product once it is all put together. There are a lot of screws, so be careful when screwing the frame to the desk top panels to prevent screws penetrating through the panels. Double check the screw sizes."; output={'Pos1': 'Aesthetics', 'Neu1': 'Number of Assembly Parts'}
Example3: comment="The desk is beautiful looking although it is a little bit deceiving. Kinda wish I ordered a different one. I agree with other reviews that the set up takes forever and there are SO MANY PARTS! I am petite/5'3 and bought a computer chair that is equivalent to the height of a dining room table chair, nothing special and I have a hard time putting my legs under so I do wish it was taller. Also, the drawers aren't as deep as the desk is so that's a bummer they are so small. It's just big enough to fit a 8 x 10 sheet of paper. Overall looks beautiful but functionality can be improved."; output={'Pos1': 'Aesthetics', 'Neg1': 'Installation Time', 'Neg2': 'Number of Assembly Parts', 'Neg3': 'Legroom Space', 'Neg4': 'Storage Space'}
!Extract only the points explicitly mentioned in the comments, without making any assumptions or inferences. Show the reasoning process without break line and then output the extracted aspects.
Now do: comment='''
        return prompt

    def get_points_extract_prompt(self):
        prompt = '''You are a review analyst. You task is to extract customers' experience points from customer reviews. These are all reviews for a desk. The answer format should be {'point1': 'simple description of what reviewer talked', ...}.
- When categorizing user feedback on experience points, the definitions should be as specific and informative as possible. For example, a comment like "This table is good" is too vague and lacks specific information. In contrast, "This table looks good" provides a clear point, indicating the table's aesthetic appeal. Therefore, clear definitions can help us better understand the users' actual experiences.
Example1: comment="Wonderful desk! Wonderful people to work with. Thank you"; output={}
Example2: comment="It's a great looking product once it is all put together. There are a lot of screws, so be careful when screwing the frame to the desk top panels to prevent screws penetrating through the panels. Double check the screw sizes."; output={'Aesthetics': 'great looking product', 'Number of Assembly Parts': 'a lot of screws'}
Now do: comment='''
        return prompt
    
    def get_inspect_prompt(self):
        prompt = '''You are a comment analyst. You will have a comment and a dict of points in the form of {'Pos1': 'xxx', ..., 'PosN': 'xxx', 'Neg1': 'xxx', ..., 'NegN': 'xxx', 'Neu1': 'xxx', 'NeuN': 'xxx'}, where the key of dict is emotion bias, and the value of dict is the point.
You task is to check whether the points are actually in the comment or not, and check whether the emotional bias is correct. You should show your analysis process and output {'Integrity': 'True/False'}.
Example1: comment="It's a great looking product once it is all put together. There are a lot of screws, so be careful when screwing the frame to the desk top panels to prevent screws penetrating through the panels. Double check the screw sizes."; points={'Pos1': 'Aesthetics', 'Neu1': 'Number of Assembly Parts', 'Neg1': Stability}; output=The review did not mention stability, so {'Integrity': 'False'}
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
    def __init__(self, openai_key, criteria, model="gpt-4o-2024-08-06"):
        self.client = OpenAI(api_key=openai_key)
        self.model = model
        super().__init__(criteria)

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
    def __init__(self, forward_key, criteria, model="gpt-4o-2024-08-06"):
        self.conn = http.client.HTTPSConnection("oa.api2d.net")
        self.model = model
        self.headers = {
            'Authorization': f'Bearer {forward_key}',
            'Content-Type': 'application/json'
        }
        super().__init__(criteria)

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