# hushh_mcp/agents/semantic_categorizer/manifest.py

manifest = {
    "id": "agent_semantic_categorizer",
    "name": "Semantic Categorizer Agent",
    "description": "LLM-based semantic categorization agent that maps user events/tasks into human-centric categories",
    "scopes": [
        "custom.temporary",
        "vault.read.email"
    ],
    "version": "1.0.0",
    "capabilities": [
        "semantic_categorization",
        "batch_processing",
        "entity_extraction", 
        "category_insights",
        "confidence_scoring"
    ],
    "dependencies": [
        "categorize_content_operon",
        "extract_entities_operon"
    ],
    "llm_integration": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "free_tier": True
    }
}
