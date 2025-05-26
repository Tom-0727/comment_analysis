import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os



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
    
    # 创建2x2子图仪表板
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=sheet_names,
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    for i, sheet_name in enumerate(sheet_names):
        if sheet_name not in data:
            continue
            
        df = data[sheet_name].copy()
        
        # 计算位置
        row = i // 2 + 1
        col = i % 2 + 1
        
        # 处理数据
        df['分歧度'] = pd.to_numeric(df['分歧度'], errors='coerce').fillna(0)
        df['Top痛点_数值'] = pd.to_numeric(df['Top痛点'], errors='coerce').fillna(0)
        
        # 确保分歧度不小于0
        df['分歧度'] = df['分歧度'].clip(lower=0)
        
        # 优化点大小计算 - 使用归一化和平方根缩放
        if df['分歧度'].max() > 0:
            # 归一化到0-1范围
            df['分歧度_归一化'] = (df['分歧度'] - df['分歧度'].min()) / (df['分歧度'].max() - df['分歧度'].min())
            # 使用平方根缩放，让大小变化更平缓，范围控制在5-25之间
            df['分歧度_显示'] = 5 + (df['分歧度_归一化'] ** 0.5) * 20
        else:
            df['分歧度_显示'] = 10  # 如果所有分歧度都是0，设置固定大小
        
        # 计算重要度均值
        importance_mean = df['重要度'].mean()
        
        # 添加散点
        fig.add_trace(
            go.Scatter(
                x=df['重要度'],
                y=df['满意度'],
                mode='markers',
                marker=dict(
                    size=df['分歧度_显示'],
                    color=df['Top痛点_数值'],
                    colorscale='RdYlBu_r',
                    opacity=0.8,
                    line=dict(width=1, color='black'),
                    showscale=(i == 0),  # 只在第一个子图显示颜色条
                    colorbar=dict(title="Top痛点值", x=1.02) if i == 0 else None
                ),
                text=df['体验点'],
                hovertemplate=
                    "<b>%{text}</b><br>" +
                    "重要度: %{x:.3f}<br>" +
                    "满意度: %{y:.3f}<br>" +
                    "分歧度: " + df['分歧度'].round(3).astype(str) + "<br>" +
                    "Top痛点: " + df['Top痛点_数值'].round(3).astype(str) + "<br>" +
                    "<extra></extra>",
                name=f'{sheet_name}',
                showlegend=False
            ),
            row=row, col=col
        )
        
        # 添加分界线
        fig.add_vline(
            x=importance_mean, 
            line_dash="dash", 
            line_color="gray",
            row=row, col=col
        )
        
        fig.add_hline(
            y=0, 
            line_dash="dash", 
            line_color="gray",
            row=row, col=col
        )
    
    # 更新布局
    fig.update_layout(
        title=dict(
            text="体验点分析仪表板<br><sub>横轴：重要度 | 纵轴：满意度 | 点大小：分歧度 | 点颜色：Top痛点值</sub>",
            x=0.5,
            font=dict(size=18)
        ),
        height=800,
        width=1400,
        showlegend=False,
        plot_bgcolor='white'
    )
    
    # 更新所有子图的坐标轴
    fig.update_xaxes(title_text="重要度", showgrid=True, gridcolor='lightgray')
    fig.update_yaxes(title_text="满意度", showgrid=True, gridcolor='lightgray')
    
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
