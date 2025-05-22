import gradio as gr
import pandas as pd
import time
import re
import os
import json
import ast
from datetime import datetime, timedelta
from modules.agent import OpenAICommentAnalysisAgent, API2DCommentAnalysisAgent, QwenCommentAnalysisAgent
from modules.utils import csv_enter, amz_xlsx_enter
from modules.classes import POINTS
from data_analyze import cal_importance, cal_satisfaction, cal_splitemo, expand_list_column

# 确保输出目录存在
os.makedirs("./buffer", exist_ok=True)

# 用于存储活跃用户信息
active_users = {}

def get_active_users():
    """获取当前活跃用户信息"""
    current_time = time.time()
    # 清理超过30分钟未活动的用户
    for user_id, info in list(active_users.items()):
        if current_time - info['last_active'] > 1800:  # 30分钟
            del active_users[user_id]
    
    # 格式化活跃用户信息
    if not active_users:
        return "当前没有活跃用户"
    
    user_info = "当前活跃用户：\n"
    for user_id, info in active_users.items():
        user_info += f"- 用户 {user_id}: 正在处理 {info['file_name']}，已处理 {info['progress']} 条评论\n"
    return user_info

def update_user_status(user_id, file_name, progress, total):
    """更新用户状态"""
    active_users[user_id] = {
        'file_name': file_name,
        'progress': f"{progress}/{total}",
        'last_active': time.time()
    }

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


def analyze_reviews(file, asin, model_type, api_key, product_type, template, 
                   need_translate, need_inspect, need_points_extract, progress=gr.Progress()):
    if file is None and asin == "":
        return "请上传文件或输入 ASIN", None

    # 生成用户ID
    user_id = str(int(time.time()))
    
    progress_text = ""
    
    # 生成输出文件名
    if file is not None:
        base_name = os.path.splitext(os.path.basename(file.name))[0]
        output_csv = f"./buffer/{base_name}_analyzed.csv"
        output_xlsx = f"./buffer/{base_name}_analyzed.xlsx"
        file_name = base_name
    else:
        output_csv = f"./buffer/{asin}_analyzed.csv"
        output_xlsx = f"./buffer/{asin}_analyzed.xlsx"
        file_name = asin

    try:
        if file is not None:
            if file.name.endswith('.csv'):
                df = csv_enter(file.name)
            elif file.name.endswith('.xlsx'):
                df = amz_xlsx_enter(file.name)
            else:
                return "不支持的文件格式，请上传 CSV 或 Excel 文件", None
        else:
            # TODO: 实现通过 ASIN 抓取数据的功能
            return "ASIN 抓取功能尚未实现", None

        # 初始化评论分析代理
        if model_type == "OpenAI":
            agent = OpenAICommentAnalysisAgent(api_key, product_type, template)
        elif model_type == "API2D":
            agent = API2DCommentAnalysisAgent(api_key, product_type, template)
        elif model_type == "Qwen":
            agent = QwenCommentAnalysisAgent(api_key, product_type, template)
        else:
            return "不支持的模型类型", None

        # 检查是否已有处理结果
        if not os.path.exists(output_csv):
            # 创建新文件
            columns = list(df.columns) + ['翻译评论', '分析结果', '观点提取', '检查结果', '好差评结果']
            pd.DataFrame(columns=columns).to_csv(output_csv, index=False, encoding='utf-8-sig')
            start_index = 0
        else:
            # 读取已处理的结果
            df_processed = pd.read_csv(output_csv)
            start_index = len(df_processed)
            progress_text += f"发现已有处理结果，从第 {start_index + 1} 条开始继续处理\n"

        # 分析评论
        total_comments = len(df)
        if start_index >= total_comments:
            return "所有评论已处理完成", output_xlsx

        progress(0, desc=f"开始分析评论... (从第 {start_index + 1} 条开始)")
        
        for idx, row in df.iloc[start_index:].iterrows():
            try:
                comment = row['评论内容']
                progress_text += f"分析中：{idx+1}/{total_comments} 条\n"
                progress((idx - start_index + 1) / (total_comments - start_index), 
                        desc=f"正在分析第 {idx+1}/{total_comments} 条评论")
                
                # 更新用户状态
                update_user_status(user_id, file_name, idx + 1, total_comments)
                
                # 分析评论（必须执行）
                analysis_result = agent.comment_analyze(comment)
                
                # 可选功能
                translated_comment = agent.translate(comment) if need_translate else ""
                points_result = agent.points_extract(comment) if need_points_extract else ""
                inspection_result = agent.inspect(comment, analysis_result) if need_inspect else ""
                
                # 提取好差评结果
                output_result = extract_output(analysis_result)
                output_result = remove_duplicate_values(output_result)
                
                # 创建单条结果，保留原始数据
                result = row.to_dict()
                # 添加分析结果
                result.update({
                    '翻译评论': translated_comment,
                    '分析结果': analysis_result,
                    '观点提取': points_result,
                    '检查结果': inspection_result,
                    '好差评结果': str(output_result)
                })
                
                # 立即保存单条结果
                pd.DataFrame([result]).to_csv(output_csv, mode='a', header=False, index=False, encoding='utf-8-sig')
                
                progress_text += f"✓ 第 {idx+1} 条评论分析完成并保存\n"
                
            except Exception as e:
                progress_text += f"✗ 第 {idx+1} 条评论分析失败：{str(e)}\n"
                continue

        # 读取分析结果进行数据处理
        df = pd.read_csv(output_csv)
        df['评论时间'] = pd.to_datetime(df['评论时间'])
        df = df.dropna(subset=['好差评结果'])

        # 计算时间戳
        now = datetime.now()
        half_year_ago = now - timedelta(days=365/2)
        half_year_date = half_year_ago.strftime('%Y-%m-%d')
        one_year_ago = now - timedelta(days=365)
        one_year_date = one_year_ago.strftime('%Y-%m-%d')
        two_years_ago = now - timedelta(days=365*2)
        two_years_date = two_years_ago.strftime('%Y-%m-%d')
        three_years_ago = now - timedelta(days=365*3)
        three_years_date = three_years_ago.strftime('%Y-%m-%d')
        time_stamps = {
            '近半年数据分析': half_year_date,
            '近一年数据分析': one_year_date,
            '近两年数据分析': two_years_date,
            '近三年数据分析': three_years_date
        }

        # 根据产品类型获取对应的criteria文件路径
        criteria_path = f"./modules/criterias/{product_type}_criteria.csv"
        if not os.path.exists(criteria_path):
            return f"找不到产品类型 {product_type} 的criteria文件", None
        
        # 读取criteria文件
        criteria_df = pd.read_csv(criteria_path, sep=None, engine='python')
        e2c_dict = dict(zip(criteria_df['体验点二级分类英文'].apply(str.lower), criteria_df['体验点二级分类']))

        df['好评'] = ''
        df['差评'] = ''
        df['中评'] = ''
        for i in range(len(df)):
            ext_pts = df.iloc[i]['好差评结果']
            try:
                ext_pts = eval(ext_pts)
            except:
                print(ext_pts)
                continue
            pos = []
            neg = []
            neu = []
            for k in ext_pts.keys():
                if 'Pos' in k or 'pos' in k:
                    ch = ext_pts[k]
                    ch = ch.strip().lower()
                    ch = e2c_dict[ch]
                    pos.append(ch)
                elif 'Neg' in k or 'neg' in k:
                    ch = ext_pts[k]
                    ch = ch.strip().lower()
                    ch = e2c_dict[ch]
                    neg.append(ch)
                elif 'Neu' in k or 'neu' in k:
                    ch = ext_pts[k]
                    ch = ch.strip().lower()
                    ch = e2c_dict[ch]
                    neu.append(ch)
            df.loc[i, '好评'] = str(pos)
            df.loc[i, '差评'] = str(neg)
            df.loc[i, '中评'] = str(neu)

        # 展开列表列
        expand_list_column(df, '好评', '好评')
        expand_list_column(df, '差评', '差评')
        expand_list_column(df, '中评', '中评')

        # 创建Excel文件，输出格式与data_analyze.py一致
        with pd.ExcelWriter(output_xlsx) as writer:
            # 输出好差评打标sheet
            df.to_excel(writer, sheet_name='好差评打标', index=False)
            # 输出体验点分类标准
            criteria_df.to_excel(writer, sheet_name='体验点分类标准', index=False)

            # 按时间区间输出分析sheet
            for stamp in time_stamps.keys():
                filtered_df = df[df['评论时间'] > time_stamps[stamp]]

                importance = cal_importance(filtered_df)
                satisfaction, diversity = cal_satisfaction(filtered_df)
                pos_frequency, neg_frequency, pos_satisfaction, neg_satisfaction = cal_splitemo(filtered_df)

                data = {
                    '重要度': importance,
                    '满意度': satisfaction,
                    '分歧度': diversity,
                    '好评频率': pos_frequency,
                    '差评频率': neg_frequency,
                    '好评满意度': pos_satisfaction,
                    '差评满意度': neg_satisfaction
                }
                analysis_df = pd.DataFrame(data)
                analysis_df.reset_index(inplace=True)
                analysis_df.rename(columns={'index': '体验点'}, inplace=True)
                analysis_df['Top痛点'] = analysis_df['重要度'] * analysis_df['满意度']

                # 体验点转中文
                for i in range(len(analysis_df)):
                    analysis_df.loc[i, '体验点'] = e2c_dict.get(str(analysis_df.loc[i, '体验点']).lower(), analysis_df.loc[i, '体验点'])
                analysis_df['评论条数'] = ''
                analysis_df.loc[0, '评论条数'] = len(filtered_df)

                analysis_df.to_excel(writer, sheet_name=stamp, index=False)

        # 处理完成后移除用户状态
        if user_id in active_users:
            del active_users[user_id]

        return progress_text + "分析完成！", output_xlsx

    except Exception as e:
        # 发生错误时也要移除用户状态
        if user_id in active_users:
            del active_users[user_id]
        return f"分析过程中出现错误：{str(e)}", None

def update_active_users_display():
    """更新活跃用户显示"""
    return get_active_users()

# 构建界面
with gr.Blocks() as demo:
    gr.Markdown("# 评论分析系统")
    
    # 活跃用户显示组件放在最前面
    with gr.Row():
        active_users_display = gr.Textbox(label="活跃用户", lines=10, value="当前没有活跃用户")
    with gr.Row():
        update_btn = gr.Button("刷新活跃用户")
        update_btn.click(fn=update_active_users_display, outputs=active_users_display)
    
    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="上传文件")
            asin_input = gr.Textbox(label="ASIN")
            model_type = gr.Dropdown(
                choices=["OpenAI", "API2D", "Qwen"],
                label="选择模型",
                value="OpenAI"
            )
            
            # 定义不同模型类型的版本选项
            model_versions = {
                "OpenAI": ["gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14"],
                "Qwen": ["qwen-plus", "qwen-plus-latest"],
                "API2D": ["gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "qwen-plus", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
            }
            
            model_version = gr.Dropdown(
                choices=model_versions["OpenAI"],
                label="选择模型版本",
                value=model_versions["OpenAI"][0]
            )
            
            def update_model_version(model_type):
                return gr.update(
                    choices=model_versions[model_type],
                    value=model_versions[model_type][0],
                    interactive=True
                )
            
            model_type.change(
                fn=update_model_version,
                inputs=[model_type],
                outputs=[model_version]
            )
            
            api_key = gr.Textbox(label="API Key", type="password")
            product_type = gr.Dropdown(
                choices=list(POINTS.keys()),
                label="选择产品类型",
                value=list(POINTS.keys())[0]
            )
            template = gr.Dropdown(
                choices=list(POINTS.keys()),
                label="提示词模板",
                value=list(POINTS.keys())[0]
            )
            # 增加一个提示，就是说以下每一个勾选了都会增加消耗和等待时间
            gr.Markdown("以下每一个勾选了都会增加消耗和等待时间，请谨慎勾选")
            need_translate = gr.Checkbox(label="需要大模型翻译", value=False)
            need_inspect = gr.Checkbox(label="需要大模型反审查", value=False)
            need_points_extract = gr.Checkbox(label="需要无监督观点提取", value=False)
            analyze_btn = gr.Button("开始分析")
            progress = gr.Textbox(label="进度", lines=10)
            output_file = gr.File(label="分析结果")
    
    analyze_btn.click(
        fn=analyze_reviews,
        inputs=[
            file_input, asin_input, model_type, api_key, product_type,
            template, need_translate, need_inspect, need_points_extract
        ],
        outputs=[progress, output_file]
    )

if __name__ == "__main__":
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
