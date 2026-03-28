"""
File Brain Web 界面
使用 Streamlit 构建的交互式前端
"""
import streamlit as st
import os
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import networkx as nx
import plotly.graph_objects as go

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from file_brain import FileBrain

# 初始化 FileBrain
file_brain = FileBrain()

# 页面配置
st.set_page_config(
    page_title="File Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 侧边栏导航
st.sidebar.title("🧠 File Brain")

page = st.sidebar.selectbox(
    "选择功能",
    ["首页", "文件索引", "智能搜索", "文件组织", "知识图谱", "系统统计", "用户反馈"]
)

# 首页
if page == "首页":
    st.title("🧠 File Brain")
    st.markdown("### 本地文件系统智能搜索和管理工具")
    
    st.markdown("\n**功能特性：**")
    st.markdown("- 📄 支持多种文件格式（文本、Office、PDF、HTML、思维导图等）")
    st.markdown("- 🔍 智能搜索（语义搜索、关键词搜索、混合搜索）")
    st.markdown("- 📁 智能文件组织（自动标签提取、智能文件名生成）")
    st.markdown("- 🌐 知识图谱（文件关联分析）")
    st.markdown("- 🔗 第三方服务集成（Notion、Obsidian）")
    st.markdown("- 📡 API 接口")
    
    st.markdown("\n**快速开始：**")
    st.markdown("1. 进入 '文件索引' 页面，添加文件或目录")
    st.markdown("2. 进入 '智能搜索' 页面，搜索文件内容")
    st.markdown("3. 进入 '文件组织' 页面，智能组织文件")
    st.markdown("4. 进入 '知识图谱' 页面，查看文件关联")

# 文件索引页面
elif page == "文件索引":
    st.title("📄 文件索引")
    
    # 索引单个文件
    st.markdown("### 索引单个文件")
    file_path = st.text_input("文件路径")
    if st.button("索引文件"):
        if file_path:
            success = file_brain.add_file(file_path)
            if success:
                st.success(f"文件 {file_path} 已成功索引")
            else:
                st.error("文件索引失败")
        else:
            st.error("请输入文件路径")
    
    # 索引目录
    st.markdown("### 索引目录")
    dir_path = st.text_input("目录路径")
    recursive = st.checkbox("递归索引子目录", value=True)
    if st.button("索引目录"):
        if dir_path:
            stats = file_brain.add_directory(dir_path, recursive=recursive)
            st.success(f"目录索引完成: {stats}")
        else:
            st.error("请输入目录路径")
    
    # 已索引的文件
    st.markdown("### 已索引的文件")
    sources = file_brain.list_sources()
    if sources:
        df = pd.DataFrame(sources, columns=["文件路径"])
        st.dataframe(df)
    else:
        st.info("暂无已索引的文件")
    
    # 清空索引
    if st.button("清空所有索引"):
        success = file_brain.clear_all()
        if success:
            st.success("所有索引已清空")
        else:
            st.error("清空索引失败")

# 智能搜索页面
elif page == "智能搜索":
    st.title("🔍 智能搜索")
    
    # 搜索参数
    query = st.text_input("搜索查询")
    top_k = st.slider("返回结果数量", min_value=1, max_value=20, value=10)
    search_type = st.selectbox(
        "搜索类型",
        ["语义搜索", "关键词搜索", "混合搜索"]
    )
    
    if st.button("搜索"):
        if query:
            with st.spinner("搜索中..."):
                if search_type == "关键词搜索":
                    results = file_brain.keyword_search(query, top_k=top_k)
                elif search_type == "混合搜索":
                    results = file_brain.hybrid_search(query, top_k=top_k)
                else:
                    results = file_brain.search(query, top_k=top_k)
                
                if results:
                    st.success(f"找到 {len(results)} 个结果")
                    for i, result in enumerate(results, 1):
                        with st.expander(f"结果 {i}: {result.title} (相似度: {result.score:.2f})"):
                            st.markdown(f"**文件路径:** {result.source}")
                            st.markdown(f"**文件类型:** {result.file_type}")
                            st.markdown(f"**内容:** {result.content[:300]}...")
                            if result.context:
                                st.markdown(f"**上下文:** {result.context[:200]}...")
                else:
                    st.info("未找到相关结果")
        else:
            st.error("请输入搜索查询")

# 文件组织页面
elif page == "文件组织":
    st.title("📁 智能文件组织")
    
    # 提取标签
    st.markdown("### 提取文件标签")
    tag_file_path = st.text_input("文件路径", key="tag_file")
    tag_top_n = st.slider("标签数量", min_value=1, max_value=20, value=10, key="tag_top_n")
    if st.button("提取标签"):
        if tag_file_path:
            tags = file_brain.extract_tags(tag_file_path, top_n=tag_top_n)
            if tags:
                st.success("标签提取成功")
                st.write(tags)
            else:
                st.info("未能提取标签")
        else:
            st.error("请输入文件路径")
    
    # 生成文件名
    st.markdown("### 生成智能文件名")
    rename_file_path = st.text_input("文件路径", key="rename_file")
    if st.button("生成文件名"):
        if rename_file_path:
            filename = file_brain.generate_filename(rename_file_path)
            st.success(f"生成的文件名: {filename}")
        else:
            st.error("请输入文件路径")
    
    # 智能重命名文件
    st.markdown("### 智能重命名文件")
    rename_file_path = st.text_input("文件路径", key="smart_rename_file")
    if st.button("智能重命名"):
        if rename_file_path:
            new_path = file_brain.rename_file(rename_file_path)
            st.success(f"文件已重命名为: {new_path}")
        else:
            st.error("请输入文件路径")
    
    # 组织目录文件
    st.markdown("### 组织目录文件")
    organize_dir_path = st.text_input("目录路径")
    organize_recursive = st.checkbox("递归处理子目录", value=True)
    if st.button("组织文件"):
        if organize_dir_path:
            stats = file_brain.organize_files(organize_dir_path, recursive=organize_recursive)
            st.success(f"文件组织完成: {stats}")
        else:
            st.error("请输入目录路径")

# 知识图谱页面
elif page == "知识图谱":
    st.title("🌐 知识图谱")
    
    # 知识图谱统计
    stats = file_brain.get_knowledge_graph_stats()
    st.markdown(f"### 知识图谱统计")
    st.markdown(f"- 节点数: {stats['nodes']}")
    st.markdown(f"- 边数: {stats['edges']}")
    st.markdown(f"- 密度: {stats['density']:.4f}")
    
    # 中心文件
    st.markdown("### 中心文件")
    central_files = file_brain.get_central_files(top_k=10)
    if central_files:
        df_central = pd.DataFrame(central_files)
        st.dataframe(df_central)
    else:
        st.info("知识图谱为空")
    
    # 相关文件
    st.markdown("### 相关文件")
    related_file_path = st.text_input("文件路径")
    related_top_k = st.slider("相关文件数量", min_value=1, max_value=20, value=5)
    if st.button("查找相关文件"):
        if related_file_path:
            related_files = file_brain.get_related_files(related_file_path, top_k=related_top_k)
            if related_files:
                df_related = pd.DataFrame(related_files)
                st.dataframe(df_related)
            else:
                st.info("未找到相关文件")
        else:
            st.error("请输入文件路径")
    
    # 知识图谱可视化
    st.markdown("### 知识图谱可视化")
    if st.button("生成知识图谱"):
        with st.spinner("生成中..."):
            graph_data = file_brain.get_knowledge_graph()
            if graph_data['nodes'] and graph_data['edges']:
                # 创建 NetworkX 图
                G = nx.Graph()
                
                # 添加节点
                for node in graph_data['nodes']:
                    G.add_node(node['id'], title=node.get('title', node['id']))
                
                # 添加边
                for edge in graph_data['edges']:
                    G.add_edge(edge['source'], edge['target'], weight=edge.get('weight', 1))
                
                # 使用 Plotly 可视化
                pos = nx.spring_layout(G, seed=42)
                
                edge_x = []
                edge_y = []
                for edge in G.edges():
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    edge_x.append(x0)
                    edge_x.append(x1)
                    edge_x.append(None)
                    edge_y.append(y0)
                    edge_y.append(y1)
                    edge_y.append(None)
                
                edge_trace = go.Scatter(
                    x=edge_x,
                    y=edge_y,
                    line=dict(width=0.5, color='#888'),
                    hoverinfo='none',
                    mode='lines'
                )
                
                node_x = []
                node_y = []
                node_text = []
                for node in G.nodes():
                    x, y = pos[node]
                    node_x.append(x)
                    node_y.append(y)
                    node_text.append(G.nodes[node]['title'])
                
                node_trace = go.Scatter(
                    x=node_x,
                    y=node_y,
                    mode='markers',
                    hoverinfo='text',
                    marker=dict(
                        showscale=True,
                        colorscale='YlGnBu',
                        size=10,
                        colorbar=dict(
                            thickness=15,
                            title='Node Connections',
                            xanchor='left',
                            titleside='right'
                        )
                    )
                )
                
                node_trace.text = node_text
                
                fig = go.Figure(data=[edge_trace, node_trace],
                             layout=go.Layout(
                                title='File Brain 知识图谱',
                                titlefont_size=16,
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=20,l=5,r=5,t=40),
                                annotations=[ dict(
                                    text="知识图谱可视化",
                                    showarrow=False,
                                    xref="paper", yref="paper"
                                ) ],
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("知识图谱为空")

# 系统统计页面
elif page == "系统统计":
    st.title("📊 系统统计")
    
    # 基本统计
    stats = file_brain.get_stats()
    st.markdown("### 基本统计")
    st.markdown(f"- 总文档数: {stats['total_documents']}")
    st.markdown(f"- 集合名称: {stats['collection_name']}")
    st.markdown(f"- 嵌入模型: {stats['embedding_model']}")
    st.markdown(f"- 模型类型: {stats['model_type']}")
    
    # 已索引的文件类型
    st.markdown("### 文件类型分布")
    sources = file_brain.list_sources()
    if sources:
        file_types = []
        for source in sources:
            ext = Path(source).suffix.lower()
            file_types.append(ext if ext else "无扩展名")
        
        df_types = pd.DataFrame(file_types, columns=["文件类型"])
        type_counts = df_types['文件类型'].value_counts()
        
        fig = px.bar(
            x=type_counts.index,
            y=type_counts.values,
            labels={"x": "文件类型", "y": "数量"},
            title="文件类型分布"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无已索引的文件")
    
    # AI 状态
    st.markdown("### AI 状态")
    try:
        ai_status = file_brain.get_ai_status()
        st.markdown(f"- AI 状态: {ai_status['status']}")
        st.markdown(f"- 模型: {ai_status.get('model', 'N/A')}")
    except Exception as e:
        st.info("AI 功能未启用")

# 用户反馈页面
elif page == "用户反馈":
    st.title("📝 用户反馈")
    
    st.markdown("### 反馈表单")
    
    # 反馈类型
    feedback_type = st.selectbox(
        "反馈类型",
        ["功能建议", "Bug 报告", "使用问题", "其他"]
    )
    
    # 反馈内容
    feedback_content = st.text_area("反馈内容", height=200)
    
    # 联系方式（可选）
    contact_info = st.text_input("联系方式（可选）", placeholder="邮箱或其他联系方式")
    
    # 提交按钮
    if st.button("提交反馈"):
        if feedback_content:
            # 保存反馈到文件
            feedback_dir = Path(__file__).parent.parent / "feedback"
            feedback_dir.mkdir(exist_ok=True)
            
            import datetime
            import json
            
            feedback_data = {
                "type": feedback_type,
                "content": feedback_content,
                "contact": contact_info,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            feedback_file = feedback_dir / f"feedback_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedback_data, f, ensure_ascii=False, indent=2)
            
            st.success("反馈提交成功！感谢您的反馈，我们会认真处理。")
        else:
            st.error("请填写反馈内容")
    
    # 反馈历史（仅管理员可见）
    st.markdown("### 反馈历史")
    feedback_dir = Path(__file__).parent.parent / "feedback"
    if feedback_dir.exists():
        feedback_files = list(feedback_dir.glob("*.json"))
        if feedback_files:
            feedback_files.sort(reverse=True, key=lambda x: x.stat().st_mtime)
            
            for feedback_file in feedback_files[:10]:  # 只显示最近10条
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    feedback_data = json.load(f)
                
                with st.expander(f"{feedback_data['timestamp']} - {feedback_data['type']}"):
                    st.markdown(f"**反馈类型:** {feedback_data['type']}")
                    st.markdown(f"**反馈内容:** {feedback_data['content']}")
                    if feedback_data.get('contact'):
                        st.markdown(f"**联系方式:** {feedback_data['contact']}")
        else:
            st.info("暂无反馈记录")
    else:
        st.info("暂无反馈记录")

# 页脚
st.sidebar.markdown("---")
st.sidebar.markdown("© 2026 File Brain")
st.sidebar.markdown("智能文件管理工具")