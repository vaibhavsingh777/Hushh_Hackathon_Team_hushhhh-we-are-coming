# hushh_mcp/agents/semantic_categorizer/index.py

from typing import Dict, List, Any, Optional
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import UserID
from hushh_mcp.operons.categorize_content import categorize_with_llm
from hushh_mcp.operons.extract_entities import extract_entities
import time


class SemanticCategorizerAgent:
    """
    Specialized agent for LLM-based semantic categorization of user content.
    Maps user events/tasks into human-centric, meaningful buckets.
    """

    def __init__(self, agent_id: str = "agent_semantic_categorizer"):
        self.agent_id = agent_id
        self.required_scope = ConsentScope.CUSTOM_TEMPORARY

    def categorize_content(self, user_id: UserID, token_str: str, content: str) -> Dict[str, Any]:
        """
        Categorize user content using LLM-based semantic analysis.
        
        Args:
            user_id: User requesting categorization
            token_str: Valid consent token
            content: Text content to categorize
            
        Returns:
            Dict with categorization results
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Categorization denied: {reason}")
        
        if token.user_id != user_id:
            raise PermissionError("❌ Token user mismatch")

        print(f"🧠 Semantic Categorizer processing content for user {user_id}")
        
        if not content or len(content.strip()) < 3:
            return {"error": "Content too short for categorization"}

        try:
            # Use LLM operon for categorization
            categories = categorize_with_llm(content)
            
            # Extract entities for additional context
            entities = extract_entities(content)
            
            # Determine primary category and confidence
            primary_category = self._determine_primary_category(categories)
            
            result = {
                "primary_category": primary_category,
                "all_categories": categories,
                "entities": entities,
                "confidence_score": self._calculate_confidence(categories),
                "content_length": len(content),
                "processed_at": int(time.time() * 1000),
                "agent_id": self.agent_id
            }
            
            print(f"✅ Content categorized as: {primary_category}")
            return result
            
        except Exception as e:
            print(f"❌ Categorization failed: {str(e)}")
            return {"error": f"Categorization failed: {str(e)}"}

    def batch_categorize(self, user_id: UserID, token_str: str, content_list: List[str]) -> Dict[str, Any]:
        """
        Categorize multiple pieces of content in batch.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Batch categorization denied: {reason}")

        print(f"🧠 Batch categorizing {len(content_list)} items for user {user_id}")
        
        results = []
        for i, content in enumerate(content_list):
            try:
                result = self.categorize_content(user_id, token_str, content)
                result["batch_index"] = i
                results.append(result)
            except Exception as e:
                results.append({
                    "batch_index": i,
                    "error": str(e),
                    "content_preview": content[:50] + "..." if len(content) > 50 else content
                })
        
        return {
            "batch_results": results,
            "total_processed": len(content_list),
            "successful": len([r for r in results if "error" not in r]),
            "failed": len([r for r in results if "error" in r]),
            "processed_at": int(time.time() * 1000)
        }

    def get_category_insights(self, user_id: UserID, token_str: str, categories: List[str]) -> Dict[str, Any]:
        """
        Provide insights about category patterns and relationships.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Category insights denied: {reason}")

        print(f"📊 Generating category insights for user {user_id}")
        
        # Analyze category patterns
        category_counts = {}
        for cat in categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Find most common categories
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "category_distribution": dict(sorted_categories),
            "most_common": sorted_categories[0] if sorted_categories else None,
            "total_categories": len(category_counts),
            "unique_categories": len(category_counts),
            "insights": self._generate_insights(category_counts)
        }

    def _determine_primary_category(self, categories: List[str]) -> str:
        """Determine the most likely primary category."""
        if not categories:
            return "uncategorized"
        
        # If LLM provides confidence scores, use highest
        # For now, return first category
        return categories[0] if categories else "uncategorized"

    def _calculate_confidence(self, categories: List[str]) -> float:
        """Calculate confidence score for categorization."""
        if not categories:
            return 0.0
        
        # Simple heuristic: more specific categories = higher confidence
        specificity_scores = {
            "work": 0.8,
            "personal": 0.7,
            "finance": 0.9,
            "health": 0.8,
            "social": 0.6,
            "entertainment": 0.5,
            "education": 0.8,
            "travel": 0.7,
            "shopping": 0.8,
            "uncategorized": 0.2
        }
        
        primary = self._determine_primary_category(categories)
        return specificity_scores.get(primary.lower(), 0.5)

    def _generate_insights(self, category_counts: Dict[str, int]) -> List[str]:
        """Generate human-readable insights about category patterns."""
        insights = []
        
        if not category_counts:
            return ["No categories to analyze"]
        
        total = sum(category_counts.values())
        most_common = max(category_counts.items(), key=lambda x: x[1])
        
        insights.append(f"Most frequent category: {most_common[0]} ({most_common[1]} items)")
        
        if len(category_counts) > 3:
            insights.append(f"High category diversity with {len(category_counts)} different types")
        
        work_related = sum(count for cat, count in category_counts.items() 
                          if 'work' in cat.lower() or 'business' in cat.lower())
        if work_related > total * 0.4:
            insights.append("Work-focused content dominates your data")
        
        return insights
