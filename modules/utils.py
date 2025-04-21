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


def xlsx_enter():
    pass