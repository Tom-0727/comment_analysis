

COMMANA_DICT = {
    "desk": '''
Example1: comment="Wonderful desk! Wonderful people to work with. Thank you"; output={}
Example2: comment="It's a great looking product once it is all put together. There are a lot of screws, so be careful when screwing the frame to the desk top panels to prevent screws penetrating through the panels. Double check the screw sizes."; output={'Pos1': 'Aesthetics', 'Neu1': 'Number of Assembly Parts'}
Example3: comment="The desk is beautiful looking although it is a little bit deceiving. Kinda wish I ordered a different one. I agree with other reviews that the set up takes forever and there are SO MANY PARTS! I am petite/5'3 and bought a computer chair that is equivalent to the height of a dining room table chair, nothing special and I have a hard time putting my legs under so I do wish it was taller. Also, the drawers aren't as deep as the desk is so that's a bummer they are so small. It's just big enough to fit a 8 x 10 sheet of paper. Overall looks beautiful but functionality can be improved."; output={'Pos1': 'Aesthetics', 'Neg1': 'Installation Time', 'Neg2': 'Number of Assembly Parts', 'Neg3': 'Legroom Space', 'Neg4': 'Storage Space'}''',
    "standing_desk": '''
Example1: comment="Wonderful desk! Wonderful people to work with. Thank you"; output={}
Example2: comment="Must have desk for long hours. Excellent leg design is really unobtrusive for legs and chair. Works great. I used function daily. Excellent value."; output={'Pos1': 'Value for Money'}
Example3: comment="The desk is beautiful looking. However, coupling bolts missing from the package. customer support to get help for this is awful."; output={'Pos1': 'Appearance & Style', 'Neg1': 'Product Integrity', 'Neg2': 'customer service'}''',
    "banshi_desk": '''
Example1: comment="Wonderful desk! Wonderful people to work with. Thank you"; output={}
Example2: comment="Cheap particle board, desk is probably worth about a third of what they are selling it for. Was basically falling apart coming out of the box."; output={'Neg1': 'Value for Money', 'Neg2': 'Product Integrity'}
Example3: comment="DO NOT buy this desk. So not worth the money it costs. Takes up a lot of space, but also has plenty of space for storage. Problem is, once it's together, it's barely holding on by the wooden pegs and plywood everything is attached with. Back bracing piece also game in broken in half and unable to use. Spent 10 hours putting it together for a hunk of junk that was missing screw holes to begin with too."; output={'Neg1': 'Value for Money', 'Neu1': 'Storage Features', 'Neg2': 'Product Integrity', 'Neg3': 'Assembly difficulty & Time'}''',
    "gangmu_desk": '''
Example1: comment="Wonderful desk! Wonderful people to work with. Thank you"; output={}
Example2: comment="Easy to assemble. The table top is real wood. Great price."; output={'Pos1': 'Assembly Difficulty & Time', 'Pos2': 'Desktop Quality', 'Pos3': 'Value for Money'}
Example3: comment="wasn't even the same measurements as what it said in the pictures"; output={'Neg1': 'Product Image/Description Mismatch'}''',
    "ceiling_fan": '''
Example1: comment="Good fan! Lets go!"; output={}
Example2: comment="Classy exciting fan to turn heads!"; output={'Pos1': 'Style & Appearance'}
Example3: comment="I love this fan! It is so quiet and moves a lot of air. I have it in my bedroom and it is perfect. I love the remote control feature. I would recommend this fan to anyone."; output={'Pos1': 'Noise Level', 'Pos2': 'Airflow', 'Pos3': 'Remote & Control Functions', 'Pos4': 'Recommendation'}''',
}