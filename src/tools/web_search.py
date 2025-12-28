#!/usr/bin/env python
"""
Web Search Tool - Network search using Perplexity API
"""

from datetime import datetime
import json
import os

try:
    from perplexity import Perplexity

    PERPLEXITY_AVAILABLE = True
except ImportError:
    PERPLEXITY_AVAILABLE = False
    Perplexity = None


def web_search(query: str, output_dir: str | None = None, verbose: bool = False) -> dict:
    """
    Perform network search using Perplexity API and return results

    Args:
        query: Search query
        output_dir: Output directory (optional, if provided will save results)
        verbose: Whether to print detailed information

    Returns:
        dict: Dictionary containing search results
            {
                "query": str,
                "answer": str,
                "result_file": str (if file was saved)
            }

    Raises:
        ImportError: If perplexity module is not installed
        ValueError: If PERPLEXITY_API_KEY environment variable is not set
        Exception: If API call fails
    """
    # Check if perplexity module is available
    if not PERPLEXITY_AVAILABLE:
        raise ImportError(
            "perplexity module is not installed. To use web search functionality, please install the corresponding package.\n"
            "Note: This is an optional feature and does not affect the use of other modules."
        )

    # Check API key
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY environment variable is not set")

    # Initialize client
    client = Perplexity(api_key=api_key)

    try:
        # Call API
        completion = client.chat.completions.create(
            model="sonar",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Provide detailed and accurate answers based on web search results.",
                },
                {"role": "user", "content": query},
            ],
        )

        # Extract response content
        answer = completion.choices[0].message.content

        # Build result dictionary
        result = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "model": completion.model,
            "answer": answer,
            "response": {
                "content": answer,
                "role": completion.choices[0].message.role,
                "finish_reason": completion.choices[0].finish_reason,
            },
            "usage": {
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens,
                "cost": {
                    "total_cost": completion.usage.cost.total_cost,
                    "input_tokens_cost": completion.usage.cost.input_tokens_cost,
                    "output_tokens_cost": completion.usage.cost.output_tokens_cost,
                },
            },
            "citations": [],
            "search_results": [],
        }

        # Extract citation links (improved: includes complete metadata)
        if hasattr(completion, "citations") and completion.citations:
            for i, citation_url in enumerate(completion.citations, 1):
                citation_data = {
                    "id": i,
                    "reference": f"[{i}]",
                    "url": citation_url,
                    "title": "",
                    "snippet": "",
                }

                # Try to match from search_results
                for search_item in result.get("search_results", []):
                    if search_item.get("url") == citation_url:
                        citation_data["title"] = search_item.get("title", "")
                        citation_data["snippet"] = search_item.get("snippet", "")
                        break

                result["citations"].append(citation_data)

        # Extract search result details
        if hasattr(completion, "search_results") and completion.search_results:
            for search_item in completion.search_results:
                search_result = {
                    "title": search_item.title,
                    "url": search_item.url,
                    "date": search_item.date,
                    "last_updated": search_item.last_updated,
                    "snippet": search_item.snippet,
                    "source": search_item.source,
                }
                result["search_results"].append(search_result)

        # If output directory provided, save results
        result_file = None
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"search_{timestamp}.json"
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            result_file = output_path

            if verbose:
                print(f"Search results saved to: {output_path}")

        # Add file path to result
        if result_file:
            result["result_file"] = result_file

        if verbose:
            print(f"Query: {query}")
            print(f"Answer: {answer[:200]}..." if len(answer) > 200 else answer)

        return result

    except Exception as e:
        raise Exception(f"Perplexity API call failed: {e!s}")


if __name__ == "__main__":
    import sys

    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    # Test
    result = web_search("What is a diffusion model?", output_dir="./test_output", verbose=True)
    print("\nSearch completed!")
    print(f"Query: {result['query']}")
    print(f"Answer: {result['answer'][:300]}...")
