# 论文选题评估系统

这是一个基于向量搜索技术的论文选题评估系统，用于全面评估学术论文选题的价值性、创新性和可行性。系统通过向量搜索技术，将用户提供的论文选题与多个专业数据集进行比对，生成详细的评估报告。

## 功能特点

- **多维度评估**：从价值性、创新性和可行性三个维度对论文选题进行全面评估
- **向量搜索技术**：使用阿里云DashScope和DashVector服务进行文本向量化和相似度搜索
- **多数据源集成**：整合期刊论文、征稿启事、数据集和社科基金项目等多种数据源
- **结构化报告**：生成包含详细分析和评分的Markdown格式评估报告

## 系统架构

- **核心模块**
  - `vector_search_core.py`：向量搜索核心功能实现
  - `search_functions.py`：各类搜索功能实现
  - `report_generator.py`：评估报告生成器
  - `evaluation_prompts.json`：评估标准和模板定义

## 评估维度

### 价值性评估
- 文件支撑性：与国家社科基金重大项目招标选题的匹配度
- 征稿启事参考性：与CSSCI期刊征稿启事的匹配度
- 政策参考性：与国家核心政策的契合度
- 实践解决性：问题针对性和问题价值性评估

### 创新性评估
- 理论创新：理论创新可能性评估
- 研究视角创新性：研究视角的新颖程度
- 模型创新性：实证模型的创新程度
- 数据创新性：数据指标的创新程度

### 可行性评估
- 数据可得性：研究所需数据的获取难度
- 能力匹配度：与研究者学术水平的匹配度
- 实证模型可行性：实证模型的适用性和可行性

## 使用方法

1. 准备论文选题和相关参数
2. 调用`calculate_research_score`函数进行评估
3. 使用`generate_research_report`函数生成评估报告

示例代码：
```python
from report_generator import generate_research_report

# 论文选题
paper_topic = "新质生产力对碳排放的影响路径"

# 变量设置
variable_settings = "新质生产力、碳排放、数字化转型、地区教育水平、地区金融发展水平、地区产业聚集水平"

# 学历水平
academic_qualification = "硕士"

# 实证模型
empirical_model = "空间计量模型"

# 生成评估报告
report_path = generate_research_report(
    paper_topic, 
    variable_settings, 
    academic_qualification, 
    empirical_model
)

print(f"评估报告已生成: {report_path}")
```

## 环境要求

- Python 3.6+
- 阿里云DashScope API密钥
- 阿里云DashVector API密钥

## 数据集说明

系统使用以下数据集进行评估：
- 期刊论文集合 (journal_new)
- 征稿启事集合 (CFP_v2)
- 数据集集合 (dataset_v4)
- 社科基金项目集合 (SKJJ)

## 测试

使用`function_test.py`文件可以测试系统的各项功能：
```
python function_test.py
```

更多测试脚本位于`test/`目录下。