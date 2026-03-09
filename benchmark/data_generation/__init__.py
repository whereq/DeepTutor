# Data Generation Pipeline for Benchmark
#
# Modules:
#   - llm_utils: LLM calling utilities (prompt loading, JSON parsing)
#   - scope_generator: Generate knowledge scope from KB via RAG
#   - profile_generator: Generate student profiles
#   - gap_generator: Generate knowledge gaps
#   - task_generator: Generate learning tasks
#   - pipeline: Orchestrate the full pipeline

from benchmark.data_generation.pipeline import DataGenerationPipeline
from benchmark.data_generation.request_pipeline import main as generate_requests_main

__all__ = ["DataGenerationPipeline", "generate_requests_main"]
