from vector_search_core import TextVectorizer, VectorSearchClient, ResultProcessor, APIConfig
import json
import os
import requests

# 内部配置参数
class SearchConfig:
    # 检索结果数量配置
    MAX_JOURNAL_RESULTS = 60  # 期刊检索最大返回结果数
    MAX_DATASET_RESULTS = 50   # 数据集检索最大返回结果数
    MAX_CFP_RESULTS = 50       # CFP检索最大返回结果数
    MAX_SKJJ_RESULTS = 50      # skjj检索最大返回结果数
    
    # 检索分数阈值配置
    JOURNAL_MAX_SCORE = 0.35    # 期刊检索最大score值
    DATASET_MAX_SCORE = 0.55   # 数据集检索最大score值
    CFP_MAX_SCORE = 0.5        # CFP检索最大score值
    SKJJ_MAX_SCORE = 0.52       # skjj检索最大score值

def search_vector_by_text(paper_topic, empirical_model=""):
    """根据文本执行向量检索
    
    Args:
        paper_topic: 论文选题
        empirical_model: 实证模型，默认为空字符串
        
    Returns:
        tuple: (filtered_count, filtered_docs)
            - filtered_count: 筛选后的记录数量
            - filtered_docs: 筛选后的记录内容列表
    """
    # 使用配置类获取API密钥
    dashscope_api_key = APIConfig.DASHSCOPE_API_KEY
    dashvector_api_key = APIConfig.DASHVECTOR_API_KEY
    cluster_endpoint = APIConfig.CLUSTER_ENDPOINT
    
    # 初始化文本向量转换器
    vectorizer = TextVectorizer(api_key=dashscope_api_key)
    
    # 拼接paper_topic和empirical_model
    query_text = paper_topic
    if empirical_model:
        query_text = f"{paper_topic}；{empirical_model}"
    
    # 将查询文本转换为向量
    query_vector = vectorizer.text_to_vector(query_text)
    if not query_vector:
        print("向量转换失败，无法执行检索")
        return 0, []
    
    print(f"成功将文本 '{query_text}' 转换为向量-search_vector_by_text")
    
    # 初始化向量检索客户端
    search_client = VectorSearchClient(api_key=dashvector_api_key, endpoint=cluster_endpoint)
    
    # 获取集群和collection
    cluster_name = APIConfig.CLUSTER_NAME
    collection_name = APIConfig.JOURNAL_COLLECTION
    
    if not search_client.get_cluster(cluster_name):
        return 0, []
        
    if not search_client.get_collection(collection_name):
        return 0, []
    
    # 执行向量检索
    collection_name = APIConfig.JOURNAL_COLLECTION
    output_fields = APIConfig.get_output_fields(collection_name)
    results = search_client.search(
        query_vector=query_vector,
        topk=SearchConfig.MAX_JOURNAL_RESULTS,
        output_fields=output_fields,
        include_vector=False
    )
    
    if not results:
        print(f"未找到与 '{paper_topic}' 相关的结果")
        return 0, []
    
    # 处理检索结果
    processor = ResultProcessor()
    filtered_results = processor.filter_results_by_score(results, SearchConfig.JOURNAL_MAX_SCORE)
    
    # 返回筛选后的记录数量和记录内容
    filtered_count = len(filtered_results)
    
    print(f"筛选出 {filtered_count} 条score值小于等于{SearchConfig.JOURNAL_MAX_SCORE}的记录")
    if filtered_count > 0:
        print(f"筛选出的记录内容第一条: {filtered_results[0]}")
    return filtered_count, filtered_results


def search_vector_from_cfp(paper_topic):
    """从CFP_v2集合中根据文本执行向量检索
    
    Args:
        paper_topic: 论文选题
        
    Returns:
        tuple: (filtered_count, filtered_docs)
            - filtered_count: 筛选后的记录数量
            - filtered_docs: 筛选后的记录内容列表
    """
    # 使用配置类获取API密钥
    dashscope_api_key = APIConfig.DASHSCOPE_API_KEY
    dashvector_api_key = APIConfig.DASHVECTOR_API_KEY
    cluster_endpoint = APIConfig.CLUSTER_ENDPOINT
    
    # 初始化文本向量转换器
    vectorizer = TextVectorizer(api_key=dashscope_api_key)
    
    # 将查询文本转换为向量
    query_vector = vectorizer.text_to_vector(paper_topic)
    if not query_vector:
        print("向量转换失败，无法执行检索")
        return 0, []
    
    print(f"成功将文本 '{paper_topic}' 转换为向量-search_vector_from_cfp")
    
    # 初始化向量检索客户端
    search_client = VectorSearchClient(api_key=dashvector_api_key, endpoint=cluster_endpoint)
    
    # 获取集群和collection
    cluster_name = APIConfig.CLUSTER_NAME
    collection_name = APIConfig.CFP_COLLECTION
    
    if not search_client.get_cluster(cluster_name):
        return 0, []
        
    if not search_client.get_collection(collection_name):
        return 0, []
    
    # 执行向量检索
    collection_name = APIConfig.CFP_COLLECTION
    output_fields = APIConfig.get_output_fields(collection_name)
    results = search_client.search(
        query_vector=query_vector,
        topk=SearchConfig.MAX_CFP_RESULTS,
        output_fields=output_fields,
        include_vector=False
    )
    
    if not results:
        print(f"未找到与 '{paper_topic}' 相关的结果")
        return 0, []
    
    # 处理检索结果
    processor = ResultProcessor()
    filtered_results = processor.filter_results_by_score(results, SearchConfig.CFP_MAX_SCORE)
    
    # 返回筛选后的记录数量和记录内容
    filtered_count = len(filtered_results)
    
    print(f"从CFP_v2集合中筛选出 {filtered_count} 条score值小于等于{SearchConfig.CFP_MAX_SCORE}的记录")
    if filtered_count > 0:
        print(f"筛选出的记录内容第一条: {filtered_results[0]}")
    return filtered_count, filtered_results


def search_vector_from_dataset(variable_settings):
    """从dataset_v4集合中执行向量检索
    
    支持按"、"分隔多个关键词，分别执行检索并合并结果
    
    Args:
        variable_settings: 变量设置，支持按"、"分隔多个关键词
        
    Returns:
        tuple: (filtered_count, filtered_docs, keyword_counts)
            - filtered_count: 筛选后的记录数量
            - filtered_docs: 筛选后的记录内容列表（每条记录包含url字段）
            - keyword_counts: 每个关键词匹配的结果数量字典
    """
    try:
        # 参数检查
        if not variable_settings or not isinstance(variable_settings, str):
            print("变量设置无效")
            return 0, [], {}
            
        # 初始化向量转换器和检索客户端
        try:
            vectorizer = TextVectorizer(api_key=APIConfig.DASHSCOPE_API_KEY)
            search_client = VectorSearchClient(api_key=APIConfig.DASHVECTOR_API_KEY, endpoint=APIConfig.CLUSTER_ENDPOINT)
            
            # 检查集合是否存在
            collection_name = APIConfig.DATASET_COLLECTION
            if not search_client.get_collection(collection_name):
                print(f"集合 {collection_name} 不存在")
                return 0, [], {}
                
            # 拆分关键词
            keywords = [kw.strip() for kw in variable_settings.split("、") if kw.strip()]
            if not keywords:
                print("未提供有效的关键词")
                return 0, [], {}
                
            print(f"从变量设置中提取的关键词: {keywords}")
            
            # 存储所有检索结果和每个关键词的匹配数量
            all_results = []
            keyword_counts = {}
            
            # 对每个关键词执行检索
            for keyword in keywords:
                print(f"\n检索关键词: {keyword}")
                
                # 将关键词转换为向量
                query_vector = vectorizer.text_to_vector(keyword)
                if not query_vector:
                    print(f"关键词 '{keyword}' 向量转换失败，跳过")
                    keyword_counts[keyword] = 0
                    continue
                
                # 执行向量检索
                output_fields = APIConfig.get_output_fields(collection_name)
                results = search_client.search(
                    query_vector=query_vector,
                    topk=SearchConfig.MAX_DATASET_RESULTS,
                    output_fields=output_fields,
                    include_vector=False
                )
                
                if not results:
                    print(f"未找到与关键词 '{keyword}' 相关的结果")
                    keyword_counts[keyword] = 0
                    continue
                
                # 处理检索结果
                processor = ResultProcessor()
                filtered_results = processor.filter_results_by_score(results, SearchConfig.DATASET_MAX_SCORE)
                
                # 记录该关键词的匹配数量
                keyword_counts[keyword] = len(filtered_results)
                print(f"关键词 '{keyword}' 匹配到 {len(filtered_results)} 条记录")
                
                # 将结果添加到总结果列表中
                all_results.extend(filtered_results)
            
            # 去重（根据url字段）
            unique_results = []
            seen_urls = set()
            for result in all_results:
                url = result.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
            
            filtered_count = len(unique_results)
            print(f"\n总共找到 {filtered_count} 条不重复的数据集记录")
            
            return filtered_count, unique_results, keyword_counts
            
        except Exception as e:
            print(f"执行向量检索时发生异常: {str(e)}")
            return 0, [], {}
            
    except Exception as e:
        print(f"search_vector_from_dataset函数发生异常: {str(e)}")
        return 0, [], {}


def search_vector_from_skjj(paper_topic):
    """从SKJJ集合中根据文本执行向量检索
    
    Args:
        paper_topic: 论文选题
        
    Returns:
        tuple: (filtered_count, filtered_docs)
            - filtered_count: 筛选后的记录数量
            - filtered_docs: 筛选后的记录内容列表
    """
    # 使用配置类获取API密钥
    dashscope_api_key = APIConfig.DASHSCOPE_API_KEY
    dashvector_api_key = APIConfig.DASHVECTOR_API_KEY
    cluster_endpoint = APIConfig.CLUSTER_ENDPOINT
    
    # 初始化文本向量转换器
    vectorizer = TextVectorizer(api_key=dashscope_api_key)
    
    # 将查询文本转换为向量
    query_vector = vectorizer.text_to_vector(paper_topic)
    if not query_vector:
        print("向量转换失败，无法执行检索")
        return 0, []
    
    print(f"成功将文本 '{paper_topic}' 转换为向量-search_vector_from_skjj")
    
    # 初始化向量检索客户端
    search_client = VectorSearchClient(api_key=dashvector_api_key, endpoint=cluster_endpoint)
    
    # 获取集群和collection
    cluster_name = APIConfig.CLUSTER_NAME
    collection_name = APIConfig.SKJJ_COLLECTION
    
    if not search_client.get_cluster(cluster_name):
        return 0, []
        
    if not search_client.get_collection(collection_name):
        return 0, []
    
    # 执行向量检索
    collection_name = APIConfig.SKJJ_COLLECTION
    output_fields = APIConfig.get_output_fields(collection_name)
    results = search_client.search(
        query_vector=query_vector,
        topk=SearchConfig.MAX_SKJJ_RESULTS,
        output_fields=output_fields,
        include_vector=False
    )
    
    if not results:
        print(f"未找到与 '{paper_topic}' 相关的结果")
        return 0, []
    
    # 处理检索结果
    processor = ResultProcessor()
    filtered_results = processor.filter_results_by_score(results, SearchConfig.SKJJ_MAX_SCORE)
    
    # 返回筛选后的记录数量和记录内容
    filtered_count = len(filtered_results)
    
    print(f"从SKJJ集合中筛选出 {filtered_count} 条score值小于等于{SearchConfig.SKJJ_MAX_SCORE}的记录")
    if filtered_count > 0:
        print(f"筛选出的记录内容第一条: {filtered_results[0]}")
    return filtered_count, filtered_results


def search_vector_by_model(paper_topic, empirical_model):
    """根据论文选题和实证模型执行向量检索
    
    Args:
        paper_topic: 论文选题
        empirical_model: 实证模型
        
    Returns:
        tuple: (filtered_count, filtered_docs)
            - filtered_count: 筛选后的记录数量
            - filtered_docs: 筛选后的记录内容列表
    """
    # 使用配置类获取API密钥
    dashscope_api_key = APIConfig.DASHSCOPE_API_KEY
    dashvector_api_key = APIConfig.DASHVECTOR_API_KEY
    cluster_endpoint = APIConfig.CLUSTER_ENDPOINT
    
    # 初始化文本向量转换器
    vectorizer = TextVectorizer(api_key=dashscope_api_key)
    
    # 拼接paper_topic和empirical_model
    query_text = f"{paper_topic}；{empirical_model}"
    
    # 将查询文本转换为向量
    query_vector = vectorizer.text_to_vector(query_text)
    if not query_vector:
        print("向量转换失败，无法执行检索")
        return 0, []
    
    print(f"成功将文本 '{query_text}' 转换为向量-search_vector_by_model")
    
    # 初始化向量检索客户端
    search_client = VectorSearchClient(api_key=dashvector_api_key, endpoint=cluster_endpoint)
    
    # 获取集群和collection
    cluster_name = APIConfig.CLUSTER_NAME
    collection_name = APIConfig.JOURNAL_COLLECTION
    
    if not search_client.get_cluster(cluster_name):
        return 0, []
        
    if not search_client.get_collection(collection_name):
        return 0, []
    
    # 执行向量检索
    collection_name = APIConfig.JOURNAL_COLLECTION
    output_fields = APIConfig.get_output_fields(collection_name)
    results = search_client.search(
        query_vector=query_vector,
        topk=SearchConfig.MAX_JOURNAL_RESULTS,
        output_fields=output_fields,
        include_vector=False
    )
    
    if not results:
        print(f"未找到与 '{query_text}' 相关的结果")
        return 0, []
    
    # 处理检索结果
    processor = ResultProcessor()
    filtered_results = processor.filter_results_by_score(results, SearchConfig.JOURNAL_MAX_SCORE)
    
    # 返回筛选后的记录数量和记录内容
    filtered_count = len(filtered_results)
    
    print(f"筛选出 {filtered_count} 条score值小于等于{SearchConfig.JOURNAL_MAX_SCORE}的记录")
    if filtered_count > 0:
        print(f"筛选出的记录内容第一条: {filtered_results[0]}")
    return filtered_count, filtered_results


def load_prompts():
    """加载评估提示词
    
    Returns:
        dict: 评估提示词字典
    """
    try:
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建提示词文件路径
        prompts_file = os.path.join(current_dir, "evaluation_prompts.json")
        
        # 检查文件是否存在
        if not os.path.exists(prompts_file):
            print(f"提示词文件不存在: {prompts_file}")
            return {}
            
        # 读取提示词文件
        with open(prompts_file, "r", encoding="utf-8") as f:
            prompts = json.load(f)
            
        return prompts
    except Exception as e:
        print(f"加载提示词文件时发生异常: {str(e)}")
        return {}


def calculate_research_score(paper_topic, variable_settings, empirical_model=""):
    """计算论文选题评估得分
    
    Args:
        paper_topic: 论文选题
        variable_settings: 变量设置
        empirical_model: 实证模型，默认为空字符串
        
    Returns:
        dict: 评估得分和分析结果
    """
    # 加载评估提示词
    prompts = load_prompts()
    if not prompts:
        print("加载评估提示词失败")
        return {}
        
    # 执行向量检索
    print("\n执行论文选题相关文献检索...")
    journal_count, journal_results = search_vector_by_text(paper_topic)
    
    print("\n执行实证模型相关文献检索...")
    journal_model_count, journal_model_results = search_vector_by_model(paper_topic, empirical_model)
    
    print("\n执行数据集检索...")
    dataset_count, dataset_results, keyword_counts = search_vector_from_dataset(variable_settings)
    
    print("\n执行征稿启事检索...")
    cfp_count, cfp_results = search_vector_from_cfp(paper_topic)
    
    print("\n执行SKJJ项目检索...")
    skjj_count, skjj_results = search_vector_from_skjj(paper_topic)
    
    # 计算各项得分
    # 1. 价值性得分
    # 1.1 文件支撑性得分
    skjj_score = min(5, skjj_count)
    
    # 1.2 征稿启事参考性得分
    cfp_reference_score = min(5, cfp_count)
    
    # 1.3 政策参考性得分
    policy_reference_score = 3  # 默认值
    
    # 1.4 实践解决性得分
    practical_solution_score = 3  # 默认值
    
    # 价值性总分
    value_score = (skjj_score + cfp_reference_score + policy_reference_score + practical_solution_score) / 4
    
    # 2. 创新性得分
    # 2.1 理论创新可能性得分
    theoretical_innovation_score = 3  # 默认值
    
    # 2.2 研究视角创新性得分
    research_perspective_score = 5 - min(5, journal_count / 3)
    
    # 理论创新总分
    theoretical_innovation_total_score = (theoretical_innovation_score + research_perspective_score) / 2
    
    # 2.3 模型创新性得分
    model_innovation_score = 5 - min(5, journal_model_count / 3)
    
    # 2.4 数据创新性得分
    data_innovation_score = 3  # 默认值
    
    # 创新性总分
    innovation_score = (theoretical_innovation_total_score + model_innovation_score + data_innovation_score) / 3
    
    # 3. 可行性得分
    # 3.1 数据可得性得分
    data_availability_score = min(5, dataset_count)
    
    # 3.2 实证模型可行性得分
    empirical_model_score = 3  # 默认值
    
    # 可行性总分
    feasibility_score = (data_availability_score + empirical_model_score) / 2
    
    # 总分
    total_score = (value_score + innovation_score + feasibility_score) / 3
    
    # 生成分析文本
    # 文件支撑性分析
    skjj_analysis = f"该选题在国家社科基金重大项目招标选题中找到了{skjj_count}个相关项目，表明该选题具有一定的文件支撑性。"
    
    # 征稿启事参考性分析
    cfp_analysis = f"该选题在期刊征稿启事中找到了{cfp_count}个相关征稿，表明该选题具有一定的征稿启事参考性。"
    
    # 政策参考性分析
    policy_reference_reason = "该选题与当前政策导向具有一定的相关性，但需要进一步结合具体政策文件进行分析。"
    
    # 实践解决性分析
    practical_solution_reason = "该选题具有一定的实践解决价值，但需要进一步明确其实践应用场景和解决方案。"
    
    # 理论创新可能性分析
    theoretical_innovation_reason = "该选题在理论层面有一定的创新空间，但需要进一步明确其理论贡献点。"
    
    # 研究视角创新性分析
    research_perspective_innovation_analysis = f"该选题在现有文献中找到了{journal_count}篇相关文献，创新空间{5 - min(5, journal_count / 3)}星。"
    
    # 模型创新性分析
    model_innovation_analysis = f"该选题使用的实证模型在现有文献中找到了{journal_model_count}篇相关文献，创新空间{5 - min(5, journal_model_count / 3)}星。"
    
    # 数据创新性分析
    data_innovation_analysis = "该选题使用的数据具有一定的创新性，但需要进一步明确其数据处理和应用方式。"
    
    # 数据可得性分析
    data_availability_analysis = f"该选题涉及的变量在现有数据集中找到了{dataset_count}个相关数据集，数据可得性较高。"
    
    # 实证模型可行性分析
    empirical_model_feasibility_reason = "该选题使用的实证模型具有一定的可行性，但需要进一步明确其模型设定和估计方法。"
    
    # 返回评估结果
    return {
        "total_score": total_score,
        "value_score": value_score,
        "skjj_score": skjj_score,
        "skjj_analysis": skjj_analysis,
        "cfp_reference_score": cfp_reference_score,
        "cfp_analysis": cfp_analysis,
        "policy_reference_score": policy_reference_score,
        "policy_reference_reason": policy_reference_reason,
        "practical_solution_score": practical_solution_score,
        "practical_solution_reason": practical_solution_reason,
        "innovation_score": innovation_score,
        "theoretical_innovation_total_score": theoretical_innovation_total_score,
        "theoretical_innovation_score": theoretical_innovation_score,
        "theoretical_innovation_reason": theoretical_innovation_reason,
        "research_perspective_score": research_perspective_score,
        "research_perspective_innovation_analysis": research_perspective_innovation_analysis,
        "model_innovation_score": model_innovation_score,
        "model_innovation_analysis": model_innovation_analysis,
        "data_innovation_score": data_innovation_score,
        "data_innovation_analysis": data_innovation_analysis,
        "feasibility_score": feasibility_score,
        "data_availability_score": data_availability_score,
        "data_availability_analysis": data_availability_analysis,
        "empirical_model_feasibility_score": empirical_model_score,
        "empirical_model_feasibility_reason": empirical_model_feasibility_reason,
        "journal_results": journal_results,
        "journal_model_results": journal_model_results,
        "dataset_results": dataset_results,
        "cfp_results": cfp_results,
        "skjj_results": skjj_results
    }