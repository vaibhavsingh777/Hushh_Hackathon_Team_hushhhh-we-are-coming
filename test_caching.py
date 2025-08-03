#!/usr/bin/env python3
"""
Test caching functionality specifically
"""

import asyncio
import time
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hushh_mcp.operons.categorize_content import categorize_with_free_llm


async def test_caching():
    """Test that caching is working correctly"""
    
    print("🧪 Testing Caching Functionality")
    print("=" * 40)
    
    test_content = "Important work meeting with the development team"
    content_type = "email"
    
    # First run - should take normal time
    print("\n📝 First run (no cache)...")
    start_time = time.time()
    result1 = await categorize_with_free_llm(test_content, content_type)
    first_time = time.time() - start_time
    
    print(f"Result: {result1['categories']}")
    print(f"Method: {result1['processing_method']}")
    print(f"Time: {first_time:.4f} seconds")
    
    # Second run - should be cached and faster
    print("\n🚀 Second run (should be cached)...")
    start_time = time.time()
    result2 = await categorize_with_free_llm(test_content, content_type)
    second_time = time.time() - start_time
    
    print(f"Result: {result2['categories']}")
    print(f"Method: {result2['processing_method']}")
    print(f"Time: {second_time:.4f} seconds")
    
    # Verify caching
    print("\n📊 Cache Analysis:")
    if "_cached" in result2['processing_method']:
        print("✅ Caching is working!")
        if second_time < first_time:
            speedup = first_time / second_time
            print(f"🚀 Speed improvement: {speedup:.1f}x faster")
        else:
            print("⚠️ Cache hit but no speed improvement detected")
    else:
        print("❌ Caching not detected - check implementation")
    
    # Test with different content
    print("\n🔄 Testing with different content...")
    different_content = "Buy groceries and pick up dry cleaning"
    result3 = await categorize_with_free_llm(different_content, "note")
    print(f"Different content result: {result3['categories']} ({result3['processing_method']})")
    
    # Test same content again
    result4 = await categorize_with_free_llm(test_content, content_type)
    print(f"Original content again: {result4['categories']} ({result4['processing_method']})")
    
    if "_cached" in result4['processing_method']:
        print("✅ Cache persistence verified!")
    
    print("\n🎉 Caching test completed!")


if __name__ == "__main__":
    asyncio.run(test_caching())
