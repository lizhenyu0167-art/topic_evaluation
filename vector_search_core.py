import os 
from dashvector import Client
import dashscope
from dashscope.embeddings.text_embedding import TextEmbedding

class APIConfig:
    """API配置类，管理API密钥和端点配置"""
    
    # 默认API密钥和端点
    DASHSCOPE_API_KEY = os.environ.get("ALI_BL_API_KEY", "sk-af619f6bab904deaad088ce46f94d098")
    DASHVECTOR_API_KEY = os.environ.get("ALI_API_KEY", "sk-lCTWY8yJFghu0veFEYoiACadz2U8R3B35764E233A11F081106692BAE8F276")
    CLUSTER_ENDPOINT = os.environ.get("CLUSTER_ENDPOINT", "vrs-cn-oo048jnmx00030.dashvector.cn-hangzhou.aliyuncs.com")
    
    # 集群和集合名称
    CLUSTER_NAME = "jiecl"
    JOURNAL_COLLECTION = "journal_new"
    CFP_COLLECTION = "CFP_v2"
    DATASET_COLLECTION = "dataset_v4"
    SKJJ_COLLECTION = "SKJJ"
    
    # 输出字段 - 根据不同集合类型返回不同字段
    @classmethod
    def get_output_fields(cls, collection_name=None):
        """根据集合名称返回相应的输出字段
        
        Args:
            collection_name: 集合名称，默认为None时使用当前上下文的集合名称
            
        Returns:
            list: 输出字段列表
        """
        if collection_name is None:
            return ["title", "keywords", "source", "journallevel"]  # 默认字段
            
        if collection_name == cls.JOURNAL_COLLECTION:
            return ["title", "source", "keywords", "descs", "publication_date", "url", "journallevel"]
        elif collection_name == cls.CFP_COLLECTION:
            return ["journal_name", "hot_topics", "call_for_papers_title","url"]
        elif collection_name == cls.DATASET_COLLECTION:
            return ["name", "indicators", "year_start", "year_end", "url"]
        elif collection_name == cls.SKJJ_COLLECTION:
            return ["topic_name"]
        else:
            return ["title", "keywords", "source", "journallevel"]  # 默认字段

class TextVectorizer:
    """文本向量转换类，负责将文本转换为向量"""
    
    def __init__(self, api_key=None):
        """初始化文本向量转换器
        
        Args:
            api_key: DashScope API密钥
        """
        self.api_key = api_key
        if api_key:
            dashscope.api_key = api_key
            # 设置DashScope的base_url
            dashscope.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            masked_key = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "未设置"
            print(f"DashScope API Key: {masked_key}")
        else:
            print("DashScope API Key未设置")
    
    def text_to_vector(self, text):
        """将文本转换为向量
        
        Args:
            text: 要转换的文本
            
        Returns:
            向量或None（如果转换失败）
        """
        try:
            # 使用DashScope的TextEmbedding模型将文本转换为向量
            resp = TextEmbedding.call(
                model="text-embedding-v4",  # 使用最新的embedding模型
                input=text,
                api_key=self.api_key
            )
            
            # 打印响应信息用于调试
            print(f"API响应状态: {resp.status_code}")
            # print(f"API响应内容: {resp.output}")
            
            if resp.status_code == 200:
                # 根据响应结构提取向量
                if hasattr(resp.output, 'embeddings') and resp.output.embeddings:
                    return resp.output.embeddings[0].embedding
                elif isinstance(resp.output, dict) and 'embeddings' in resp.output:
                    return resp.output['embeddings'][0]['embedding']
                else:
                    print(f"无法从响应中提取向量: {resp.output}")
                    return None
            else:
                print(f"文本转向量失败: {resp.message}")
                return None
        except Exception as e:
            print(f"文本转向量异常: {str(e)}")
            return None


class VectorSearchClient:
    """向量检索客户端类，负责连接服务和执行检索"""
    
    def __init__(self, api_key=None, endpoint=None):
        """初始化向量检索客户端
        
        Args:
            api_key: DashVector API密钥
            endpoint: 服务端点
        """
        self.api_key = api_key
        self.endpoint = endpoint
        self.client = None
        self.cluster = None
        self.collection = None
        
        # 尝试初始化客户端
        if api_key and endpoint:
            self._init_client()
    
    def _init_client(self):
        """初始化DashVector客户端"""
        try:
            self.client = Client(api_key=self.api_key, endpoint=self.endpoint)
            print("创建客户端成功!")
            # print(f"API Key: {self.api_key}")
            # print(f"Endpoint: {self.endpoint}")
            return True
        except Exception as e:
            print(f"创建客户端失败: {str(e)}")
            return False
    
    def get_cluster(self, cluster_name):
        """获取指定的集群
        
        Args:
            cluster_name: 集群名称
            
        Returns:
            成功返回True，失败返回False
        """
        try:
            self.cluster = self.client.get(name=cluster_name)
            print(f"成功获取cluster: {cluster_name}")
            return True
        except Exception as e:
            print(f"获取cluster失败: {str(e)}")
            return False
    
    def get_collection(self, collection_name):
        """获取指定的collection
        
        Args:
            collection_name: collection名称
            
        Returns:
            成功返回True，失败返回False
        """
        try:
            self.collection = self.client.get(name=collection_name)
            print(f"成功获取collection: {collection_name}")
            return True
        except Exception as e:
            print(f"获取collection失败: {str(e)}")
            return False
    
    def search(self, query_vector, topk=10, output_fields=None, include_vector=True):
        """执行向量检索
        
        Args:
            query_vector: 查询向量
            topk: 返回结果数量
            output_fields: 返回字段列表
            include_vector: 是否包含向量数据
            
        Returns:
            检索结果列表或None（如果检索失败）
        """
        if not self.collection:
            print("未设置collection，无法执行检索")
            return None
            
        try:
            print("\n执行向量检索...")
            results = self.collection.query(
                vector=query_vector,
                topk=topk,
                output_fields=output_fields,
                include_vector=include_vector
            )
            return results
        except Exception as e:
            print(f"执行向量检索失败: {str(e)}")
            return None


class ResultProcessor:
    """结果处理类，负责处理和统计检索结果"""
    
    @staticmethod
    def print_results(results, output_fields=None):
        """打印检索结果
        
        Args:
            results: 检索结果列表
            output_fields: 要打印的字段列表
        """
        if not results:
            print("没有检索结果")
            return
            
        print(f"\n找到 {len(results)} 条结果:")
        for i, result in enumerate(results):
            print(f"\n结果 {i+1}:")
            # 打印相似度分数
            if 'score' in result:
                print(f"相似度: {result['score']:.4f}")
                
            # 打印指定字段
            if output_fields:
                for field in output_fields:
                    if field in result:
                        print(f"{field}: {result[field]}")
            else:
                # 如果没有指定字段，打印所有非向量字段
                for key, value in result.items():
                    if key != 'vector':  # 不打印向量数据
                        print(f"{key}: {value}")
    
    @staticmethod
    def extract_field_values(results, field_name):
        """从结果中提取指定字段的值
        
        Args:
            results: 检索结果列表
            field_name: 要提取的字段名
            
        Returns:
            list: 提取的字段值列表
        """
        values = []
        if not results:
            return values
            
        for result in results:
            if field_name in result and result[field_name]:
                values.append(result[field_name])
                
        return values
    
    @staticmethod
    def calculate_average_score(results):
        """计算平均相似度分数
        
        Args:
            results: 检索结果列表
            
        Returns:
            float: 平均分数
        """
        if not results:
            return 0.0
            
        total_score = sum(result.get('score', 0) for result in results)
        return total_score / len(results)
    
    @staticmethod
    def filter_results_by_score(results, min_score=0.5):
        """按分数过滤结果
        
        Args:
            results: 检索结果列表
            min_score: 最小分数阈值
            
        Returns:
            list: 过滤后的结果列表
        """
        if not results:
            return []
            
        return [result for result in results if result.get('score', 0) >= min_score]


class VectorSearchEngine:
    """向量搜索引擎类，整合文本向量化和向量检索功能"""
    
    def __init__(self, dashscope_api_key=None, dashvector_api_key=None, endpoint=None):
        """初始化向量搜索引擎
        
        Args:
            dashscope_api_key: DashScope API密钥
            dashvector_api_key: DashVector API密钥
            endpoint: 服务端点
        """
        # 使用提供的API密钥或默认配置
        self.dashscope_api_key = dashscope_api_key or APIConfig.DASHSCOPE_API_KEY
        self.dashvector_api_key = dashvector_api_key or APIConfig.DASHVECTOR_API_KEY
        self.endpoint = endpoint or APIConfig.CLUSTER_ENDPOINT
        
        # 初始化文本向量转换器和向量检索客户端
        self.vectorizer = TextVectorizer(api_key=self.dashscope_api_key)
        self.search_client = VectorSearchClient(api_key=self.dashvector_api_key, endpoint=self.endpoint)
        
        # 结果处理器
        self.result_processor = ResultProcessor()
    
    def search_by_text(self, text, collection_name, topk=10, min_score=None, print_results=True):
        """通过文本执行向量检索
        
        Args:
            text: 查询文本
            collection_name: 集合名称
            topk: 返回结果数量
            min_score: 最小分数阈值
            print_results: 是否打印结果
            
        Returns:
            检索结果列表或None（如果检索失败）
        """
        # 将文本转换为向量
        query_vector = self.vectorizer.text_to_vector(text)
        if not query_vector:
            print("文本转向量失败，无法执行检索")
            return None
        
        # 获取集合
        if not self.search_client.get_collection(collection_name):
            print(f"获取集合 {collection_name} 失败，无法执行检索")
            return None
        
        # 获取输出字段
        output_fields = APIConfig.get_output_fields(collection_name)
        
        # 执行向量检索
        results = self.search_client.search(
            query_vector=query_vector,
            topk=topk,
            output_fields=output_fields,
            include_vector=False
        )
        
        if not results:
            print("检索未返回结果")
            return None
        
        # 如果设置了最小分数阈值，过滤结果
        if min_score is not None:
            results = self.result_processor.filter_results_by_score(results, min_score)
        
        # 打印结果
        if print_results:
            self.result_processor.print_results(results, output_fields)
        
        return results