import re



def extract_output(text):
    pattern = r'\{.*?\}'
    matches = re.findall(pattern, text, re.DOTALL)

    matches = [match.replace('\n', '') for match in matches]
    # 去除重复的字典字符串
    unique_matches = list(set(matches))  # 使用 set 去重，然后转回 list

    # 将去重后的字典字符串拼接成一个字符串
    extracted_output = ''.join(unique_matches)

    # 只要第一个{}包含起来的字典
    first_brace_index = extracted_output.find('{')
    last_brace_index = extracted_output.rfind('}')
    extracted_output = extracted_output[first_brace_index:last_brace_index + 1]
    
    # 使用 eval 将字符串转换为字典
    extracted_output = eval(extracted_output)
    
    return extracted_output



def remove_duplicate_values(input_dict):
    seen_values = set()  # 用于存储已经出现过的值
    output_dict = {}  # 用于存储最终的结果

    for key, value in input_dict.items():
        if value not in seen_values:
            seen_values.add(value)
            output_dict[key] = value

    return output_dict
