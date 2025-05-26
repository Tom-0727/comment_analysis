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

from modules.data_analyzor import DataAnalyzor
from modules.point_extractor import extract_output, remove_duplicate_values
from modules.visualizor import create_quick_visualization

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
        data_analyzor = DataAnalyzor(criteria_path=f"./modules/criterias/{product_type}_criteria.csv")
        data_analyzor.analyze(file_path=output_csv, output_path=output_xlsx)

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

def create_visualization(excel_file):
    """创建数据可视化"""
    if excel_file is None:
        return "请先上传Excel文件", None, None
    
    try:
        # 检查文件是否存在
        if not os.path.exists(excel_file):
            return "文件不存在", None, None
        
        # 生成HTML文件路径
        base_name = os.path.splitext(os.path.basename(excel_file))[0]
        html_file = f"./visualizations/{base_name}_dashboard.html"
        
        # 创建可视化，传入HTML输出路径，不自动打开浏览器
        fig = create_quick_visualization(excel_file, output_html_path=html_file, auto_open_browser=False)
        
        # 返回成功信息、文件路径和图表对象
        return f"✅ 可视化创建成功！\n📊 图表已保存到: {html_file}\n🎯 可以在右侧查看图表，也可以下载HTML文件", html_file, fig
        
    except Exception as e:
        return f"❌ 创建可视化时出现错误：{str(e)}", None, None

def upload_excel_for_visualization(file):
    """上传Excel文件用于可视化"""
    if file is None:
        return "请上传Excel文件", None
    
    if not file.name.endswith('.xlsx'):
        return "请上传.xlsx格式的Excel文件", None
    
    return f"✅ 文件上传成功: {os.path.basename(file.name)}", file

# 构建界面
with gr.Blocks() as demo:
    gr.Markdown("# 评论分析系统")
    
    # 活跃用户显示组件放在最前面
    with gr.Row():
        active_users_display = gr.Textbox(label="活跃用户", lines=5, value="当前没有活跃用户")
    with gr.Row():
        update_btn = gr.Button("刷新活跃用户")
        update_btn.click(fn=update_active_users_display, outputs=active_users_display)
    
    # 使用Tab组件分离功能
    with gr.Tabs():
        # 评论分析标签页
        with gr.TabItem("评论分析"):
            with gr.Row():
                with gr.Column():
                    file_input = gr.File(label="上传文件")
                    asin_input = gr.Textbox(label="ASIN")
                    model_type = gr.Dropdown(
                        choices=["Qwen", "OpenAI", "API2D"],
                        label="选择模型",
                        value="Qwen"
                    )
                    
                    # 定义不同模型类型的版本选项
                    model_versions = {
                        "Qwen": ["qwen-plus", "qwen-plus-latest"],
                        "OpenAI": ["gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14"],
                        "API2D": ["gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "qwen-plus", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
                    }
                    
                    model_version = gr.Dropdown(
                        choices=model_versions["Qwen"],
                        label="选择模型版本",
                        value=model_versions["Qwen"][0]
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
                    need_points_extract = gr.Checkbox(label="需要无监督体验点提取", value=False)
                    analyze_btn = gr.Button("开始分析")
                    progress = gr.Textbox(label="进度", lines=10)
                    output_file = gr.File(label="分析结果")
        
        # 数据可视化标签页
        with gr.TabItem("数据可视化"):
            gr.Markdown("## 📊 数据可视化")
            gr.Markdown("上传已分析的Excel文件来生成交互式可视化图表")
            
            with gr.Row():
                with gr.Column():
                    # 可视化文件上传
                    viz_file_input = gr.File(
                        label="上传Excel文件", 
                        file_types=[".xlsx"],
                        type="filepath"
                    )
                    
                    # 可视化按钮
                    viz_btn = gr.Button("🎨 生成可视化", variant="primary")
                    
                    # 可视化状态显示
                    viz_status = gr.Textbox(label="可视化状态", lines=5)
                    
                    # HTML文件下载
                    viz_download = gr.File(label="下载可视化HTML文件")
                
                with gr.Column():
                    # 可视化图表显示区域
                    viz_plot = gr.Plot(label="可视化图表")
    
    # 绑定分析功能
    analyze_btn.click(
        fn=analyze_reviews,
        inputs=[
            file_input, asin_input, model_type, api_key, product_type,
            template, need_translate, need_inspect, need_points_extract
        ],
        outputs=[progress, output_file]
    )
    
    # 绑定可视化功能
    viz_btn.click(
        fn=create_visualization,
        inputs=[viz_file_input],
        outputs=[viz_status, viz_download, viz_plot]
    )

if __name__ == "__main__":
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
