# API路由设计

<cite>
**本文档引用的文件**
- [main.py](file://src/api/main.py)
- [solve.py](file://src/api/routers/solve.py)
- [question.py](file://src/api/routers/question.py)
- [research.py](file://src/api/routers/research.py)
- [co_writer.py](file://src/api/routers/co_writer.py)
- [guide.py](file://src/api/routers/guide.py)
- [ideagen.py](file://src/api/routers/ideagen.py)
- [knowledge.py](file://src/api/routers/knowledge.py)
- [notebook.py](file://src/api/routers/notebook.py)
- [dashboard.py](file://src/api/routers/dashboard.py)
- [settings.py](file://src/api/routers/settings.py)
- [system.py](file://src/api/routers/system.py)
- [task_id_manager.py](file://src/api/utils/task_id_manager.py)
- [history.py](file://src/api/utils/history.py)
</cite>

## 目录
1. [简介](#简介)
2. [项目结构](#项目结构)
3. [核心组件](#核心组件)
4. [架构概述](#架构概述)
5. [详细组件分析](#详细组件分析)
6. [依赖分析](#依赖分析)
7. [性能考虑](#性能考虑)
8. [故障排除指南](#故障排除指南)
9. [结论](#结论)

## 简介
DeepTutor是一个基于FastAPI的智能教育平台，提供解题、研究、引导、问题生成等多种AI辅助学习功能。本API文档详细描述了系统的RESTful和WebSocket路由设计，包括各功能模块的实现逻辑、路由注册机制、生命周期事件处理以及CORS跨域配置策略。

## 项目结构
DeepTutor的API路由采用模块化设计，每个功能模块都有独立的路由器文件，统一在主应用中注册。这种设计提高了代码的可维护性和可扩展性。

```mermaid
graph TD
subgraph "API模块"
main[main.py]
routers[routers/]
utils[utils/]
end
subgraph "功能路由器"
solve[solve.py]
question[question.py]
research[research.py]
co_writer[co_writer.py]
guide[guide.py]
ideagen[ideagen.py]
knowledge[knowledge.py]
notebook[notebook.py]
dashboard[dashboard.py]
settings[settings.py]
system[system.py]
end
subgraph "工具模块"
task_id[task_id_manager.py]
history[history.py]
end
main --> routers
routers --> solve
routers --> question
routers --> research
routers --> co_writer
routers --> guide
routers --> ideagen
routers --> knowledge
routers --> notebook
routers --> dashboard
routers --> settings
routers --> system
routers --> task_id
routers --> history
```

**图源**
- [main.py](file://src/api/main.py#L1-L129)
- [routers目录](file://src/api/routers/)

**章节源**
- [main.py](file://src/api/main.py#L1-L129)

## 核心组件
DeepTutor的API核心组件包括基于FastAPI的应用实例、模块化路由器、任务ID管理器和历史记录管理器。这些组件协同工作，提供了完整的RESTful和WebSocket服务。

**章节源**
- [main.py](file://src/api/main.py#L1-L129)
- [task_id_manager.py](file://src/api/utils/task_id_manager.py#L1-L103)
- [history.py](file://src/api/utils/history.py#L1-L172)

## 架构概述
DeepTutor的API架构采用分层设计，包括应用层、路由层、服务层和工具层。应用层负责初始化FastAPI实例和配置中间件；路由层包含各个功能模块的API端点；服务层提供业务逻辑实现；工具层提供通用功能支持。

```mermaid
graph TD
subgraph "应用层"
app[FastAPI应用]
cors[CORS中间件]
static[静态文件服务]
end
subgraph "路由层"
solve_router[解题路由器]
question_router[问题生成路由器]
research_router[研究路由器]
co_writer_router[协同写作路由器]
guide_router[引导学习路由器]
ideagen_router[创意生成路由器]
knowledge_router[知识库路由器]
notebook_router[笔记本路由器]
dashboard_router[仪表板路由器]
settings_router[设置路由器]
system_router[系统路由器]
end
subgraph "服务层"
solve_service[解题服务]
question_service[问题生成服务]
research_service[研究服务]
co_writer_service[协同写作服务]
guide_service[引导学习服务]
ideagen_service[创意生成服务]
knowledge_service[知识库服务]
notebook_service[笔记本服务]
end
subgraph "工具层"
task_id_manager[任务ID管理器]
history_manager[历史记录管理器]
progress_broadcaster[进度广播器]
notebook_manager[笔记本管理器]
end
app --> solve_router
app --> question_router
app --> research_router
app --> co_writer_router
app --> guide_router
app --> ideagen_router
app --> knowledge_router
app --> notebook_router
app --> dashboard_router
app --> settings_router
app --> system_router
solve_router --> solve_service
question_router --> question_service
research_router --> research_service
co_writer_router --> co_writer_service
guide_router --> guide_service
ideagen_router --> ideagen_service
knowledge_router --> knowledge_service
notebook_router --> notebook_service
solve_service --> task_id_manager
solve_service --> history_manager
question_service --> task_id_manager
question_service --> history_manager
research_service --> task_id_manager
research_service --> history_manager
co_writer_service --> task_id_manager
co_writer_service --> history_manager
guide_service --> task_id_manager
guide_service --> history_manager
ideagen_service --> task_id_manager
ideagen_service --> history_manager
knowledge_service --> task_id_manager
knowledge_service --> history_manager
notebook_service --> task_id_manager
notebook_service --> history_manager
```

**图源**
- [main.py](file://src/api/main.py#L1-L129)
- [各路由器文件](file://src/api/routers/)

**章节源**
- [main.py](file://src/api/main.py#L1-L129)

## 详细组件分析
### 解题功能分析
解题功能通过WebSocket提供实时问题解决服务，支持流式日志输出和进度更新。

#### 解题路由器实现
```mermaid
sequenceDiagram
participant 前端 as 前端应用
participant WebSocket as WebSocket端点
participant 解题器 as MainSolver
participant 日志拦截器 as LogInterceptor
participant 任务管理器 as TaskIDManager
前端->>WebSocket : 连接并发送问题
WebSocket->>任务管理器 : 生成任务ID
WebSocket->>解题器 : 初始化解题器
WebSocket->>日志拦截器 : 设置日志队列
WebSocket->>解题器 : 执行解题流程
loop 日志推送
日志拦截器->>WebSocket : 推送日志条目
WebSocket->>前端 : 发送日志
end
解题器->>WebSocket : 返回解题结果
WebSocket->>前端 : 发送最终结果
WebSocket->>历史记录 : 保存解题记录
```

**图源**
- [solve.py](file://src/api/routers/solve.py#L1-L294)

**章节源**
- [solve.py](file://src/api/routers/solve.py#L1-L294)

### 问题生成功能分析
问题生成功能支持两种模式：直接上传PDF试卷和使用预解析的试卷目录。

#### 问题生成路由器实现
```mermaid
sequenceDiagram
participant 前端 as 前端应用
participant WebSocket as WebSocket端点
participant 协调器 as AgentCoordinator
participant 模拟工具 as exam_mimic
前端->>WebSocket : 连接并发送配置
alt 上传PDF模式
WebSocket->>模拟工具 : 保存PDF文件
WebSocket->>模拟工具 : 解析PDF试卷
WebSocket->>模拟工具 : 执行问题生成工作流
else 预解析模式
WebSocket->>模拟工具 : 使用预解析的试卷目录
WebSocket->>模拟工具 : 执行问题生成工作流
end
模拟工具->>WebSocket : 发送进度更新
WebSocket->>前端 : 推送实时进度
模拟工具->>WebSocket : 返回生成结果
WebSocket->>前端 : 发送完成信号
WebSocket->>历史记录 : 保存问题生成记录
```

**图源**
- [question.py](file://src/api/routers/question.py#L1-L465)

**章节源**
- [question.py](file://src/api/routers/question.py#L1-L465)

### 研究功能分析
研究功能提供学术研究支持，包括主题优化和研究流程执行。

#### 研究路由器实现
```mermaid
sequenceDiagram
participant 前端 as 前端应用
participant WebSocket as WebSocket端点
participant 研究管道 as ResearchPipeline
participant 进度回调 as progress_callback
前端->>WebSocket : 连接并发送研究主题
WebSocket->>研究管道 : 初始化研究管道
WebSocket->>研究管道 : 设置进度回调
WebSocket->>研究管道 : 执行研究流程
loop 进度推送
研究管道->>进度回调 : 发送进度事件
进度回调->>WebSocket : 推送进度
WebSocket->>前端 : 发送进度更新
end
研究管道->>WebSocket : 返回研究报告
WebSocket->>前端 : 发送最终结果
WebSocket->>历史记录 : 保存研究记录
```

**图源**
- [research.py](file://src/api/routers/research.py#L1-L407)

**章节源**
- [research.py](file://src/api/routers/research.py#L1-L407)

### 协同写作功能分析
协同写作功能提供文本编辑、自动批改和语音讲解功能。

#### 协同写作路由器实现
```mermaid
flowchart TD
Start([API请求]) --> ValidateInput["验证输入参数"]
ValidateInput --> InputValid{"输入有效?"}
InputValid --> |否| ReturnError["返回错误响应"]
InputValid --> |是| CheckAction["检查操作类型"]
CheckAction --> Edit["文本编辑"]
CheckAction --> AutoMark["自动批改"]
CheckAction --> Narrate["语音讲解"]
Edit --> ProcessEdit["处理文本编辑请求"]
ProcessEdit --> ReturnEditResult["返回编辑结果"]
AutoMark --> ProcessAutoMark["处理自动批改请求"]
ProcessAutoMark --> ReturnAutoMarkResult["返回批改结果"]
Narrate --> CheckTTS["检查TTS配置"]
CheckTTS --> |可用| GenerateNarration["生成语音讲解"]
CheckTTS --> |不可用| ReturnTTSUnavailable["返回TTS不可用"]
GenerateNarration --> ReturnNarrationResult["返回讲解结果"]
ReturnEditResult --> End([结束])
ReturnAutoMarkResult --> End
ReturnNarrationResult --> End
ReturnTTSUnavailable --> End
ReturnError --> End
```

**图源**
- [co_writer.py](file://src/api/routers/co_writer.py#L1-L313)

**章节源**
- [co_writer.py](file://src/api/routers/co_writer.py#L1-L313)

### 引导学习功能分析
引导学习功能提供会话管理、学习进度跟踪和聊天交互。

#### 引导学习路由器实现
```mermaid
sequenceDiagram
participant 前端 as 前端应用
participant WebSocket as WebSocket端点
participant 引导管理器 as GuideManager
前端->>WebSocket : 连接并发送会话ID
WebSocket->>引导管理器 : 获取会话信息
WebSocket->>前端 : 发送会话详情
loop 消息循环
前端->>WebSocket : 发送消息
WebSocket->>引导管理器 : 处理消息
alt 消息类型
消息类型=开始 -> 引导管理器 : 开始学习
消息类型=下一个 -> 引导管理器 : 下一个知识点
消息类型=聊天 -> 引导管理器 : 聊天交互
消息类型=修复HTML -> 引导管理器 : 修复HTML
消息类型=获取会话 -> 引导管理器 : 获取会话状态
end
引导管理器->>WebSocket : 返回结果
WebSocket->>前端 : 发送响应
end
```

**图源**
- [guide.py](file://src/api/routers/guide.py#L1-L337)

**章节源**
- [guide.py](file://src/api/routers/guide.py#L1-L337)

### 创意生成功能分析
创意生成功能从笔记本内容中生成研究创意。

#### 创意生成路由器实现
```mermaid
flowchart TD
Start([WebSocket连接]) --> Init["初始化"]
Init --> Extract["提取知识点"]
Extract --> KnowledgeExtracted["知识点提取完成"]
KnowledgeExtracted --> Filter["松散过滤"]
Filter --> Filtered["过滤完成"]
Filtered --> Explore["探索研究创意"]
Explore --> Explored["探索完成"]
Explored --> StrictFilter["严格过滤"]
StrictFilter --> Generate["生成陈述"]
Generate --> IdeaReady["创意准备就绪"]
IdeaReady --> Complete["全部完成"]
Complete --> End([结束])
style Start fill:#f9f,stroke:#333,stroke-width:2px
style End fill:#f9f,stroke:#333,stroke-width:2px
```

**图源**
- [ideagen.py](file://src/api/routers/ideagen.py#L1-L414)

**章节源**
- [ideagen.py](file://src/api/routers/ideagen.py#L1-L414)

### 知识库功能分析
知识库功能提供知识库的CRUD操作、文件上传和初始化。

#### 知识库路由器实现
```mermaid
sequenceDiagram
participant 前端 as 前端应用
participant API as REST API端点
participant 知识库管理器 as KnowledgeBaseManager
participant 初始化器 as KnowledgeBaseInitializer
participant 进度广播器 as ProgressBroadcaster
前端->>API : 创建知识库
API->>知识库管理器 : 检查知识库是否存在
API->>初始化器 : 初始化知识库
API->>进度广播器 : 广播初始化进度
初始化器->>API : 返回初始化结果
API->>前端 : 返回创建结果
前端->>API : 上传文件
API->>知识库管理器 : 检查知识库是否存在
API->>后台任务 : 处理文件上传
后台任务->>进度广播器 : 广播处理进度
后台任务->>API : 返回处理结果
API->>前端 : 返回上传结果
```

**图源**
- [knowledge.py](file://src/api/routers/knowledge.py#L1-L535)

**章节源**
- [knowledge.py](file://src/api/routers/knowledge.py#L1-L535)

### 笔记本功能分析
笔记本功能提供笔记本的创建、查询、更新和删除，以及记录管理。

#### 笔记本路由器实现
```mermaid
classDiagram
class NotebookManager {
+list_notebooks() List[Notebook]
+get_statistics() Dict
+create_notebook(name, description, color, icon) Notebook
+get_notebook(notebook_id) Notebook
+update_notebook(notebook_id, name, description, color, icon) Notebook
+delete_notebook(notebook_id) bool
+add_record(notebook_ids, record_type, title, user_query, output, metadata, kb_name) Dict
+remove_record(notebook_id, record_id) bool
}
class CreateNotebookRequest {
+name : str
+description : str
+color : str
+icon : str
}
class UpdateNotebookRequest {
+name : str | None
+description : str | None
+color : str | None
+icon : str | None
}
class AddRecordRequest {
+notebook_ids : List[str]
+record_type : Literal["solve", "question", "research", "co_writer"]
+title : str
+user_query : str
+output : str
+metadata : dict
+kb_name : str | None
}
class RemoveRecordRequest {
+record_id : str
}
NotebookManager --> CreateNotebookRequest : "创建请求"
NotebookManager --> UpdateNotebookRequest : "更新请求"
NotebookManager --> AddRecordRequest : "添加记录请求"
NotebookManager --> RemoveRecordRequest : "删除记录请求"
```

**图源**
- [notebook.py](file://src/api/routers/notebook.py#L1-L248)

**章节源**
- [notebook.py](file://src/api/routers/notebook.py#L1-L248)

### 仪表板功能分析
仪表板功能提供最近历史记录和历史条目查询。

#### 仪表板路由器实现
```mermaid
flowchart TD
A([获取最近历史]) --> B["调用history_manager.get_recent()"]
B --> C{是否有类型过滤?}
C --> |是| D["按类型过滤历史记录"]
C --> |否| E["返回所有最近记录"]
D --> F["返回过滤后的记录"]
E --> G["返回最近记录"]
F --> H([返回结果])
G --> H
I([获取历史条目]) --> J["调用history_manager.get_entry()"]
J --> K{条目是否存在?}
K --> |是| L["返回条目详情"]
K --> |否| M["返回404错误"]
L --> N([返回结果])
M --> N
```

**图源**
- [dashboard.py](file://src/api/routers/dashboard.py#L1-L19)

**章节源**
- [dashboard.py](file://src/api/routers/dashboard.py#L1-L19)

### 设置功能分析
设置功能管理用户设置，包括主题、语言和环境变量。

#### 设置路由器实现
```mermaid
classDiagram
class ConfigManager {
+load_config() Dict
+save_config(config) bool
+get_env_info() Dict
}
class UISettings {
+theme : Literal["light", "dark"]
+language : Literal["zh", "en"]
+output_language : Literal["zh", "en"]
}
class FullSettingsResponse {
+ui : UISettings
+config : Dict[str, Any]
+env : Dict[str, str]
}
class EnvVarInfo {
+key : str
+value : str
+description : str
+category : str
+required : bool
+default : str
+sensitive : bool
+is_set : bool
}
class EnvCategoryInfo {
+id : str
+name : str
+description : str
+icon : str
}
class EnvConfigResponse {
+variables : List[EnvVarInfo]
+categories : List[EnvCategoryInfo]
}
ConfigManager --> FullSettingsResponse : "返回完整设置"
ConfigManager --> EnvConfigResponse : "返回环境配置"
UISettings --> FullSettingsResponse : "包含在完整设置中"
EnvVarInfo --> EnvConfigResponse : "包含在环境配置中"
EnvCategoryInfo --> EnvConfigResponse : "包含在环境配置中"
```

**图源**
- [settings.py](file://src/api/routers/settings.py#L1-L597)

**章节源**
- [settings.py](file://src/api/routers/settings.py#L1-L597)

### 系统功能分析
系统功能提供系统状态检查和模型连接测试。

#### 系统路由器实现
```mermaid
sequenceDiagram
participant 前端 as 前端应用
participant API as REST API端点
participant 核心模块 as src.core.core
前端->>API : 获取系统状态
API->>核心模块 : get_llm_config()
核心模块-->>API : 返回LLM配置
API->>核心模块 : get_embedding_config()
核心模块-->>API : 返回嵌入配置
API->>核心模块 : get_tts_config()
核心模块-->>API : 返回TTS配置
API->>前端 : 返回系统状态
前端->>API : 测试LLM连接
API->>核心模块 : get_llm_config()
核心模块-->>API : 返回LLM配置
API->>lightrag : openai_complete_if_cache()
lightrag-->>API : 返回测试响应
API->>前端 : 返回测试结果
前端->>API : 测试嵌入连接
API->>核心模块 : get_embedding_config()
核心模块-->>API : 返回嵌入配置
API->>lightrag : openai_embed()
lightrag-->>API : 返回嵌入响应
API->>前端 : 返回测试结果
前端->>API : 测试TTS连接
API->>核心模块 : get_tts_config()
核心模块-->>API : 返回TTS配置
API->>前端 : 返回配置验证结果
```

**图源**
- [system.py](file://src/api/routers/system.py#L1-L256)

**章节源**
- [system.py](file://src/api/routers/system.py#L1-L256)

## 依赖分析
DeepTutor的API组件之间存在明确的依赖关系，通过模块化设计降低了耦合度。

```mermaid
graph TD
main[main.py] --> solve[solve.py]
main --> question[question.py]
main --> research[research.py]
main --> co_writer[co_writer.py]
main --> guide[guide.py]
main --> ideagen[ideagen.py]
main --> knowledge[knowledge.py]
main --> notebook[notebook.py]
main --> dashboard[dashboard.py]
main --> settings[settings.py]
main --> system[system.py]
solve --> task_id_manager[task_id_manager.py]
solve --> history[history.py]
question --> task_id_manager
question --> history
research --> task_id_manager
research --> history
co_writer --> task_id_manager
co_writer --> history
guide --> task_id_manager
guide --> history
ideagen --> task_id_manager
ideagen --> history
knowledge --> task_id_manager
knowledge --> history
notebook --> task_id_manager
notebook --> history
dashboard --> history
settings --> task_id_manager
settings --> history
```

**图源**
- [main.py](file://src/api/main.py#L1-L129)
- [各路由器文件](file://src/api/routers/)

**章节源**
- [main.py](file://src/api/main.py#L1-L129)

## 性能考虑
DeepTutor的API设计考虑了性能优化，包括异步处理、后台任务和连接池管理。

**章节源**
- [main.py](file://src/api/main.py#L1-L129)
- [各路由器文件](file://src/api/routers/)

## 故障排除指南
当遇到API问题时，可以按照以下步骤进行排查：

1. 检查服务器是否正常运行
2. 验证请求的URL路径和HTTP方法是否正确
3. 检查请求参数是否符合API文档要求
4. 查看服务器日志以获取详细错误信息
5. 验证认证令牌是否有效且未过期
6. 检查网络连接是否正常

**章节源**
- [main.py](file://src/api/main.py#L1-L129)
- [各路由器文件](file://src/api/routers/)

## 结论
DeepTutor的API路由设计采用了现代化的FastAPI框架，提供了丰富的RESTful和WebSocket接口。通过模块化设计，各个功能组件保持了良好的独立性和可维护性。系统实现了完整的错误处理、日志记录和安全性措施，为用户提供稳定可靠的AI辅助学习服务。