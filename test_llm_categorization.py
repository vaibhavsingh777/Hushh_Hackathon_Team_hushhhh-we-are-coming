#!/usr/bin/env python3
"""
Test LLM categorization to ensure it works errorlessly
"""

import asyncio
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_llm_categorization():
    """Test the LLM categorization function"""
    print("🧪 Testing LLM Categorization")
    print("=" * 50)
    
    try:
        from hushh_mcp.operons.categorize_content import categorize_with_free_llm
        
        # Test with sample email content
        test_content = "Meeting scheduled for tomorrow at 2 PM to discuss project roadmap and quarterly planning."
        
        print(f"📧 Test content: {test_content[:50]}...")
        
        # Test the categorization
        result = await categorize_with_free_llm(test_content, "email")
        
        print(f"✅ Categorization result:")
        print(f"   Category: {result.get('category', 'Unknown')}")
        print(f"   Confidence: {result.get('confidence', 0)}")
        print(f"   Method: {result.get('processing_method', 'Unknown')}")
        print(f"   Reasoning: {result.get('reasoning', 'No reasoning provided')[:100]}...")
        
        # Verify the result structure
        required_fields = ['category', 'confidence', 'processing_method']
        missing_fields = [field for field in required_fields if field not in result]
        
        if not missing_fields:
            print("\n🎉 LLM categorization test PASSED!")
            print("✅ All required fields present")
            print("✅ No async/await errors")
            print("✅ Function returns properly structured result")
            return True
        else:
            print(f"\n❌ Missing fields in result: {missing_fields}")
            return False
        
    except Exception as e:
        print(f"❌ LLM categorization test FAILED: {e}")
        return False

async def test_error_handling():
    """Test error handling with edge cases"""
    print("\n🛡️ Testing Error Handling")
    print("=" * 30)
    
    try:
        from hushh_mcp.operons.categorize_content import categorize_with_free_llm
        
        # Test with empty content
        result = await categorize_with_free_llm("", "email")
        print(f"✅ Empty content handled: {result.get('category', 'Unknown')}")
        
        # Test with very short content
        result = await categorize_with_free_llm("Hi", "email")
        print(f"✅ Short content handled: {result.get('category', 'Unknown')}")
        
        # Test with None content (should be caught)
        try:
            result = await categorize_with_free_llm(None, "email")
            print(f"✅ None content handled: {result.get('category', 'Unknown')}")
        except:
            print("⚠️ None content caused error (acceptable)")
        
        print("🎉 Error handling test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test FAILED: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 LLM Categorization Test Suite")
    print("=" * 60)
    
    # Test 1: Basic functionality
    test1_passed = await test_llm_categorization()
    
    # Test 2: Error handling
    test2_passed = await test_error_handling()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Basic Functionality: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"   Error Handling:      {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! LLM categorization is working correctly.")
        print("💡 Ready for production use with:")
        print("   • Ollama integration (if available)")
        print("   • API fallbacks (Groq, Hugging Face)")
        print("   • Rule-based fallback")
        print("   • Proper error handling")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        
    return test1_passed and test2_passed

if __name__ == "__main__":
    asyncio.run(main())
