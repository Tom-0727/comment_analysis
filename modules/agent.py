from openai import OpenAI



class CommentAnalysisAgent:
    def __init__(self, openai_key, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=openai_key)
        self.model = model

    def one_shot(self, text):
        completion = self.client.chat.completions.create(
            model=self.model,
            store=True,
            messages=[
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content