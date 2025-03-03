import os
import pandas as pd

from tqdm import tqdm


def merge_xlsx(folder_path, output_file):
    files_lis = os.listdir(folder_path)
    writer = pd.ExcelWriter(output_file, engine="openpyxl")


    for file in tqdm(files_lis):
        if file.endswith(".xlsx"):
            file_path = os.path.join(folder_path, file)
            file = file.replace('_done.xlsx', '.xlsx')
            try:
                df = pd.read_excel(file_path, sheet_name=None)  # 读取所有 sheet
                for sheet_name, sheet_data in df.items():
                    new_sheet_name = f"{os.path.splitext(file)[0]}"  # 避免重名
                    sheet_data.to_excel(writer, sheet_name=new_sheet_name, index=False)
            except Exception as e:
                print(f"无法读取 {file}: {e}")
    writer.close()
    print(f"合并完成，保存为 {output_file}")


if __name__ == '__main__':
    merge_xlsx(folder_path='./results/v2_comment_analysis', output_file='./results/final_outcome/v2_outcome.xlsx')