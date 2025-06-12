INSPECT_DICT = {
    "mock": '''
Example1: comment="This is a great product! I love it!"; points={'Pos1': 'Quality'}; output=The review did not mention specific quality aspects, so {'Integrity': 'False'}
Example2: comment="The quality is good but the price is a bit high. The design is beautiful."; points={'Pos1': 'Quality', 'Neg1': 'Price', 'Pos2': 'Design'}; output=All points are supported by the review, so {'Integrity': 'True'}
Example3: comment="Not worth the money. The material is poor and it's difficult to assemble. However, the color is nice."; points={'Neg1': 'Value', 'Neg2': 'Material', 'Neg3': 'Assembly', 'Pos1': 'Color'}; output=All points are supported by the review, so {'Integrity': 'True'}'''
}