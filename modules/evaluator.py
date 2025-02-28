import pandas as pd




def metric_calculate(testset, version):
    total_extraction = 0
    correct_extraction = 0
    wrong_extraction = 0
    expected_extraction = 0

    length = len(testset)
    for i in range(length):
        comment = testset.iloc[i]['内容']
        if not isinstance(comment, str):
            continue

        good_points = []
        bad_points = []
        # 很多column是好评点x, 差评点x的格式，从1开始，动态遍历所有这些columns，存储到good_points和bad_points中
        for j in range(1, 100):
            try:
                good_point = testset.iloc[i]['好评点' + str(j)]
            except:
                break
            if pd.notna(good_point):
                good_points.append(good_point)
        for j in range(1, 100):
            try:
                bad_point = testset.iloc[i]['差评点' + str(j)]
            except:
                break
            if pd.notna(bad_point):
                bad_points.append(bad_point)
        
        expected_extraction += len(good_points) + len(bad_points)
        response = testset.iloc[i][version]
        try:
            output = eval(response)
            # 遍历 output，将数据存入 DataFrame
            
            for key, value in output.items():
                total_extraction += 1
                if key[:3] == '好评点':
                    if value in good_points:
                        correct_extraction += 1
                    else:
                        wrong_extraction += 1
                elif key[:3] == '差评点':
                    if value in bad_points:
                        correct_extraction += 1
                    else:
                        wrong_extraction += 1
        except:
            pass
    print('total_extraction:', total_extraction)
    print('correct_extraction:', correct_extraction)
    print('wrong_extraction:', wrong_extraction)
    precision = correct_extraction / total_extraction
    recall = correct_extraction / expected_extraction
    print('precision:', precision)
    print('recall:', recall)

    return precision, recall