import pandas as pd



def read_xlsx(file_path):
    # 读取Excel文件中的所有sheet
    xls = pd.ExcelFile(file_path)
    
    # 初始化一个空的DataFrame用于存储合并后的数据
    combined_df = pd.DataFrame()
    
    # 遍历所有sheet
    for sheet_name in xls.sheet_names:
        # 读取当前sheet为DataFrame
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # 将当前sheet的DataFrame追加到总DataFrame中
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    
    return combined_df