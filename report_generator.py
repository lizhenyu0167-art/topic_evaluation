from search_functions import calculate_research_score
import os

def generate_star_display(score):
    """
    生成星星显示，共5颗星，前X颗为黄色★，后(5-X)颗为灰色☆
    
    Args:
        score: 得分值
        
    Returns:
        str: 星星显示字符串
    """
    rounded_score = round(score)
    # 确保得分在0-5范围内
    rounded_score = max(0, min(5, rounded_score))
    
    yellow_stars = "★" * rounded_score
    gray_stars = "☆" * (5 - rounded_score)
    
    return yellow_stars + gray_stars

def generate_literature_table(journal_docs):
    """
    生成相关文献表格的Markdown内容
    
    Args:
        journal_docs: 文献数据列表
        
    Returns:
        str: 生成的Markdown表格内容
    """
    table_content = "相关文献列表：\n\n"
    table_content += "| 篇名 | 关键词 | 来源期刊 | 期刊等级 |\n"
    table_content += "|------|--------|----------|----------|\n"
    
    for doc in journal_docs[:10]:
        # 获取并处理字段，确保转义分隔符和特殊字符
        title = doc.get('title', '').replace('|', '\\|').replace('\n', ' ')
        url = doc.get('url', '')
        keywords = doc.get('keywords', [])
        if isinstance(keywords, list):
            keywords = ','.join(keywords)
        
        # 处理关键词中的逗号，只保留分号作为分隔符
        if isinstance(keywords, str):
            # 将逗号替换为空字符串，保留分号
            keywords = keywords.replace(',', '')
        
        keywords = keywords.replace('|', '\\|').replace('\n', ' ')
        # 使用source字段作为来源期刊
        journal = doc.get('source', '').replace('|', '\\|').replace('\n', ' ')
        # 使用journallevel字段作为期刊等级
        journal_level = doc.get('journallevel', '').replace('|', '\\|').replace('\n', ' ')
        
        # 处理标题超链接
        if url:
            # 转义标题中的特殊字符，避免Markdown语法冲突
            title = title.replace('[', '\\[').replace(']', '\\]')
            title = title.replace('(', '\\(').replace(')', '\\)')
            # 转义URL中的特殊字符
            url = url.replace('(', '%28').replace(')', '%29')
            title_link = f"[{title}]({url})"
        else:
            title_link = title
            
        table_content += f"| {title_link} | {keywords} | {journal} | {journal_level} |\n"
    
    return table_content

def generate_cfp_table(journal_docs):
    """
    生成相关征稿启事表格的Markdown内容
    
    Args:
        journal_docs: 征稿启事数据列表
        
    Returns:
        str: 生成的Markdown表格内容
    """
    table_content = "相关征稿启事列表：\n\n"
    table_content += "| 征稿启事 | 热点选题 | 来源期刊 |\n"
    table_content += "|------|--------|----------|\n"
    
    for doc in journal_docs[:3]:
        # 获取并处理字段，确保转义分隔符和特殊字符
        call_for_papers_title = doc.get('call_for_papers_title', '').replace('|', '\\|').replace('\n', ' ')
        url = doc.get('url', '')
        # 使用source字段作为来源期刊
        journal_name = doc.get('journal_name', '').replace('|', '\\|').replace('\n', ' ')
        # 使用hot_topics字段作为热点选题
        hot_topics = doc.get('hot_topics', '').replace('|', '\\|').replace('\n', ' ')
        
        # 处理标题超链接
        if url:
            # 转义标题中的特殊字符，避免Markdown语法冲突
            call_for_papers_title = call_for_papers_title.replace('[', '\\[').replace(']', '\\]')
            call_for_papers_title = call_for_papers_title.replace('(', '\\(').replace(')', '\\)')
            # 转义URL中的特殊字符
            url = url.replace('(', '%28').replace(')', '%29')
            title_link = f"[{call_for_papers_title}]({url})"
        else:
            title_link = call_for_papers_title
            
        table_content += f"| {title_link} | {hot_topics} | {journal_name} |\n"
    
    return table_content

def generate_skjj_table(journal_docs):
    """
    生成相关SKJJ项目表格的Markdown内容
    
    Args:   
        journal_docs: SKJJ项目数据列表
        
    Returns:
        str: 生成的Markdown表格内容
    """
    table_content = "相关SKJJ项目列表：\n\n"
    table_content += "| 2025年国家社科基金重大项目招标选题 |\n"
    table_content += "|------|\n"
    
    for doc in journal_docs[:5]:
        # 获取并处理字段，确保转义分隔符和特殊字符
        # 使用topic_name字段作为项目名称
        topic_name = doc.get('topic_name', '').replace('|', '\\|').replace('\n', ' ')
        
        table_content += f"| {topic_name} |\n"
    
    return table_content

def generate_dataset_table(journal_docs):
    """
    生成相关数据集表格的Markdown内容
    
    Args:
        journal_docs: 数据集数据列表
        
    Returns:
        str: 生成的Markdown表格内容
    """
    table_content = "相关数据集列表：\n\n"
    table_content += "| 数据集名称 | 相关指标 |\n"
    table_content += "|------|--------|\n"
    
    for doc in journal_docs[:3]:
        # 获取并处理字段，确保转义分隔符和特殊字符
        dataset_name = doc.get('name', '').replace('|', '\\|').replace('\n', ' ')
        url = doc.get('url', '')
        # 相关指标
        indicators = doc.get('indicators', [])
        if isinstance(indicators, list):
            # 去除每个indicator外面的引号
            indicators = [indicator.strip('"') for indicator in indicators]
            indicators = '，'.join(indicators)
        else:
            # 处理字符串类型的indicators
            # 先检查是否是字符串类型
            if isinstance(indicators, str):
                # 将字符串按逗号分割成列表，然后去除每个元素的引号
                indicators_list = indicators.split(',')
                indicators_list = [indicator.strip().strip('"') for indicator in indicators_list]
                indicators = '，'.join(indicators_list)
        indicators = indicators.replace('|', '\\|').replace('\n', ' ')
        
        # 处理数据集名称超链接
        if url:
            # 转义数据集名称中的特殊字符，避免Markdown语法冲突
            dataset_name = dataset_name.replace('[', '\\[').replace(']', '\\]')
            dataset_name = dataset_name.replace('(', '\\(').replace(')', '\\)')
            # 转义URL中的特殊字符
            url = url.replace('(', '%28').replace(')', '%29')
            dataset_name_link = f"[{dataset_name}]({url})"
        else:
            dataset_name_link = dataset_name
            
        table_content += f"| {dataset_name_link} | {indicators} |\n"
    
    return table_content

def generate_research_report(paper_topic, variable_settings, empirical_model="", output_file=None):
    """
    生成论文选题评估报告
    
    Args:
        paper_topic: 论文选题
        variable_settings: 变量设置
        empirical_model: 实证模型
        output_file: 输出文件路径，默认为"论文选题评估结果.md"
    
    Returns:
        str: 生成的报告文件路径
    """
    # 如果未指定输出文件，使用默认文件名
    if output_file is None:
        output_file = os.path.join(os.path.dirname(__file__), "论文选题评估结果.md")
    
    # 运行calculate_research_score获取评分结果
    score_results = calculate_research_score(paper_topic, variable_settings, empirical_model)
    
    # 提取各项得分和评分理由
    # 总分为所有维度得分的平均值
    total_score = score_results.get("total_score", 0)
    total_score_stars = generate_star_display(total_score)
    
    # 价值性分析 - 价值性得分
    value_score = score_results.get("value_score", 0)
    value_score_stars = generate_star_display(value_score)

    # 价值性分析 - 文件支撑性
    skjj_score = score_results.get("skjj_score", 0)
    skjj_score_stars = generate_star_display(skjj_score)
    skjj_analysis = score_results.get("skjj_analysis", "未能获取文件支撑性分析")

    # 价值性分析 - 征稿启事参考性
    cfp_reference_score = score_results.get("cfp_reference_score", 0)
    cfp_reference_score_stars = generate_star_display(cfp_reference_score)
    cfp_analysis = score_results.get("cfp_analysis", "未能获取征稿启事参考性分析")

    # 价值性分析 - 政策参考性
    policy_reference_score = score_results.get("policy_reference_score", 0)
    policy_reference_score_stars = generate_star_display(policy_reference_score)
    policy_reference_reason = score_results.get("policy_reference_reason", "未能获取评分理由")
    
    # 价值性分析 - 实践解决性
    practical_solution_score = score_results.get("practical_solution_score", 0)
    practical_solution_score_stars = generate_star_display(practical_solution_score)
    practical_solution_reason = score_results.get("practical_solution_reason", "未能获取评分理由")
    
    # 创新性分析 - 创新性得分
    innovation_score = score_results.get("innovation_score", 0)
    innovation_score_stars = generate_star_display(innovation_score)

    # 创新性分析 - 理论创新
    theoretical_innovation_total_score = score_results.get("theoretical_innovation_total_score", 0)
    theoretical_innovation_total_score_stars = generate_star_display(theoretical_innovation_total_score)

    # 创新性分析 - 理论创新可能性
    theoretical_innovation_score = score_results.get("theoretical_innovation_score", 0)
    theoretical_innovation_score_stars = generate_star_display(theoretical_innovation_score)
    theoretical_innovation_possibility_reason = score_results.get("theoretical_innovation_reason", "未能获取评分理由")

    # 创新性分析 - 研究视角创新性
    research_perspective_score = score_results.get("research_perspective_score", 0)
    research_perspective_score_stars = generate_star_display(research_perspective_score)
    research_perspective_innovation_analysis = score_results.get("research_perspective_innovation_analysis", "未能获取评分理由")
    
    # 获取相关文献列表
    journal_docs = score_results.get("journal_results", [])
    journal_model_docs = score_results.get("journal_model_results", [])
    dataset_docs = score_results.get("dataset_results", [])
    cfp_docs = score_results.get("cfp_results", [])
    skjj_docs = score_results.get("skjj_results", [])

    
    # 生成相关文献表格
    table_content_journal = generate_literature_table(journal_docs)
    table_content_journal_model = generate_literature_table(journal_model_docs)
    table_content_cfp = generate_cfp_table(cfp_docs)
    table_content_skjj = generate_skjj_table(skjj_docs)
    table_content_dataset = generate_dataset_table(dataset_docs)
    
    # 创新性分析 - 模型创新性
    model_innovation_score = score_results.get("model_innovation_score", 0)
    model_innovation_score_stars = generate_star_display(model_innovation_score)
    model_innovation_analysis = score_results.get("model_innovation_analysis", "未能获取评分理由")

    # 创新性分析 - 数据创新性
    data_innovation_score = score_results.get("data_innovation_score", 0)
    data_innovation_score_stars = generate_star_display(data_innovation_score)
    data_innovation_analysis = score_results.get("data_innovation_analysis", "未能获取评分理由")

    # 可行性分析 - 可行性得分
    feasibility_score = score_results.get("feasibility_score", 0)
    feasibility_score_stars = generate_star_display(feasibility_score)

    # 可行性分析 - 数据可得性
    data_availability_score = score_results.get("data_availability_score", 0)
    data_availability_score_stars = generate_star_display(data_availability_score)
    data_availability_analysis = score_results.get("data_availability_analysis", "未能获取评分理由")

    # 可行性分析 - 实证模型可行性
    empirical_model_score = score_results.get("empirical_model_feasibility_score", 0)
    empirical_model_score_stars = generate_star_display(empirical_model_score)
    empirical_model_reason = score_results.get("empirical_model_feasibility_reason", "未能获取评分理由")

    # 生成Markdown报告内容
    report_content = f"""
 # 论文选题评估报告
 ## 论文标题：{paper_topic}
 ## 总分：{total_score_stars}
 
 ## 论文价值性得分：{value_score_stars}
 ### 文件支撑性：{skjj_score_stars}
 {skjj_analysis}
 {table_content_skjj}

 ### 征稿启事参考性：{cfp_reference_score_stars}
 {cfp_analysis}
 {table_content_cfp}

 ### 政策参考性：{policy_reference_score_stars}
 {policy_reference_reason}

 ### 实践解决性：{practical_solution_score_stars}
 {practical_solution_reason}
 
 ## 论文创新性得分：{innovation_score_stars}
 ### 理论创新：{theoretical_innovation_total_score_stars}
 #### 理论创新可能性：{theoretical_innovation_score_stars}
 {theoretical_innovation_possibility_reason}
 
 #### 研究视角创新性：{research_perspective_score_stars}
 {research_perspective_innovation_analysis}
 {table_content_journal}
 
 ### 模型创新性：{model_innovation_score_stars}
 {model_innovation_analysis}
 {table_content_journal_model}
 
 ### 数据创新性：{data_innovation_score_stars}
 {data_innovation_analysis}
 
 ## 论文可行性得分：{feasibility_score_stars}
 
 ### 数据可得性：{data_availability_score_stars}
 {data_availability_analysis}
 {table_content_dataset}
 
 ### 实证模型可行性：{empirical_model_score_stars}
 {empirical_model_reason}
"""

    # 写入报告文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"评估报告已生成: {output_file}")
    return output_file

if __name__ == "__main__":
    # 示例用法
    paper_topic = "新质生产力对碳排放的影响路经分析"
    variable_settings = "新质生产力、碳排放、教育发展水平、经济发展水平、外商投资水平、产业聚集度、城镇化水平"
    empirical_model = "空间计量模型"
    # paper_topic = "企业人工智能水平对数字化转型的影响分析"
    # variable_settings = "人工智能、数字化转型、人工智能创新发展试验区、净资产收益率、托宾Q、企业规模、研发强度、股权集中度"
    # empirical_model = "双重差分模型"
    
    generate_research_report(paper_topic, variable_settings, empirical_model)