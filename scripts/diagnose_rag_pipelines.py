#!/usr/bin/env python
"""
RAG Pipeline Diagnostic Script
Run with: python scripts/diagnose_rag_pipelines.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / "DeepTutor.env", override=False)
load_dotenv(project_root / ".env", override=False)


class Colors:
    """Terminal colors"""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"  {Colors.GREEN}✓{Colors.END} {text}")


def print_warning(text: str):
    """Print warning message"""
    print(f"  {Colors.YELLOW}⚠{Colors.END} {text}")


def print_error(text: str):
    """Print error message"""
    print(f"  {Colors.RED}✗{Colors.END} {text}")


def print_info(text: str):
    """Print info message"""
    print(f"  {Colors.BLUE}ℹ{Colors.END} {text}")


def check_rag_anything_availability():
    """Check if RAG-Anything is available"""
    print_header("RAG-Anything 依赖检查")
    
    # Check sys.path setup
    raganything_path = project_root.parent / "raganything" / "RAG-Anything"
    if raganything_path.exists():
        print_success(f"RAG-Anything 路径存在: {raganything_path}")
        sys.path.insert(0, str(raganything_path))
    else:
        print_warning(f"RAG-Anything 路径不存在: {raganything_path}")
        print_info("这会影响 raganything, lightrag, academic pipeline")
    
    # Try importing
    try:
        from raganything import RAGAnything, RAGAnythingConfig
        print_success("可以导入 raganything 库")
        return True
    except ImportError as e:
        print_error(f"无法导入 raganything: {e}")
        return False


def check_lightrag_availability():
    """Check if LightRAG is available"""
    print_header("LightRAG 依赖检查")
    
    try:
        from lightrag import LightRAG
        print_success("可以导入 lightrag 库")
        return True
    except ImportError as e:
        print_error(f"无法导入 lightrag: {e}")
        return False


def check_embedding_service():
    """Check embedding service availability"""
    print_header("Embedding 服务检查")
    
    try:
        from src.services.embedding import get_embedding_client
        client = get_embedding_client()
        print_success(f"Embedding 客户端可用")
        print_info(f"Model: {client.config.model if hasattr(client, 'config') else 'unknown'}")
        return True
    except Exception as e:
        print_error(f"Embedding 服务错误: {e}")
        return False


def check_llm_service():
    """Check LLM service availability"""
    print_header("LLM 服务检查")
    
    try:
        from src.services.llm import get_llm_client, get_llm_config
        config = get_llm_config()
        print_success(f"LLM 配置可用")
        print_info(f"Model: {config.model}")
        print_info(f"Base URL: {config.base_url[:50]}..." if len(config.base_url) > 50 else f"Base URL: {config.base_url}")
        return True
    except Exception as e:
        print_error(f"LLM 服务错误: {e}")
        return False


def check_pipelines():
    """Check all pipeline availability"""
    print_header("Pipeline 可用性检查")
    
    from src.services.rag.factory import list_pipelines, get_pipeline, has_pipeline
    
    pipelines = list_pipelines()
    print_info(f"已注册 {len(pipelines)} 个 pipeline\n")
    
    results = {}
    for p in pipelines:
        pid = p["id"]
        print(f"\n{Colors.BOLD}  [{pid}]{Colors.END} {p['name']}")
        print(f"    描述: {p['description']}")
        
        try:
            pipeline = get_pipeline(pid)
            print_success(f"Pipeline 实例创建成功")
            
            # Check components for RAGPipeline types
            if hasattr(pipeline, '_parser'):
                components = []
                if pipeline._parser:
                    components.append(f"Parser: {pipeline._parser.name}")
                if pipeline._chunkers:
                    components.append(f"Chunkers: {[c.name for c in pipeline._chunkers]}")
                if pipeline._embedder:
                    components.append(f"Embedder: {pipeline._embedder.name}")
                if pipeline._indexers:
                    components.append(f"Indexers: {[i.name for i in pipeline._indexers]}")
                if pipeline._retriever:
                    components.append(f"Retriever: {pipeline._retriever.name}")
                
                for comp in components:
                    print_info(comp)
            
            results[pid] = "available"
            
        except Exception as e:
            print_error(f"Pipeline 创建失败: {e}")
            results[pid] = f"error: {e}"
    
    return results


async def test_pipeline_search(pipeline_id: str, kb_name: str = None):
    """Test a specific pipeline's search capability"""
    from src.tools.rag_tool import rag_search
    from src.services.rag.factory import get_pipeline
    
    print(f"\n  测试 {pipeline_id} 搜索功能...")
    
    # Find an existing KB
    if kb_name is None:
        kb_base = project_root / "data" / "knowledge_bases"
        if kb_base.exists():
            kbs = [d.name for d in kb_base.iterdir() if d.is_dir() and (d / "rag_storage").exists()]
            if kbs:
                kb_name = kbs[0]
                print_info(f"使用已有知识库: {kb_name}")
    
    if kb_name is None:
        print_warning("没有找到可用的知识库，跳过搜索测试")
        return False
    
    try:
        result = await rag_search(
            query="What is the main topic?",
            kb_name=kb_name,
            mode="naive",
            provider=pipeline_id
        )
        
        answer_len = len(result.get("answer", ""))
        if answer_len > 0:
            print_success(f"搜索成功，返回 {answer_len} 字符")
            return True
        else:
            print_warning("搜索返回空结果")
            return False
            
    except Exception as e:
        print_error(f"搜索失败: {e}")
        return False


def check_existing_knowledge_bases():
    """Check existing knowledge bases"""
    print_header("已有知识库检查")
    
    kb_base = project_root / "data" / "knowledge_bases"
    if not kb_base.exists():
        print_warning(f"知识库目录不存在: {kb_base}")
        return []
    
    kbs = []
    for kb_dir in kb_base.iterdir():
        if kb_dir.is_dir():
            kb_name = kb_dir.name
            rag_storage = kb_dir / "rag_storage"
            content_list = kb_dir / "content_list"
            numbered_items = kb_dir / "numbered_items.json"
            
            status = []
            if rag_storage.exists():
                status.append("rag_storage")
            if content_list.exists():
                status.append("content_list")
            if numbered_items.exists():
                status.append("numbered_items")
            
            if status:
                kbs.append(kb_name)
                print_success(f"{kb_name}: {', '.join(status)}")
            else:
                print_warning(f"{kb_name}: 空知识库")
    
    if not kbs:
        print_warning("没有找到已初始化的知识库")
    
    return kbs


def check_environment():
    """Check environment variables"""
    print_header("环境变量检查")
    
    env_vars = [
        ("RAG_PROVIDER", "raganything"),
        ("OPENAI_API_KEY", None),
        ("OPENAI_BASE_URL", None),
        ("LLM_MODEL", None),
        ("EMBEDDING_MODEL", None),
    ]
    
    for var, default in env_vars:
        value = os.getenv(var, default)
        if value:
            # Mask API keys
            if "KEY" in var and value:
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print_success(f"{var}: {masked}")
            else:
                print_success(f"{var}: {value}")
        else:
            print_warning(f"{var}: 未设置")


def print_summary(results: dict):
    """Print diagnostic summary"""
    print_header("诊断总结")
    
    for key, value in results.items():
        if value is True or value == "available":
            print_success(f"{key}: 可用")
        elif value is False:
            print_error(f"{key}: 不可用")
        elif isinstance(value, str) and value.startswith("error"):
            print_error(f"{key}: {value}")
        else:
            print_warning(f"{key}: {value}")


def print_recommendations(results: dict):
    """Print recommendations based on results"""
    print_header("建议")
    
    recommendations = []
    
    if not results.get("rag_anything_lib"):
        recommendations.append(
            "安装 RAG-Anything:\n"
            "    git clone https://github.com/HKUDS/RAG-Anything.git ../raganything/RAG-Anything\n"
            "    pip install -r ../raganything/RAG-Anything/requirements.txt"
        )
    
    if not results.get("embedding_service"):
        recommendations.append(
            "配置 Embedding 服务:\n"
            "    确保在 DeepTutor.env 或 .env 中设置了正确的 API key 和 base URL"
        )
    
    if not results.get("llm_service"):
        recommendations.append(
            "配置 LLM 服务:\n"
            "    确保在 DeepTutor.env 或 .env 中设置了正确的 OPENAI_API_KEY"
        )
    
    if results.get("pipelines", {}).get("llamaindex") == "available":
        print_success("llamaindex pipeline 可以在没有 RAG-Anything 的情况下使用 (轻量级向量搜索)")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"\n  {i}. {rec}")
    else:
        print_success("所有服务正常运行!")


async def main():
    """Main diagnostic function"""
    print(f"\n{Colors.BOLD}DeepTutor RAG Pipeline 诊断工具{Colors.END}")
    print(f"项目根目录: {project_root}\n")
    
    results = {}
    
    # Check environment
    check_environment()
    
    # Check services
    results["embedding_service"] = check_embedding_service()
    results["llm_service"] = check_llm_service()
    
    # Check external dependencies
    results["rag_anything_lib"] = check_rag_anything_availability()
    results["lightrag_lib"] = check_lightrag_availability()
    
    # Check pipelines
    results["pipelines"] = check_pipelines()
    
    # Check existing KBs
    kbs = check_existing_knowledge_bases()
    results["knowledge_bases"] = kbs
    
    # Print summary and recommendations
    print_summary(results)
    print_recommendations(results)
    
    # Optional: Run search tests
    if kbs and results.get("rag_anything_lib"):
        print_header("搜索功能测试")
        for pipeline_id in ["raganything"]:
            await test_pipeline_search(pipeline_id, kbs[0])


if __name__ == "__main__":
    if sys.platform == "win32":
        # Windows needs special handling for asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
