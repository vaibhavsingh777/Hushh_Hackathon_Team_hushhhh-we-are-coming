# hushh_mcp/agents/file_parser/index.py

from typing import Dict, Any, List, Optional
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import UserID
from hushh_mcp.operons.parse_document import parse_pdf, parse_text, parse_image
from hushh_mcp.operons.extract_entities import extract_entities
import time
import os


class FileParserAgent:
    """
    Specialized agent for file parsing and document processing.
    Supports PDF, text, image, and other file formats.
    """

    def __init__(self, agent_id: str = "agent_file_parser"):
        self.agent_id = agent_id
        self.required_scope = ConsentScope.CUSTOM_TEMPORARY
        
        # Supported file types
        self.supported_types = {
            "pdf": [".pdf"],
            "text": [".txt", ".md", ".csv", ".json", ".xml"],
            "image": [".jpg", ".jpeg", ".png", ".bmp", ".tiff"],
            "document": [".doc", ".docx", ".rtf"],
            "spreadsheet": [".xls", ".xlsx", ".ods"],
            "presentation": [".ppt", ".pptx", ".odp"]
        }

    def parse_file(self, user_id: UserID, token_str: str, file_path: str, file_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse file and extract structured data with consent validation.
        
        Args:
            user_id: User requesting file parsing
            token_str: Valid consent token
            file_path: Path to file to parse
            file_type: Optional file type hint
            
        Returns:
            Dict with parsing results
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ File parsing denied: {reason}")
        
        if token.user_id != user_id:
            raise PermissionError("❌ Token user mismatch")

        print(f"📄 File Parser Agent processing file for user {user_id}")
        
        # Validate file exists
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        # Determine file type
        if not file_type:
            file_type = self._detect_file_type(file_path)
        
        if not file_type:
            return {"error": f"Unable to determine file type for: {file_path}"}

        try:
            # Route to appropriate parser
            if file_type == "pdf":
                result = self._parse_pdf(file_path)
            elif file_type == "text":
                result = self._parse_text(file_path)
            elif file_type == "image":
                result = self._parse_image(file_path)
            elif file_type == "document":
                result = self._parse_document(file_path)
            elif file_type == "spreadsheet":
                result = self._parse_spreadsheet(file_path)
            elif file_type == "presentation":
                result = self._parse_presentation(file_path)
            else:
                return {"error": f"Unsupported file type: {file_type}"}
            
            # Extract entities from parsed content
            if "content" in result:
                entities = extract_entities(result["content"])
                result["entities"] = entities
            
            # Add metadata
            result.update({
                "user_id": user_id,
                "file_path": file_path,
                "file_type": file_type,
                "file_size": os.path.getsize(file_path),
                "parsed_at": int(time.time() * 1000),
                "agent_id": self.agent_id,
                "token_id": token.signature[:8]
            })
            
            print(f"✅ File parsed successfully: {file_type}")
            return result
            
        except Exception as e:
            print(f"❌ File parsing failed: {str(e)}")
            return {"error": f"File parsing failed: {str(e)}"}

    def _detect_file_type(self, file_path: str) -> Optional[str]:
        """Detect file type from extension."""
        _, ext = os.path.splitext(file_path.lower())
        
        for file_type, extensions in self.supported_types.items():
            if ext in extensions:
                return file_type
        
        return None

    def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse PDF file."""
        try:
            result = parse_pdf(file_path)
            
            return {
                "content": result["text"],
                "pages": result["pages"],
                "metadata": result.get("metadata", {}),
                "images_found": result.get("images_count", 0),
                "parsing_method": "pdf_extraction"
            }
            
        except Exception as e:
            return {"error": f"PDF parsing failed: {str(e)}"}

    def _parse_text(self, file_path: str) -> Dict[str, Any]:
        """Parse text-based files."""
        try:
            result = parse_text(file_path)
            
            return {
                "content": result["content"],
                "encoding": result.get("encoding", "utf-8"),
                "line_count": result.get("line_count", 0),
                "word_count": result.get("word_count", 0),
                "char_count": result.get("char_count", 0),
                "parsing_method": "text_extraction"
            }
            
        except Exception as e:
            return {"error": f"Text parsing failed: {str(e)}"}

    def _parse_image(self, file_path: str) -> Dict[str, Any]:
        """Parse image files using OCR."""
        try:
            result = parse_image(file_path)
            
            return {
                "content": result["text"],
                "confidence": result.get("confidence", 0),
                "image_dimensions": result.get("dimensions", {}),
                "detected_objects": result.get("objects", []),
                "parsing_method": "ocr_extraction"
            }
            
        except Exception as e:
            return {"error": f"Image parsing failed: {str(e)}"}

    def _parse_document(self, file_path: str) -> Dict[str, Any]:
        """Parse document files (DOC, DOCX)."""
        # Mock implementation - in production, use python-docx, etc.
        try:
            file_size = os.path.getsize(file_path)
            
            return {
                "content": f"Mock document content from {os.path.basename(file_path)}",
                "pages": 1,
                "word_count": 500,
                "paragraphs": 5,
                "parsing_method": "document_extraction",
                "file_size": file_size
            }
            
        except Exception as e:
            return {"error": f"Document parsing failed: {str(e)}"}

    def _parse_spreadsheet(self, file_path: str) -> Dict[str, Any]:
        """Parse spreadsheet files (XLS, XLSX)."""
        # Mock implementation - in production, use pandas, openpyxl, etc.
        try:
            file_size = os.path.getsize(file_path)
            
            return {
                "content": f"Mock spreadsheet data from {os.path.basename(file_path)}",
                "sheets": ["Sheet1", "Sheet2"],
                "rows": 100,
                "columns": 10,
                "has_headers": True,
                "parsing_method": "spreadsheet_extraction",
                "file_size": file_size
            }
            
        except Exception as e:
            return {"error": f"Spreadsheet parsing failed: {str(e)}"}

    def _parse_presentation(self, file_path: str) -> Dict[str, Any]:
        """Parse presentation files (PPT, PPTX)."""
        # Mock implementation - in production, use python-pptx, etc.
        try:
            file_size = os.path.getsize(file_path)
            
            return {
                "content": f"Mock presentation content from {os.path.basename(file_path)}",
                "slides": 15,
                "text_boxes": 45,
                "images": 8,
                "parsing_method": "presentation_extraction",
                "file_size": file_size
            }
            
        except Exception as e:
            return {"error": f"Presentation parsing failed: {str(e)}"}

    def batch_parse_files(self, user_id: UserID, token_str: str, file_paths: List[str]) -> Dict[str, Any]:
        """
        Parse multiple files in batch.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Batch file parsing denied: {reason}")

        print(f"📄 File Parser Agent batch processing {len(file_paths)} files for user {user_id}")
        
        results = []
        successful = 0
        failed = 0
        
        for i, file_path in enumerate(file_paths):
            try:
                result = self.parse_file(user_id, token_str, file_path)
                result["batch_index"] = i
                
                if "error" not in result:
                    successful += 1
                else:
                    failed += 1
                
                results.append(result)
                
            except Exception as e:
                results.append({
                    "batch_index": i,
                    "file_path": file_path,
                    "error": str(e)
                })
                failed += 1
        
        return {
            "user_id": user_id,
            "total_files": len(file_paths),
            "successful": successful,
            "failed": failed,
            "success_rate": round(successful / len(file_paths) * 100, 2),
            "results": results,
            "processed_at": int(time.time() * 1000),
            "agent_id": self.agent_id
        }

    def get_supported_formats(self) -> Dict[str, Any]:
        """
        Get list of supported file formats.
        """
        return {
            "supported_types": self.supported_types,
            "total_formats": sum(len(exts) for exts in self.supported_types.values()),
            "categories": list(self.supported_types.keys()),
            "agent_id": self.agent_id
        }

    def extract_structured_data(self, user_id: UserID, token_str: str, parsed_content: str, data_type: str) -> Dict[str, Any]:
        """
        Extract structured data from parsed content.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Data extraction denied: {reason}")

        print(f"🔍 File Parser Agent extracting {data_type} data for user {user_id}")
        
        try:
            if data_type == "contact_info":
                entities = extract_entities(parsed_content)
                return {
                    "emails": entities.get("emails", []),
                    "phones": entities.get("phones", []),
                    "names": entities.get("names", []),
                    "addresses": entities.get("addresses", [])
                }
            
            elif data_type == "financial_info":
                entities = extract_entities(parsed_content)
                return {
                    "money_amounts": entities.get("money", []),
                    "dates": entities.get("dates", []),
                    "companies": entities.get("companies", [])
                }
            
            elif data_type == "calendar_events":
                from hushh_mcp.operons.extract_entities import extract_calendar_events
                events = extract_calendar_events(parsed_content)
                return {"events": events}
            
            elif data_type == "action_items":
                from hushh_mcp.operons.extract_entities import extract_action_items
                actions = extract_action_items(parsed_content)
                return {"action_items": actions}
            
            else:
                return {"error": f"Unsupported data type: {data_type}"}
            
        except Exception as e:
            return {"error": f"Data extraction failed: {str(e)}"}

    def analyze_document_sentiment(self, user_id: UserID, token_str: str, content: str) -> Dict[str, Any]:
        """
        Analyze sentiment of document content.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Sentiment analysis denied: {reason}")

        print(f"😊 File Parser Agent analyzing sentiment for user {user_id}")
        
        # Simple sentiment analysis (in production, use proper NLP libraries)
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'happy', 'positive']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'sad', 'negative', 'angry']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        total_words = len(content.split())
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, (positive_count / max(1, total_words)) * 10)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, (negative_count / max(1, total_words)) * 10)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "total_words": total_words,
            "analyzed_at": int(time.time() * 1000)
        }
