# 核心API集成

<cite>
**本文档引用的文件**   
- [api.ts](file://web/lib/api.ts)
- [main.py](file://src/api/main.py)
- [solve.py](file://src/api/routers/solve.py)
- [research.py](file://src/api/routers/research.py)
- [knowledge.py](file://src/api/routers/knowledge.py)
- [progress_broadcaster.py](file://src/api/utils/progress_broadcaster.py)
- [task_id_manager.py](file://src/api/utils/task_id_manager.py)
- [history.py](file://src/api/utils/history.py)
- [solver/page.tsx](file://web/app/solver/page.tsx)
- [research/page.tsx](file://web/app/research/page.tsx)
</cite>

## 目录
1. [API基础配置与工具函数](#api基础配置与工具函数)
2. [RESTful API设计与前后端契约](#restful-api设计与前后端契约)
3. [WebSocket客户端封装与实时通信](#websocket客户端封装与实时通信)
4. [请求拦截、认证与错误处理](#请求拦截认证与错误处理)
5. [连接管理与恢复机制](#连接管理与恢复机制)
6. [性能优化与超时处理](#性能优化与超时处理)
7. [API调用示例与序列图](#api调用示例与序列图)
8. [总结](#总结)

## API基础配置与工具函数

`web/lib/api.ts` 文件提供了API基础配置和工具函数，用于构建完整的API和WebSocket URL。API基础URL通过环境变量 `NEXT_PUBLIC_API_BASE` 获取，该变量由 `start_web.py` 脚本根据 `config/main.yaml` 中的配置自动生成。如果未正确配置，系统会抛出错误并提示用户检查配置。

```mermaid
flowchart TD
A[获取API基础URL] --> B{NEXT_PUBLIC_API_BASE是否设置}
B --> |是| C[使用环境变量值]
B --> |否| D[抛出配置错误]
C --> E[构建完整API URL]
C --> F[构建WebSocket URL]
E --> G[HTTP/HTTPS -> http:///https://]
F --> H[HTTP/HTTPS -> ws:///wss://]
```

**代码片段路径**
- [api.ts](file://web/lib/api.ts#L6-L22)

## RESTful API设计与前后端契约

后端API通过FastAPI框架实现，`src/api/main.py` 定义了应用的生命周期和路由配置。所有API路由均通过 `app.include_router()` 方法挂载，并遵循统一的版本控制前缀 `/api/v1`。CORS（跨域资源共享）已配置为允许所有来源，生产环境中应限制为特定前端域名。

```mermaid
graph TB
subgraph "后端API"
A[FastAPI应用]
B[CORS中间件]
C[路由挂载]
D[静态文件服务]
end
subgraph "前端"
E[API调用]
end
B --> A
C --> A
D --> A
E --> A
```

**代码片段路径**
- [main.py](file://src/api/main.py#L39-L80)

## WebSocket客户端封装与实时通信

WebSocket连接用于实现实时通信，支持问题求解、研究流程等长时间运行任务的进度更新。`api.ts` 中的 `wsUrl()` 函数将HTTP协议转换为WS协议，确保WebSocket连接的正确建立。后端通过 `ProgressBroadcaster` 类管理WebSocket连接，实现进度广播。

```mermaid
sequenceDiagram
participant 前端 as 前端
participant WebSocket as WebSocket
participant 后端 as 后端
participant 进度广播器 as ProgressBroadcaster
前端->>WebSocket : 建立连接
WebSocket->>后端 : 接受连接
后端->>进度广播器 : 注册连接
速度广播器-->>后端 : 连接成功
后端-->>WebSocket : 发送任务ID
WebSocket-->>前端 : 接收任务ID
后端->>进度广播器 : 广播进度
速度广播器->>WebSocket : 发送进度更新
WebSocket-->>前端 : 显示实时进度
```

**代码片段路径**
- [api.ts](file://web/lib/api.ts#L47-L58)
- [progress_broadcaster.py](file://src/api/utils/progress_broadcaster.py#L11-L73)

## 请求拦截、认证与错误处理

API请求的统一拦截和错误处理机制确保了系统的稳定性和用户体验。前端在调用API时会进行错误捕获，根据错误类型显示不同的提示信息。例如，网络连接错误会提示用户检查后端服务是否运行，超时错误会建议检查网络连接或服务器负载。

```mermaid
flowchart TD
A[发起API请求] --> B{请求成功?}
B --> |是| C[处理响应数据]
B --> |否| D{错误类型}
D --> |网络错误| E[提示: 无法连接后端服务]
D --> |超时错误| F[提示: 请求超时]
D --> |其他错误| G[显示具体错误信息]
E --> H[建议检查后端服务]
F --> I[建议检查网络或服务器]
G --> J[直接显示错误]
```

**代码片段路径**
- [CoMarkerEditor.tsx](file://web/components/CoMarkerEditor.tsx#L808-L844)
- [CoWriterEditor.tsx](file://web/components/CoWriterEditor.tsx#L808-L844)

## 连接管理与恢复机制

WebSocket连接管理包括连接建立、消息广播和异常断开处理。`ProgressBroadcaster` 类使用线程锁确保多连接操作的线程安全，当连接异常断开时，系统会自动清理连接并移除对应的WebSocket实例。此外，系统还实现了任务ID管理器，为每个后台任务分配唯一ID，便于状态跟踪和管理。

```mermaid
classDiagram
class ProgressBroadcaster {
+_instance : ProgressBroadcaster
+_connections : dict[str, set[WebSocket]]
+_lock : asyncio.Lock
+get_instance() ProgressBroadcaster
+connect(kb_name : str, websocket : WebSocket)
+disconnect(kb_name : str, websocket : WebSocket)
+broadcast(kb_name : str, progress : dict)
+get_connection_count(kb_name : str) int
}
class TaskIDManager {
+_instance : TaskIDManager
+_task_ids : dict[str, str]
+_task_metadata : dict[str, dict]
+_lock : threading.Lock
+get_instance() TaskIDManager
+generate_task_id(task_type : str, task_key : str) str
+get_task_id(task_key : str) str | None
+update_task_status(task_id : str, status : str, **kwargs)
+get_task_metadata(task_id : str) dict | None
+cleanup_old_tasks(max_age_hours : int)
}
ProgressBroadcaster <|-- Singleton
TaskIDManager <|-- Singleton
```

**代码片段路径**
- [progress_broadcaster.py](file://src/api/utils/progress_broadcaster.py#L11-L73)
- [task_id_manager.py](file://src/api/utils/task_id_manager.py#L11-L103)

## 性能优化与超时处理

系统通过多种机制优化性能和处理超时情况。后端配置了Uvicorn服务器的热重载功能，但排除了代码执行工作区等目录，避免文件监控触发不必要的服务重启。前端通过自动滚动和日志过滤优化了大量日志输出的显示性能。对于长时间运行的任务，系统实现了超时处理和连接恢复机制。

```mermaid
flowchart TD
A[性能优化] --> B[后端热重载配置]
A --> C[前端日志过滤]
A --> D[自动滚动优化]
A --> E[连接超时处理]
B --> F[排除run_code_workspace等目录]
C --> G[过滤重复和不重要日志]
D --> H[仅在新日志时滚动]
E --> I[WebSocket心跳检测]
E --> J[连接断开后自动重连]
```

**代码片段路径**
- [main.py](file://src/api/main.py#L107-L128)
- [solver/page.tsx](file://web/app/solver/page.tsx#L95-L128)

## API调用示例与序列图

以下是一个典型的问题求解API调用序列图，展示了从用户输入问题到获取最终答案的完整流程。

```mermaid
sequenceDiagram
participant 用户 as 用户
participant 前端 as 前端
participant WebSocket as WebSocket
participant 后端 as 后端
participant 求解器 as MainSolver
用户->>前端 : 输入问题
前端->>WebSocket : 发送问题和配置
WebSocket->>后端 : 接收JSON数据
后端->>求解器 : 初始化求解器
求解器->>后端 : 返回任务ID
后端->>WebSocket : 发送任务ID
WebSocket-->>前端 : 接收任务ID
求解器->>后端 : 开始求解
后端->>WebSocket : 发送状态更新
WebSocket-->>前端 : 显示求解进度
求解器->>后端 : 完成求解
后端->>WebSocket : 发送最终结果
WebSocket-->>前端 : 显示最终答案
前端->>用户 : 展示结果
```

**代码片段路径**
- [solve.py](file://src/api/routers/solve.py#L34-L294)
- [solver/page.tsx](file://web/app/solver/page.tsx#L129-L166)

## 总结

本系统通过精心设计的RESTful API和WebSocket通信机制，实现了前后端的高效协作。API基础配置确保了服务的可配置性和灵活性，WebSocket实时通信支持了长时间运行任务的进度更新。统一的错误处理和连接管理机制提高了系统的稳定性和用户体验。前后端通过明确定义的契约保持一致性，确保了系统的可靠运行。

**代码片段路径**
- [api.ts](file://web/lib/api.ts)
- [main.py](file://src/api/main.py)
- [solve.py](file://src/api/routers/solve.py)
- [research.py](file://src/api/routers/research.py)
- [knowledge.py](file://src/api/routers/knowledge.py)