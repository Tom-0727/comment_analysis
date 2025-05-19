import gradio as gr
import pandas as pd
import time

# 模拟的分析函数（带进度显示）
def analyze_reviews(file, asin):
    if file is None and asin == "":
        return "请上传文件或输入 ASIN", None

    progress_text = ""
    # 模拟读取数据
    if file is not None:
        df = pd.read_csv(file.name)
    else:
        # 模拟通过 ASIN 抓取数据
        df = pd.DataFrame({"评论": [f"{asin}_样本评论{i}" for i in range(10)]})

    # 模拟进度分析（假设有10条数据）
    for i in range(20):
        time.sleep(0.4)  # 模拟耗时
        progress_text += f"分析中：{i+1}/10 条\n"

    # 模拟输出：把数据原样输出
    output_path = "./buffer/分析结果.csv"
    df.to_csv(output_path, index=False)
    return progress_text + "分析完成！", output_path


# 构建界面
with gr.Blocks() as demo:
    gr.Markdown("### 评论分析工具")

    with gr.Row():
        file_input = gr.File(label="上传CSV文件（可选）")
        asin_input = gr.Textbox(label="或输入ASIN")
        asin_dropdown = gr.Dropdown(choices=["ASIN_A", "ASIN_B", "ASIN_C"], label="选择ASIN（可选）")

    analyze_button = gr.Button("开始分析")

    progress_output = gr.Textbox(label="分析进度", lines=10)
    download_output = gr.File(label="下载结果")

    # 点击按钮时执行函数
    analyze_button.click(
        fn=analyze_reviews,
        inputs=[file_input, asin_input],
        outputs=[progress_output, download_output]
    )

demo.launch()
