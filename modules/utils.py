import pandas as pd



def csv_enter(file_path, time_thre='2023-01-01'):
    df = pd.read_csv(file_path, sep=None, engine='python')
    print(df.columns)

    required_columns = ['评论内容', '评论时间', '评分']
    if not all(col in df.columns for col in required_columns):
        raise ValueError("DataFrame is missing one or more required columns: {}".format(required_columns))
    
    df = df.dropna(subset=['评论内容', '评论时间', '评分'])

    df['评论时间'] = pd.to_datetime(df['评论时间'], format='%Y-%m-%d')
    filtered_df = df[df["评论时间"] > pd.to_datetime(time_thre)]
    filtered_df = filtered_df.reset_index(drop=True)
    print('Before Time filtering:', sep=' ')
    print(df.shape)
    print('After Time filtering:', sep=' ') 
    print(filtered_df.shape)

    return filtered_df


def amz_xlsx_enter(file_path, time_thre='2023-01-01'):
    xls = pd.ExcelFile(file_path)
    all_sheet_names = xls.sheet_names
    print(all_sheet_names)
    # print("文件中存在的sheet有：", all_sheet_names)

    df = pd.read_excel(file_path, sheet_name=all_sheet_names[0])
    print(df.shape)
    print(df.columns)

    df = df.rename(columns={'内容': '评论内容', '星级': '评分'})
    df['评论时间'] = pd.to_datetime(df['评论时间'], format='%Y-%m-%d')
    filtered_df = df[df["评论时间"] > pd.to_datetime(time_thre)]
    filtered_df = filtered_df.reset_index(drop=True)
    print('Before Time filtering:', sep=' ')
    print(df.shape)
    print('After Time filtering:', sep=' ') 
    print(filtered_df.shape)
    
    return df
