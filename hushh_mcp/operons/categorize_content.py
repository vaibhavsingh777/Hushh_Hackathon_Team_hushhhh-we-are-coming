# hushh_mcp/operons/categorize_content.py
# Enhanced LLM-powered content categorization operon with smart fallbacks

from typing import List, Dict, Any, Optional, Union
import os
import json
import re
import asyncio
import hashlib
from datetime import datetime

# Simple in-memory cache for categorization results
_categorization_cache = {}
_cache_max_size = 1000

def _get_content_hash(content: str, content_type: str) -> str:
    """Create a hash for content to use as cache key"""
    return hashlib.md5(f"{content_type}:{content[:500]}".encode()).hexdigest()

def _cache_result(content: str, content_type: str, result: Dict[str, Any]) -> None:
    """Cache a categorization result"""
    global _categorization_cache
    if len(_categorization_cache) >= _cache_max_size:
        # Clear old entries if cache is full
        _categorization_cache.clear()
    
    cache_key = _get_content_hash(content, content_type)
    _categorization_cache[cache_key] = result

def _get_cached_result(content: str, content_type: str) -> Optional[Dict[str, Any]]:
    """Get cached categorization result if available"""
    cache_key = _get_content_hash(content, content_type)
    return _categorization_cache.get(cache_key)



async def _generate_dynamic_categorization_prompt(content: str, content_type: str, existing_categories: List[str] = None) -> str:
    """
    Generate a dynamic, intelligent categorization prompt based on content analysis and existing categories.
    """
    # Analyze content for key themes and patterns
    content_preview = content[:800]  # Longer preview for better analysis
    content_analysis = _analyze_content_themes(content_preview)
    
    # Build dynamic category suggestions based on content
    base_prompt = f"""You are an expert AI content categorization specialist. Your task is to analyze {content_type} content and assign the most semantically meaningful category.

CONTENT ANALYSIS CONTEXT:
- Content type: {content_type}
- Content length: {len(content.split())} words
- Key themes detected: {', '.join(content_analysis.get('themes', ['general']))}
- Entities found: {', '.join(content_analysis.get('entities', ['none']))}

CATEGORIZATION INSTRUCTIONS:
1. **SMART GROUPING PRIORITY**: Group semantically similar content into broader categories
2. **Example Smart Groupings**:
   - All job-related content → "job_opportunities" (job alerts, job notifications, job postings)
   - All work communications → "work_communication" (emails from colleagues, work updates, project discussions)
   - All financial transactions → "finance" (payments, invoices, receipts, billing)
   - All health-related → "health" (appointments, medical, wellness, fitness)
   - All shopping → "shopping" (orders, deliveries, confirmations, tracking)
3. **Avoid Hyper-Specific Categories**: Don't create separate categories for minor variations
4. **Use Existing Categories**: Always prefer broader existing categories over creating new narrow ones
5. **Semantic Intent Focus**: Categorize based on the overall purpose, not specific keywords
6. Use underscore_case for multi-word categories"""

    # Add existing categories context if provided
    if existing_categories and len(existing_categories) > 0:
        unique_categories = list(set(existing_categories))
        base_prompt += f"""

EXISTING CATEGORIES IN SYSTEM:
Current categories: {', '.join(unique_categories[:15])}
{'(and ' + str(len(unique_categories) - 15) + ' more...)' if len(unique_categories) > 15 else ''}

CATEGORY REUSE GUIDELINES:
- **MANDATORY**: Always try to fit content into existing categories first
- **Smart Grouping Examples**:
  * "job alert" + "job notification" + "job posting" → ALL use "job_opportunities"  
  * "team meeting" + "client meeting" + "project meeting" → ALL use "work_meetings"
  * "order confirmation" + "shipping update" + "delivery notice" → ALL use "shopping"
  * "payment receipt" + "invoice" + "billing notice" → ALL use "finance"
- **Decision Process**: Ask "What is the core purpose?" not "What are the exact words?"
- **Similarity Threshold**: If 70%+ semantic similarity exists with existing category, use it
- **New Category Rule**: Only create if NO existing category covers the core semantic purpose"""

    # Add content-specific guidance
    content_guidance = _get_content_specific_guidance(content_type, content_analysis)
    if content_guidance:
        base_prompt += f"\n\nCONTENT-SPECIFIC GUIDANCE:\n{content_guidance}"

    # Add the actual content and response format
    base_prompt += f"""

CONTENT TO CATEGORIZE:
{content_preview}

RESPONSE FORMAT (JSON):
{{
  "category": "specific_meaningful_category_name",
  "confidence": 0.85,
  "reasoning": "Detailed explanation of why this category was chosen, including key semantic indicators",
  "is_new_category": true,
  "alternative_categories": ["alternative1", "alternative2"],
  "semantic_keywords": ["key", "terms", "that", "influenced", "decision"]
}}

IMPORTANT: Focus on semantic meaning rather than surface keywords. Create categories that would be useful for organization and retrieval."""

    return base_prompt


def _analyze_content_themes(content: str) -> Dict[str, List[str]]:
    """
    Analyze content to extract key themes and entities for dynamic categorization.
    """
    content_lower = content.lower()
    
    # Detect themes through semantic patterns
    themes = []
    entities = []
    
    # Time-related patterns
    time_patterns = [
        r'\b\d{1,2}[:/]\d{1,2}(?:[:/]\d{1,2})?\s*(?:am|pm)?\b',
        r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
        r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b',
        r'\b(?:tomorrow|today|yesterday|next week|last week)\b'
    ]
    
    if any(re.search(pattern, content_lower) for pattern in time_patterns):
        themes.append('time_sensitive')
        themes.append('scheduling')
    
    # Financial patterns
    financial_patterns = [
        r'\$\d+(?:\.\d{2})?',
        r'\b\d+(?:\.\d{2})?\s*(?:dollars?|usd|eur|gbp)\b',
        r'\b(?:payment|invoice|billing|subscription|refund|charge)\b'
    ]
    
    if any(re.search(pattern, content_lower) for pattern in financial_patterns):
        themes.append('financial')
    
    # Professional patterns
    professional_patterns = [
        r'\b(?:meeting|conference|presentation|project|deadline|client|colleague)\b',
        r'\b(?:manager|director|ceo|team|department|office)\b'
    ]
    
    if any(re.search(pattern, content_lower) for pattern in professional_patterns):
        themes.append('professional')
    
    # Personal patterns
    personal_patterns = [
        r'\b(?:family|friend|birthday|anniversary|personal|home)\b',
        r'\b(?:mom|dad|wife|husband|children|kids|parents)\b'
    ]
    
    if any(re.search(pattern, content_lower) for pattern in personal_patterns):
        themes.append('personal')
    
    # Health patterns
    health_patterns = [
        r'\b(?:doctor|appointment|medical|prescription|hospital|clinic)\b',
        r'\b(?:exercise|gym|fitness|diet|wellness|therapy)\b'
    ]
    
    if any(re.search(pattern, content_lower) for pattern in health_patterns):
        themes.append('health_related')
    
    # Extract entities (companies, people, places)
    entity_patterns = [
        r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Proper names
        r'\b[A-Z][a-z]+(?:\s+Inc\.|Corp\.|LLC|Ltd\.)\b',  # Companies
        r'\b(?:Amazon|Google|Microsoft|Apple|Facebook|Netflix)\b'  # Known entities
    ]
    
    for pattern in entity_patterns:
        matches = re.findall(pattern, content)
        entities.extend(matches[:5])  # Limit to prevent overwhelming
    
    return {
        'themes': themes if themes else ['general_content'],
        'entities': entities[:10]  # Limit entities
    }


def _get_content_specific_guidance(content_type: str, content_analysis: Dict[str, List[str]]) -> str:
    """
    Generate content-type specific guidance for categorization.
    """
    guidance = ""
    themes = content_analysis.get('themes', [])
    
    if content_type == "email":
        guidance = """For emails, consider:
- Purpose: informational, request, confirmation, marketing, personal
- Urgency: time-sensitive vs. general communication
- Sender relationship: professional, personal, automated system
- Action required: response needed, FYI, task assignment"""
        
        if 'time_sensitive' in themes:
            guidance += "\n- This appears time-sensitive, consider scheduling-related categories"
        if 'professional' in themes:
            guidance += "\n- Professional context detected, consider work-related subcategories"
    
    elif content_type == "calendar":
        guidance = """For calendar events, consider:
- Event type: meeting, appointment, deadline, reminder, personal event
- Participants: work team, family, medical, social
- Location: office, home, external venue, virtual
- Frequency: one-time, recurring, series"""
        
        if 'health_related' in themes:
            guidance += "\n- Health-related event detected, consider medical appointment categories"
    
    elif content_type == "document":
        guidance = """For documents, consider:
- Document purpose: reference, instruction, report, communication
- Audience: internal team, client-facing, personal use
- Content nature: technical, administrative, creative, analytical"""
    
    return guidance


async def categorize_with_free_llm(content: str, content_type: str = "email", existing_categories: List[str] = None) -> Dict[str, Any]:
    """
    Enhanced main function to categorize content using free LLM alternatives with smart fallbacks.
    Prioritizes local Ollama, then free cloud APIs, then rule-based fallback.
    Includes caching for efficiency.
    
    Args:
        content: Text content to categorize
        content_type: Type of content (email, calendar, document)
        
    Returns:
        Dict with category, confidence, reasoning, and processing_method
    """
    if not content or len(content.strip()) < 3:
        return {
            "category": "uncategorized",
            "confidence": 0.1,
            "reasoning": "Content too short or empty",
            "processing_method": "validation_fallback",
            "categories": ["uncategorized"]
        }
    
    # Check cache first
    cached_result = _get_cached_result(content, content_type)
    if cached_result:
        cached_result["processing_method"] += "_cached"
        return cached_result
    
    try:
        # Try Ollama local model first (completely free and private)
        print(f"🔍 Checking if Ollama is available for content categorization...")
        if await _check_ollama_available():
            print(f"✅ Ollama available! Using local LLM for categorization...")
            result = await categorize_with_ollama(content, content_type, "llama3.2", existing_categories)
            _cache_result(content, content_type, result)
            print(f"🤖 Ollama categorization successful: {result.get('category')} (confidence: {result.get('confidence', 0):.2f})")
            return result
        else:
            print(f"❌ Ollama not available, trying other LLM services...")
        
        # Try Groq API (free tier available)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and len(groq_key) > 10:
            print(f"🔍 Trying Groq API...")
            result = await categorize_with_groq(content, groq_key, content_type)
            _cache_result(content, content_type, result)
            return result
        else:
            print(f"❌ No Groq API key found")
        
        # Try Hugging Face API (free tier available)
        hf_key = os.getenv("HUGGINGFACE_API_KEY")
        if hf_key and len(hf_key) > 10:
            print(f"🔍 Trying Hugging Face API...")
            result = await categorize_with_huggingface(content, hf_key, content_type)
            _cache_result(content, content_type, result)
            return result
        else:
            print(f"❌ No Hugging Face API key found")
        
        print("ℹ️ No local Ollama or API keys found, using enhanced rule-based categorization")
        result = _categorize_with_enhanced_rules(content, content_type)
        _cache_result(content, content_type, result)
        return result
    
    except Exception as e:
        print(f"❌ LLM categorization failed: {str(e)}")
        result = _categorize_with_enhanced_rules(content, content_type)
        _cache_result(content, content_type, result)
        return result


def _categorize_with_enhanced_rules(content: str, content_type: str = "email") -> Dict[str, Any]:
    """
    Enhanced rule-based categorization with improved semantic analysis.
    Uses weighted keyword matching and context analysis.
    """
    content_lower = content.lower()
    categories = []
    confidence_scores = {}
    
    # Enhanced category mapping with weighted keywords
    category_definitions = {
        "work": {
            "keywords": ["meeting", "deadline", "project", "office", "colleague", "client", "business", "presentation", "report", "manager", "team", "conference", "proposal", "contract"],
            "patterns": [r"\b(q[1-4]|quarter|fiscal|budget|kpi|roi)\b", r"\bmeet(ing)?\s+(at|on|tomorrow|next)\b"],
            "weight": 1.0
        },
        "finance": {
            "keywords": ["money", "payment", "invoice", "budget", "expense", "income", "bank", "credit", "debit", "purchase", "transaction", "billing", "receipt", "refund", "subscription"],
            "patterns": [r"\$\d+", r"\d+\.\d{2}", r"\b(paid|owe|due|charge|bill)\b"],
            "weight": 1.2
        },
        "health": {
            "keywords": ["doctor", "appointment", "medication", "exercise", "gym", "diet", "wellness", "medical", "hospital", "prescription", "therapy", "checkup", "symptoms"],
            "patterns": [r"\b(dr\.|doctor|physician|clinic)\b", r"\b(dosage|mg|ml|prescription)\b"],
            "weight": 1.1
        },
        "personal": {
            "keywords": ["family", "friend", "birthday", "anniversary", "personal", "hobby", "weekend", "vacation", "relationship", "home", "kids", "children"],
            "patterns": [r"\b(mom|dad|wife|husband|sister|brother)\b", r"\b(happy birthday|anniversary)\b"],
            "weight": 0.9
        },
        "travel": {
            "keywords": ["flight", "hotel", "vacation", "trip", "booking", "travel", "destination", "passport", "luggage", "airport", "reservation", "itinerary"],
            "patterns": [r"\b(flight|booking)\s+#?\w+", r"\b(check.in|departure|arrival)\b"],
            "weight": 1.1
        },
        "education": {
            "keywords": ["learn", "course", "study", "book", "lecture", "assignment", "exam", "research", "university", "college", "tutorial", "webinar", "certification"],
            "patterns": [r"\b(grade|score|semester|syllabus)\b", r"\b(professor|instructor|student)\b"],
            "weight": 1.0
        },
        "shopping": {
            "keywords": ["buy", "purchase", "order", "shop", "delivery", "product", "item", "cart", "amazon", "ebay", "sale", "discount", "coupon", "shipping"],
            "patterns": [r"\border\s+#?\w+", r"\b(shipped|delivered|tracking)\b", r"\b\d+%\s+off\b"],
            "weight": 1.1
        },
        "entertainment": {
            "keywords": ["movie", "music", "game", "concert", "show", "party", "fun", "entertainment", "netflix", "spotify", "youtube", "streaming"],
            "patterns": [r"\b(watch|stream|listen|play)\b", r"\b(episode|season|album|track)\b"],
            "weight": 0.8
        },
        "social": {
            "keywords": ["social", "community", "network", "group", "event", "gathering", "meetup", "facebook", "twitter", "instagram", "linkedin"],
            "patterns": [r"\b(follow|like|share|comment)\b", r"\b(post|tweet|update)\b"],
            "weight": 0.9
        },
        "communication": {
            "keywords": ["email", "message", "call", "text", "chat", "notification", "contact", "phone", "whatsapp", "telegram", "zoom", "teams"],
            "patterns": [r"\b(call|text|message)\s+(me|you|us)\b", r"\b(zoom|meet|hangout)\s+link\b"],
            "weight": 0.7
        }
    }
    
    # Calculate weighted scores for each category
    for category, definition in category_definitions.items():
        score = 0.0
        matches = 0
        
        # Keyword matching with frequency weighting
        for keyword in definition["keywords"]:
            keyword_count = content_lower.count(keyword)
            if keyword_count > 0:
                score += keyword_count * definition["weight"]
                matches += keyword_count
        
        # Pattern matching
        for pattern in definition.get("patterns", []):
            pattern_matches = len(re.findall(pattern, content_lower))
            if pattern_matches > 0:
                score += pattern_matches * definition["weight"] * 1.5  # Patterns get higher weight
                matches += pattern_matches
        
        # Normalize score by content length and calculate confidence
        if score > 0:
            normalized_score = min(1.0, score / max(1, len(content.split()) / 10))
            # More realistic confidence calculation
            if matches >= 3:
                confidence = min(0.85, 0.4 + normalized_score * 0.45)  # Strong match: max 85%
            elif matches >= 2:
                confidence = min(0.75, 0.35 + normalized_score * 0.40)  # Medium match: max 75%
            else:
                confidence = min(0.65, 0.25 + normalized_score * 0.40)  # Weak match: max 65%
            
            categories.append({
                "category": category,
                "score": score,
                "confidence": confidence,
                "matches": matches
            })
    
    # Sort by score and select top categories
    categories.sort(key=lambda x: x["score"], reverse=True)
    
    if categories:
        top_category = categories[0]
        selected_categories = [cat["category"] for cat in categories[:3]]
        
        # Generate reasoning
        reasoning = f"Identified as '{top_category['category']}' based on {top_category['matches']} keyword/pattern matches"
        if len(categories) > 1:
            reasoning += f" (alternatives: {', '.join([cat['category'] for cat in categories[1:3]])})"
        
        return {
            "category": top_category["category"],
            "confidence": top_category["confidence"],
            "reasoning": reasoning,
            "processing_method": "enhanced_rules",
            "categories": selected_categories,
            "scores": {cat["category"]: cat["confidence"] for cat in categories[:3]}
        }
    else:
        # Fallback analysis for unmatched content
        fallback_category = _analyze_content_structure(content, content_type)
        return {
            "category": fallback_category,
            "confidence": 0.4,
            "reasoning": f"No keyword matches found, categorized based on content structure and type ({content_type})",
            "processing_method": "structure_analysis",
            "categories": [fallback_category]
        }


def _analyze_content_structure(content: str, content_type: str) -> str:
    """
    Analyze content structure when keywords don't match.
    """
    # Time-based patterns
    if re.search(r'\b\d{1,2}[:/]\d{1,2}\b', content):
        return "scheduling"
    
    # Financial patterns
    if re.search(r'\$\d+|\d+\.\d{2}|payment|invoice|bill', content):
        return "finance"
    
    # URL patterns (might be newsletters or notifications)
    if re.search(r'https?://|www\.', content):
        return "communication"
    
    # Long text documents
    if len(content.split()) > 100:
        return "documentation"
    
    # Short messages
    if len(content.split()) < 10:
        return "communication"
    
    # Content type specific defaults
    if content_type == "email":
        return "communication"
    elif content_type == "calendar":
        return "scheduling"
    else:
        return "general"


async def _check_ollama_available() -> bool:
    """
    Async check if Ollama is available and running locally.
    """
    try:
        import aiohttp
        
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ollama_url}/api/tags", timeout=aiohttp.ClientTimeout(total=3)) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('models', [])
                    available_models = [model.get('name', '') for model in models]
                    
                    # Check for suitable models
                    preferred_models = ['llama3.2', 'llama3.1', 'llama3', 'llama2', 'mistral', 'phi3', 'qwen']
                    has_model = any(any(pref in model for pref in preferred_models) for model in available_models)
                    
                    if has_model:
                        print(f"✅ Ollama available with models: {available_models[:3]}")
                        return True
                    else:
                        print(f"⚠️ Ollama running but no suitable models found. Available: {available_models}")
                        return False
                else:
                    return False
                    
    except Exception as e:
        print(f"🔍 Ollama not available: {str(e)}")
        return False


def _analyze_content_themes(content: str) -> Dict[str, List[str]]:
    """
    Analyze content to extract key themes and entities for dynamic categorization.
    """
    content_lower = content.lower()
    
    # Detect themes through semantic patterns
    themes = []
    entities = []
    
    # Time-related patterns
    time_patterns = [
        r'\b\d{1,2}[:/]\d{1,2}(?:[:/]\d{1,2})?\s*(?:am|pm)?\b',
        r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
        r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b',
        r'\b(?:tomorrow|today|yesterday|next week|last week)\b'
    ]
    
    if any(re.search(pattern, content_lower) for pattern in time_patterns):
        themes.append('time_sensitive')
        themes.append('scheduling')

    # Financial patterns
    financial_patterns = [
        r'\$\d+(?:\.\d{2})?',
        r'\b\d+(?:\.\d{2})?\s*(?:dollars?|usd|eur|gbp)\b',
        r'\b(?:payment|invoice|billing|subscription|refund|charge)\b'
    ]
    
    if any(re.search(pattern, content_lower) for pattern in financial_patterns):
        themes.append('financial')
    
    # Professional patterns
    professional_patterns = [
        r'\b(?:meeting|conference|presentation|project|deadline|client|colleague)\b',
        r'\b(?:manager|director|ceo|team|department|office)\b'
    ]
    
    if any(re.search(pattern, content_lower) for pattern in professional_patterns):
        themes.append('professional')
    
    # Personal patterns
    personal_patterns = [
        r'\b(?:family|friend|birthday|anniversary|personal|home)\b',
        r'\b(?:mom|dad|wife|husband|children|kids|parents)\b'
    ]
    
    if any(re.search(pattern, content_lower) for pattern in personal_patterns):
        themes.append('personal')
    
    # Health patterns
    health_patterns = [
        r'\b(?:doctor|appointment|medical|prescription|hospital|clinic)\b',
        r'\b(?:exercise|gym|fitness|diet|wellness|therapy)\b'
    ]
    
    if any(re.search(pattern, content_lower) for pattern in health_patterns):
        themes.append('health_related')
    
    # Extract entities (companies, people, places)
    entity_patterns = [
        r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Proper names
        r'\b[A-Z][a-z]+(?:\s+Inc\.|Corp\.|LLC|Ltd\.)\b',  # Companies
        r'\b(?:Amazon|Google|Microsoft|Apple|Facebook|Netflix)\b'  # Known entities
    ]
    
    for pattern in entity_patterns:
        matches = re.findall(pattern, content)
        entities.extend(matches[:5])  # Limit to prevent overwhelming
    
    return {
        'themes': themes if themes else ['general_content'],
        'entities': entities[:10]  # Limit entities
    }


def _get_content_specific_guidance(content_type: str, content_analysis: Dict[str, List[str]]) -> str:
    """
    Generate content-type specific guidance for categorization.
    """
    guidance = ""
    themes = content_analysis.get('themes', [])
    
    if content_type == "email":
        guidance = """For emails, consider:
- Purpose: informational, request, confirmation, marketing, personal
- Urgency: time-sensitive vs. general communication
- Sender relationship: professional, personal, automated system
- Action required: response needed, FYI, task assignment"""
        
        if 'time_sensitive' in themes:
            guidance += "\n- This appears time-sensitive, consider scheduling-related categories"
        if 'professional' in themes:
            guidance += "\n- Professional context detected, consider work-related subcategories"
    
    elif content_type == "calendar":
        guidance = """For calendar events, consider:
- Event type: meeting, appointment, deadline, reminder, personal event
- Participants: work team, family, medical, social
- Location: office, home, external venue, virtual
- Frequency: one-time, recurring, series"""
        
        if 'health_related' in themes:
            guidance += "\n- Health-related event detected, consider medical appointment categories"
    
    elif content_type == "document":
        guidance = """For documents, consider:
- Document purpose: reference, instruction, report, communication
- Audience: internal team, client-facing, personal use
- Content nature: technical, administrative, creative, analytical"""
    
    return guidance


async def categorize_with_ollama(content: str, content_type: str = "email", model: str = "llama3.2", existing_categories: List[str] = None) -> Dict[str, Any]:
    """
    Enhanced dynamic categorization using local Ollama model with smart prompting.
    """
    try:
        import aiohttp
        
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        
        # Dynamic prompt generation based on content analysis and existing categories
        prompt = await _generate_dynamic_categorization_prompt(content, content_type, existing_categories)
        
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.3,  # Slightly higher for creativity in new categories
                "top_p": 0.9,
                "num_predict": 300  # More tokens for detailed reasoning
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{ollama_url}/api/generate", json=data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get('response', '').strip()
                    
                    try:
                        # Parse JSON response
                        parsed_result = json.loads(response_text)
                        
                        category = parsed_result.get('category', 'general')
                        confidence = float(parsed_result.get('confidence', 0.7))
                        reasoning = parsed_result.get('reasoning', 'AI categorization')
                        alternatives = parsed_result.get('alternative_categories', [])
                        
                        # Allow dynamic categories but adjust confidence realistically
                        if confidence > 0.9:
                            confidence = 0.75 + (confidence - 0.9) * 0.5  # Cap at 85%
                        elif confidence > 0.8:
                            confidence = 0.65 + (confidence - 0.8) * 0.5  # Scale down high confidence
                        
                        # Clean up category name
                        category = category.lower().replace(' ', '_').replace('-', '_')
                        alternatives = [alt.lower().replace(' ', '_').replace('-', '_') for alt in alternatives if alt]
                        
                        categories = [category] + alternatives[:2]
                        
                        print(f"🤖 Ollama categorization: {category} (confidence: {confidence:.2f})")
                        
                        return {
                            "category": category,
                            "confidence": confidence,
                            "reasoning": reasoning,
                            "processing_method": "ollama_llm",
                            "categories": categories[:3],
                            "model_used": model
                        }
                        
                    except json.JSONDecodeError:
                        # Fallback parsing if JSON format fails
                        print("⚠️ Ollama returned non-JSON, attempting text parsing")
                        return _parse_ollama_text_response(response_text, content, content_type)
                        
                else:
                    print(f"❌ Ollama API error: {response.status}")
                    return _categorize_with_enhanced_rules(content, content_type)
        
    except Exception as e:
        print(f"❌ Ollama categorization failed: {str(e)}")
        return _categorize_with_enhanced_rules(content, content_type)


def _parse_ollama_text_response(response_text: str, content: str, content_type: str) -> Dict[str, Any]:
    """
    Parse non-JSON Ollama responses for category extraction.
    """
    valid_categories = [
        'work', 'personal', 'finance', 'health', 'education', 'shopping', 
        'travel', 'entertainment', 'social', 'communication', 'scheduling', 
        'documentation', 'general'
    ]
    
    response_lower = response_text.lower()
    found_categories = [cat for cat in valid_categories if cat in response_lower]
    
    if found_categories:
        category = found_categories[0]
        confidence = 0.6  # Medium confidence for text parsing
        reasoning = f"Extracted from Ollama text response: {response_text[:100]}..."
        
        return {
            "category": category,
            "confidence": confidence,
            "reasoning": reasoning,
            "processing_method": "ollama_text_parsing",
            "categories": found_categories[:3]
        }
    else:
        return _categorize_with_enhanced_rules(content, content_type)


async def categorize_with_groq(content: str, api_key: str, content_type: str = "email") -> Dict[str, Any]:
    """
    Enhanced categorization using Groq API with better prompting.
    """
    try:
        import aiohttp
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = f"""You are an expert {content_type} categorization AI. Analyze content and respond with a JSON object containing:
- category: one of [work, personal, finance, health, education, shopping, travel, entertainment, social, communication, scheduling, documentation, general]
- confidence: number between 0.0 and 1.0
- reasoning: brief explanation
- alternatives: array of 1-2 alternative categories

Be precise and consider context clues."""
        
        user_prompt = f"Categorize this {content_type}: {content[:500]}"
        
        data = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 150,
            "temperature": 0.2
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result['choices'][0]['message']['content'].strip()
                    
                    try:
                        parsed_result = json.loads(response_text)
                        category = parsed_result.get('category', 'general')
                        confidence = float(parsed_result.get('confidence', 0.7))
                        reasoning = parsed_result.get('reasoning', 'AI categorization')
                        alternatives = parsed_result.get('alternatives', [])
                        
                        categories = [category] + alternatives[:2]
                        
                        print(f"⚡ Groq categorization: {category} (confidence: {confidence:.2f})")
                        
                        return {
                            "category": category,
                            "confidence": confidence,
                            "reasoning": reasoning,
                            "processing_method": "groq_llm",
                            "categories": categories[:3]
                        }
                        
                    except json.JSONDecodeError:
                        # Fallback to simple parsing
                        categories = _extract_categories_from_text(response_text)
                        return {
                            "category": categories[0] if categories else "general",
                            "confidence": 0.6,
                            "reasoning": "Parsed from Groq text response",
                            "processing_method": "groq_text_parsing",
                            "categories": categories[:3]
                        }
                else:
                    print(f"Groq API error: {response.status}")
                    return _categorize_with_enhanced_rules(content, content_type)
        
    except Exception as e:
        print(f"❌ Groq API failed: {str(e)}")
        return _categorize_with_enhanced_rules(content, content_type)


async def categorize_with_huggingface(content: str, api_key: str, content_type: str = "email") -> Dict[str, Any]:
    """
    Enhanced categorization using Hugging Face with zero-shot classification.
    """
    try:
        import aiohttp
        
        url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        candidate_labels = [
            "work and business", "personal and family", "finance and money", "health and wellness", 
            "education and learning", "shopping and purchases", "travel and vacation", 
            "entertainment and leisure", "social and community", "communication and messaging", 
            "scheduling and appointments", "documentation and reports", "general topics"
        ]
        
        data = {
            "inputs": content[:512],
            "parameters": {
                "candidate_labels": candidate_labels
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if isinstance(result, dict) and 'labels' in result and 'scores' in result:
                        # Map labels back to simple categories
                        label_mapping = {
                            "work and business": "work",
                            "personal and family": "personal", 
                            "finance and money": "finance",
                            "health and wellness": "health",
                            "education and learning": "education",
                            "shopping and purchases": "shopping",
                            "travel and vacation": "travel",
                            "entertainment and leisure": "entertainment",
                            "social and community": "social",
                            "communication and messaging": "communication",
                            "scheduling and appointments": "scheduling",
                            "documentation and reports": "documentation",
                            "general topics": "general"
                        }
                        
                        top_label = result['labels'][0]
                        top_score = result['scores'][0]
                        category = label_mapping.get(top_label, "general")
                        
                        # Get alternative categories
                        alternatives = []
                        for label, score in zip(result['labels'][1:3], result['scores'][1:3]):
                            if score > 0.2:  # Threshold for alternatives
                                alt_category = label_mapping.get(label, "general")
                                if alt_category != category:
                                    alternatives.append(alt_category)
                        
                        categories = [category] + alternatives[:2]
                        
                        print(f"🤗 Hugging Face categorization: {category} (confidence: {top_score:.2f})")
                        
                        return {
                            "category": category,
                            "confidence": float(top_score),
                            "reasoning": f"Zero-shot classification with {top_score:.2f} confidence",
                            "processing_method": "huggingface_zero_shot",
                            "categories": categories
                        }
                    else:
                        print(f"Unexpected Hugging Face response format: {result}")
                        return _categorize_with_enhanced_rules(content, content_type)
                else:
                    print(f"Hugging Face API error: {response.status}")
                    return _categorize_with_enhanced_rules(content, content_type)
        
    except Exception as e:
        print(f"❌ Hugging Face API failed: {str(e)}")
        return _categorize_with_enhanced_rules(content, content_type)


def _extract_categories_from_text(text: str) -> List[str]:
    """
    Extract categories from plain text responses.
    """
    valid_categories = [
        'work', 'personal', 'finance', 'health', 'education', 'shopping', 
        'travel', 'entertainment', 'social', 'communication', 'scheduling', 
        'documentation', 'general'
    ]
    
    text_lower = text.lower()
    found_categories = [cat for cat in valid_categories if cat in text_lower]
    
    return found_categories if found_categories else ["general"]


def get_category_confidence(content: str, categories: List[str]) -> Dict[str, float]:
    """
    Enhanced confidence scoring for categories based on multiple factors.
    """
    confidence_scores = {}
    content_lower = content.lower()
    content_length = len(content.split())
    
    # Enhanced keyword mapping with weights
    category_indicators = {
        "work": {
            "strong": ["meeting", "deadline", "project", "client", "presentation", "proposal"],
            "medium": ["office", "colleague", "business", "manager", "team"],
            "weak": ["work", "job", "career"]
        },
        "finance": {
            "strong": ["payment", "invoice", "budget", "expense", "transaction"],
            "medium": ["money", "bank", "credit", "debit", "billing"],
            "weak": ["cost", "price", "financial"]
        },
        "health": {
            "strong": ["doctor", "appointment", "prescription", "medical"],
            "medium": ["exercise", "gym", "wellness", "therapy"],
            "weak": ["health", "fitness", "diet"]
        }
        # Add more categories as needed
    }
    
    for category in categories:
        if category in category_indicators:
            indicators = category_indicators[category]
            
            # Count weighted matches
            strong_matches = sum(1 for word in indicators["strong"] if word in content_lower)
            medium_matches = sum(1 for word in indicators["medium"] if word in content_lower)
            weak_matches = sum(1 for word in indicators["weak"] if word in content_lower)
            
            # Calculate weighted score
            weighted_score = (strong_matches * 3 + medium_matches * 2 + weak_matches * 1)
            
            # Normalize by content length and apply base confidence
            normalized_score = min(1.0, weighted_score / max(1, content_length / 20))
            # More realistic confidence calculation
            if strong_matches >= 2:
                confidence = min(0.80, 0.45 + normalized_score * 0.35)  # Strong evidence: max 80%
            elif strong_matches >= 1 or medium_matches >= 3:
                confidence = min(0.70, 0.35 + normalized_score * 0.35)  # Good evidence: max 70%
            else:
                confidence = min(0.60, 0.25 + normalized_score * 0.35)  # Weak evidence: max 60%
            
        else:
            # Default confidence for unknown categories
            confidence = 0.5
            
        confidence_scores[category] = confidence
    
    return confidence_scores


def enhance_categories_with_context(categories: List[str], user_context: Dict[str, Any]) -> List[str]:
    """
    Enhanced categorization with user context, time, and historical patterns.
    """
    enhanced = categories.copy()
    current_time = user_context.get("current_time", datetime.now())
    
    # Time-based enhancements
    hour = current_time.hour
    day_of_week = current_time.weekday()  # 0=Monday, 6=Sunday
    
    # Work hours context
    if user_context.get("work_hours"):
        work_start = user_context["work_hours"].get("start", 9)
        work_end = user_context["work_hours"].get("end", 17)
        
        if work_start <= hour <= work_end and day_of_week < 5:  # Weekdays
            if "work" not in enhanced and any(cat in ["communication", "scheduling"] for cat in enhanced):
                enhanced.append("work")
    
    # Weekend context
    if day_of_week >= 5:  # Weekend
        if "personal" not in enhanced and "entertainment" in enhanced:
            enhanced.insert(0, "personal")
    
    # Historical patterns
    if user_context.get("category_history"):
        frequent_categories = user_context["category_history"].get("frequent", [])
        for freq_cat in frequent_categories[:2]:
            if freq_cat not in enhanced:
                enhanced.append(freq_cat)
    
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for cat in enhanced:
        if cat not in seen:
            seen.add(cat)
            result.append(cat)
    
    return result[:5]  # Limit to top 5 categories


# Removed duplicate synchronous categorize_with_ollama function  
# Using only the async version defined earlier

# Removed duplicate synchronous _check_ollama_available function
# Using only the async version defined earlier

# Removed duplicate synchronous categorize_with_groq function  
# Using only the async version defined earlier

# Removed duplicate synchronous categorize_with_huggingface function  
# Using only the async version defined earlier

def categorize_with_openai_chat(content: str, api_key: str) -> List[str]:
    """
    Categorize content using OpenAI's Chat API (GPT-3.5-turbo).
    
    Args:
        content: Text content to categorize
        api_key: OpenAI API key
        
    Returns:
        List of category strings
    """
    try:
        import requests
        
        # Prepare the API request
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Create a focused prompt for categorization
        system_prompt = """You are an AI categorization assistant. Categorize the given text into 1-3 semantic categories from this list:
work, personal, finance, health, education, shopping, travel, entertainment, social, communication, scheduling, documentation, general, uncategorized.

Respond ONLY with category names separated by commas. No explanations."""
        
        user_prompt = f"Categorize this text: {content[:400]}"  # Limit content for API efficiency
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 50,
            "temperature": 0.3
        }
        
        # Make API request
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            categories_text = result['choices'][0]['message']['content'].strip()
            categories = [cat.strip().lower() for cat in categories_text.split(',') if cat.strip()]
            
            # Validate categories are from our allowed list
            valid_categories = [
                'work', 'personal', 'finance', 'health', 'education', 'shopping', 
                'travel', 'entertainment', 'social', 'communication', 'scheduling', 
                'documentation', 'general', 'uncategorized'
            ]
            
            filtered_categories = [cat for cat in categories if cat in valid_categories]
            
            return filtered_categories[:3] if filtered_categories else ["general"]
        else:
            print(f"OpenAI API error: {response.status_code} - {response.text}")
            return _categorize_with_enhanced_rules(content, "general")
        
    except Exception as e:
        print(f"❌ OpenAI Chat API failed: {str(e)}")
        return _categorize_with_enhanced_rules(content, "general")


def categorize_with_openai(content: str, api_key: Optional[str] = None) -> List[str]:
    """
    Categorize content using OpenAI's API (deprecated - use categorize_with_openai_chat).
    
    Args:
        content: Text content to categorize
        api_key: OpenAI API key
        
    Returns:
        List of category strings
    """
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("⚠️ No OpenAI API key found, using rule-based categorization")
        return _categorize_with_enhanced_rules(content, "general")
    
    # Use the new Chat API method
    return categorize_with_openai_chat(content, api_key)


def get_category_confidence(content: str, categories: List[str]) -> Dict[str, float]:
    """
    Calculate confidence scores for each category.
    
    Args:
        content: Original text content
        categories: List of assigned categories
        
    Returns:
        Dict mapping categories to confidence scores (0.0 to 1.0)
    """
    confidence_scores = {}
    content_lower = content.lower()
    
    for category in categories:
        # Simple confidence calculation based on keyword density
        category_keywords = {
            "work": ["meeting", "deadline", "project", "office", "colleague"],
            "finance": ["money", "payment", "invoice", "budget", "expense"],
            "health": ["doctor", "appointment", "medication", "exercise"],
            # Add more as needed
        }
        
        keywords = category_keywords.get(category, [])
        if keywords:
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            confidence = min(1.0, matches / len(keywords) + 0.3)  # Base confidence of 0.3
        else:
            confidence = 0.5  # Default confidence for unknown categories
            
        confidence_scores[category] = confidence
    
    return confidence_scores


def enhance_categories_with_context(categories: List[str], user_context: Dict[str, Any]) -> List[str]:
    """
    Enhance categorization with user context and history.
    
    Args:
        categories: Initial categories
        user_context: User's historical data and preferences
        
    Returns:
        Enhanced category list
    """
    enhanced = categories.copy()
    
    # Add context-based enhancements
    if user_context.get("work_hours") and "work" not in enhanced:
        current_hour = user_context.get("current_hour", 12)
        work_start = user_context.get("work_hours", {}).get("start", 9)
        work_end = user_context.get("work_hours", {}).get("end", 17)
        
        if work_start <= current_hour <= work_end:
            enhanced.append("work")
    
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for cat in enhanced:
        if cat not in seen:
            seen.add(cat)
            result.append(cat)
    
    return result[:5]  # Limit to top 5 categories
