from openai import OpenAI
from modules.classes import ENGLISH_POINTS


class OpenAICommentAnalysisAgent:
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
    
    def translate(self, text):
        text = self.preprocess(text)
        task_text =  "下面的文本发生在商品评论的场景:\n" + text + "\n将上面的文本原样翻译为中文："
        response = self.one_shot(task_text)

        return response

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
    


