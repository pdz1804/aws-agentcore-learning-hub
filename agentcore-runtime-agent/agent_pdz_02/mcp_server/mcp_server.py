"""
MCP Server for Amazon Bedrock AgentCore Runtime.
Provides advanced tools via Model Context Protocol.
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Any
import math
from datetime import datetime

# ============================================================================
# MCP Server Configuration
# ============================================================================

print("\n" + "=" * 70)
print(" MCP Server PDZ-02")
print("=" * 70)

mcp = FastMCP(
    name="pdz-mcp-server",
    host="0.0.0.0",
    stateless_http=True
)

print("[INFO] MCP Server configured for stateless HTTP")
print("[INFO] Host: 0.0.0.0:8000")
print("=" * 70 + "\n")


# ============================================================================
# Tools
# ============================================================================

@mcp.tool()
def calculate_statistics(numbers: List[float]) -> Dict[str, float]:
    """Calculate comprehensive statistics for a list of numbers."""
    print(f"\n[TOOL CALL] calculate_statistics")
    print(f"  Parameters: numbers={numbers}")
    
    if not numbers:
        print(f"  Result: ERROR - Empty list")
        return {"error": "Empty list provided"}
    
    sorted_nums = sorted(numbers)
    count = len(numbers)
    total = sum(numbers)
    mean = total / count
    
    if count % 2 == 0:
        median = (sorted_nums[count // 2 - 1] + sorted_nums[count // 2]) / 2
    else:
        median = sorted_nums[count // 2]
    
    variance = sum((x - mean) ** 2 for x in numbers) / count
    std_dev = math.sqrt(variance)
    
    result = {
        "mean": round(mean, 4),
        "median": round(median, 4),
        "std_dev": round(std_dev, 4),
        "min": min(numbers),
        "max": max(numbers),
        "sum": round(total, 4),
        "count": count
    }
    
    print(f"  Result: mean={result['mean']}, median={result['median']}, std_dev={result['std_dev']}")
    return result


@mcp.tool()
def compound_interest(principal: float, rate: float, time: float, frequency: int = 12) -> Dict[str, float]:
    """Calculate compound interest with detailed breakdown."""
    print(f"\n[TOOL CALL] compound_interest")
    print(f"  Parameters: principal={principal}, rate={rate}%, time={time} years, frequency={frequency}")
    
    rate_decimal = rate / 100
    amount = principal * (1 + rate_decimal / frequency) ** (frequency * time)
    interest = amount - principal
    roi = (interest / principal) * 100
    
    result = {
        "principal": round(principal, 2),
        "final_amount": round(amount, 2),
        "interest_earned": round(interest, 2),
        "roi_percentage": round(roi, 2),
        "years": time,
        "annual_rate": rate
    }
    
    print(f"  Result: final_amount=${result['final_amount']}, interest=${result['interest_earned']}, roi={result['roi_percentage']}%")
    return result


@mcp.tool()
def text_analyzer(text: str) -> Dict[str, Any]:
    """Analyze text and provide comprehensive statistics."""
    print(f"\n[TOOL CALL] text_analyzer")
    print(f"  Parameters: text='{text[:50]}{'...' if len(text) > 50 else ''}'")
    
    char_count = len(text)
    char_no_spaces = len(text.replace(" ", ""))
    words = text.split()
    word_count = len(words)
    
    sentence_endings = ['.', '!', '?']
    sentence_count = sum(text.count(ending) for ending in sentence_endings)
    sentence_count = max(sentence_count, 1)
    
    avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
    
    word_freq = {}
    for word in words:
        word_lower = word.lower().strip('.,!?;:')
        word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
    
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    
    result = {
        "characters": char_count,
        "characters_no_spaces": char_no_spaces,
        "words": word_count,
        "sentences": sentence_count,
        "avg_word_length": round(avg_word_length, 2),
        "avg_words_per_sentence": round(word_count / sentence_count, 2),
        "top_5_words": [{"word": word, "count": count} for word, count in top_words]
    }
    
    print(f"  Result: words={result['words']}, characters={result['characters']}, sentences={result['sentences']}")
    return result


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" Starting MCP Server PDZ-02")
    print("=" * 70)
    print(" Protocol: MCP over Streamable HTTP")
    print(" Host: 0.0.0.0")
    print(" Port: 8000")
    print(" Endpoint: /mcp")
    print("=" * 70 + "\n")
    
    mcp.run(transport="streamable-http")
