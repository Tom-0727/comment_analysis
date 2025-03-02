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
        prompt = '''You are a review analyst. Your task is to extract positive and negative aspects from customer reviews. Follow the order in which the points are mentioned in the review and output whether each point is a positive or negative aspect along with the review angle. The output format should be:{'Pos1': 'xxx', ..., 'PosN': 'xxx', 'Neg1': 'xxx', ..., 'NegN': 'xxx'}, If there are no relevant points, output `{}`.
The angles for extracting positive and negative review points include: <Installation Difficulty>, <Manual Clarity>, <Installation Time>, <Ease of Moving>, <Packaging Protection>, <Drawer Slide Smoothness>, <Drawer Size>, <Overall Storage Space>, <Wrong or Misfit Parts>, <Extra Power/USB Sockets>, <Cabinet Door Smoothness>, <Customer Service Quality>, <Screw Hole Alignment>, <Odor>, <Missing Parts>, <Noise During Use>, <Legroom Space>, <Hardware Damage>, <Shipping Speed>, <Table Surface Damage>, <Tabletop Material>, <Tabletop Thickness>, <Water Resistance>, <Anti-Slip>, <Stability>, <Aesthetics>, <Edge Finishing>, <Number of Assembly Parts>, <Surface Material>, <Ease of Cleaning>, <Stain Resistance>, <Screw Appearance>, <Cable Management>, <Metal Part Deformation>, <Panel Alignment>, <Return Shipping Cost>, <Shipment Condition>
Example1: comment='Wonderful desk! Wonderful people to work with. Thank you'; output={}
Example2: comment='It's a nice desk was pretty easy to assemble'; output={'Pos1': 'Installation Difficulty'}
Example3: comment='The desk is beautiful looking although it is a little bit deceiving. Kinda wish I ordered a different one. I agree with other reviews that the set up takes forever and there are SO MANY PARTS! I am petite/5'3 and bought a computer chair that is equivalent to the height of a dining room table chair, nothing special and I have a hard time putting my legs under so I do wish it was taller. Also, the drawers aren't as deep as the desk is so that's a bummer they are so small. It's just big enough to fit a 8 x 10 sheet of paper. Overall looks beautiful but functionality can be improved.'; output={'Pos1': 'Aesthetics', 'Neg1': 'Installation Time', 'Neg2': 'Number of Assembly Parts', 'Neg3': 'Legroom Space', 'Neg4': 'Drawer Size'}
Now do: comment='''
        return prompt