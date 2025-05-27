'''
文件说明：这里实现数据可视化的接口，包括数据可视化、数据分析等。
'''
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os
import numpy as np



def create_quick_visualization(excel_path, output_html_path=None, auto_open_browser=False):
    """快速创建可视化
    Args:
        excel_path: Excel文件路径
        output_html_path: 输出HTML文件路径，如果为None则使用默认路径
        auto_open_browser: 是否自动打开浏览器
    """
    # 加载数据
    sheet_names = ['近半年数据分析', '近一年数据分析', '近两年数据分析', '近三年数据分析']
    data = {}
    
    for sheet_name in sheet_names:
        try:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            df = df.dropna(subset=['体验点'])
            data[sheet_name] = df
            print(f"已加载 {sheet_name}: {len(df)} 行数据")
        except Exception as e:
            print(f"加载 {sheet_name} 时出错: {e}")
    
    # 检查是否有数据
    if not data:
        raise ValueError("没有找到有效的数据表，请检查Excel文件是否包含正确的工作表")
    
    # 生成所有sheet的trace
    traces = []
    scatter_indices = []
    bar_indices = []
    importance_means = []
    for i, sheet_name in enumerate(sheet_names):
        if sheet_name not in data:
            continue
        df = data[sheet_name].copy()
        df['分歧度'] = pd.to_numeric(df['分歧度'], errors='coerce').fillna(0)
        df['Top痛点_数值'] = pd.to_numeric(df['Top痛点'], errors='coerce').fillna(0)
        df['分歧度'] = df['分歧度'].clip(lower=0)
        # jitter
        jitter_scale_x = (df['重要度'].max() - df['重要度'].min()) * 0.01 if df['重要度'].max() > df['重要度'].min() else 0.01
        jitter_scale_y = (df['满意度'].max() - df['满意度'].min()) * 0.01 if df['满意度'].max() > df['满意度'].min() else 0.01
        np.random.seed(42)
        jitter_x = np.random.uniform(-jitter_scale_x, jitter_scale_x, size=len(df))
        jitter_y = np.random.uniform(-jitter_scale_y, jitter_scale_y, size=len(df))
        df['重要度_jitter'] = df['重要度'] + jitter_x
        df['满意度_jitter'] = df['满意度'] + jitter_y
        # 点大小
        if df['分歧度'].max() > 0:
            df['分歧度_归一化'] = (df['分歧度'] - df['分歧度'].min()) / (df['分歧度'].max() - df['分歧度'].min())
            df['分歧度_显示'] = 5 + (df['分歧度_归一化'] ** 0.5) * 20
        else:
            df['分歧度_显示'] = 10
        importance_mean = df['重要度'].mean()
        importance_means.append(importance_mean)
        # bar数据
        sorted_df = df.sort_values('Top痛点_数值', ascending=True).reset_index(drop=True)
        bar_colors = sorted_df['Top痛点_数值']
        bar_text = sorted_df['体验点']
        mask = bar_text != '桌面尺寸'
        bar_text = bar_text[mask]
        bar_colors = bar_colors[mask]
        # scatter trace
        scatter = go.Scatter(
            x=df['重要度_jitter'],
            y=df['满意度_jitter'],
            mode='markers+text',
            text=df['体验点'],
            textposition=[
                'top center' if y >= 0 else 'bottom center' 
                for y in df['满意度']
            ],
            textfont=dict(size=9),
            cliponaxis=False,
            marker=dict(
                size=df['分歧度_显示'],
                color=df['Top痛点_数值'],
                colorscale='RdYlBu_r',
                opacity=0.8,
                line=dict(width=1, color='black'),
                showscale=False
            ),
            hovertemplate="<b>%{text}</b><br>重要度: %{customdata[0]:.3f}<br>满意度: %{customdata[1]:.3f}<br>分歧度: %{customdata[2]:.3f}<br>Top痛点: %{customdata[3]:.3f}<br><extra></extra>",
            customdata=np.stack([
                df['重要度'],
                df['满意度'],
                df['分歧度'],
                df['Top痛点_数值']
            ], axis=-1),
            name=sheet_name,
            showlegend=False,
            visible=(i==0)
        )
        traces.append(scatter)
        scatter_indices.append(len(traces)-1)
        # bar trace
        bar = go.Bar(
            x=[1]*len(bar_text),
            y=bar_text,
            orientation='h',
            marker=dict(
                color=bar_colors,
                colorscale='RdYlBu_r',
                cmin=df['Top痛点_数值'].min(),
                cmax=df['Top痛点_数值'].max(),
            ),
            text=bar_text,
            textposition='inside',
            insidetextanchor='middle',
            showlegend=False,
            hovertemplate="%{y}<br>Top痛点值: %{customdata:.3f}<extra></extra>",
            customdata=bar_colors,
            visible=(i==0)
        )
        traces.append(bar)
        bar_indices.append(len(traces)-1)
    # 创建双列子图
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.7, 0.3],
        specs=[[{"type": "scatter"}, {"type": "bar"}]],
        horizontal_spacing=0.08,
        subplot_titles=(sheet_names[0], "Top痛点排序")
    )
    for idx, trace in enumerate(traces):
        if idx % 2 == 0:
            fig.add_trace(trace, row=1, col=1)
        else:
            fig.add_trace(trace, row=1, col=2)
    # 只添加一条vline和注释，初始为第一个sheet
    vline_shape = dict(
        type="line",
        x0=importance_means[0], x1=importance_means[0],
        y0=data[sheet_names[0]]['满意度'].min() - 0.15, y1=data[sheet_names[0]]['满意度'].max() + 0.15,
        line=dict(dash="dash", color="gray"),
        xref="x1", yref="y1"
    )
    vline_annotation = dict(
        x=importance_means[0],
        y=data[sheet_names[0]]['满意度'].max() + 0.15,
        text="重要度均值",
        showarrow=False,
        xref="x1", yref="y1",
        font=dict(size=14, color="#223366")
    )
    hline_shape = dict(
        type="line",
        x0=data[sheet_names[0]]['重要度'].min() - 0.15, x1=data[sheet_names[0]]['重要度'].max() + 0.15,
        y0=0, y1=0,
        line=dict(dash="dash", color="black", width=1),
        xref="x1", yref="y1"
    )
    fig.update_layout(shapes=[vline_shape, hline_shape], annotations=[vline_annotation])
    # 主图坐标轴
    fig.update_xaxes(title_text="重要度", showgrid=True, gridcolor='lightgray', row=1, col=1)
    fig.update_yaxes(title_text="满意度", showgrid=True, gridcolor='lightgray', row=1, col=1)
    # 右侧bar图美化
    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False, row=1, col=2)
    fig.update_yaxes(title_text="", showgrid=False, zeroline=True, zerolinecolor='black', zerolinewidth=1, row=1, col=2, autorange="reversed", showticklabels=False)
    # 下拉菜单
    buttons = []
    for i, sheet_name in enumerate(sheet_names):
        visible = [False] * len(traces)
        if i < len(scatter_indices):
            visible[2*i] = True
        if i < len(bar_indices):
            visible[2*i+1] = True
        # 重新计算vline和hline位置
        cur_df = data[sheet_name].copy()
        cur_df['满意度'] = pd.to_numeric(cur_df['满意度'], errors='coerce').fillna(0)
        cur_df['重要度'] = pd.to_numeric(cur_df['重要度'], errors='coerce').fillna(0)
        vline_shape_i = dict(
            type="line",
            x0=importance_means[i], x1=importance_means[i],
            y0=cur_df['满意度'].min() - 0.15, y1=cur_df['满意度'].max() + 0.15,
            line=dict(dash="dash", color="gray"),
            xref="x1", yref="y1"
        )
        vline_annotation_i = dict(
            x=importance_means[i],
            y=cur_df['满意度'].max() + 0.15,
            text="重要度均值",
            showarrow=False,
            xref="x1", yref="y1",
            font=dict(size=14, color="#223366")
        )
        hline_shape_i = dict(
            type="line",
            x0=cur_df['重要度'].min() - 0.15, x1=cur_df['重要度'].max() + 0.15,
            y0=0, y1=0,
            line=dict(dash="dash", color="black", width=1),
            xref="x1", yref="y1"
        )
        buttons.append(dict(
            label=sheet_name,
            method="update",
            args=[
                {"visible": visible + [True]},
                {"title.text": f"体验点分析仪表板<br><sub>横轴：重要度 | 纵轴：满意度 | 点大小：分歧度 | 点颜色：Top痛点值</sub>",
                 "shapes": [vline_shape_i, hline_shape_i],
                 "annotations": [vline_annotation_i]
                }
            ]
        ))
    fig.update_layout(
        updatemenus=[dict(
            active=0,
            buttons=buttons,
            x=0.01,
            xanchor="left",
            y=1.15,
            yanchor="top"
        )],
        title=dict(
            text="体验点分析仪表板<br><sub>横轴：重要度 | 纵轴：满意度 | 点大小：分歧度 | 点颜色：Top痛点值</sub>",
            x=0.5,
            font=dict(size=18)
        ),
        height=800,
        width=1400,
        plot_bgcolor='white',
        dragmode='pan',
        hovermode='closest',
    )
    
    # 保存HTML文件（如果指定了路径）
    if output_html_path:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
        fig.write_html(output_html_path)
        print(f"\n✅ 可视化已保存到: {output_html_path}")
        
        # 自动在浏览器中打开（如果启用）
        if auto_open_browser:
            try:
                webbrowser.open(f'file://{os.path.abspath(output_html_path)}')
                print("📱 已自动在浏览器中打开")
            except:
                print("请手动在浏览器中打开上述文件")
    
    return fig
