# hushh_mcp/agents/file_parser/manifest.py

manifest = {
    "id": "agent_file_parser",
    "name": "File Parser Agent",
    "description": "Specialized agent for file parsing and document processing with OCR and entity extraction",
    "scopes": [
        "custom.temporary",
        "vault.read.email"
    ],
    "version": "1.0.0",
    "capabilities": [
        "pdf_parsing",
        "text_extraction",
        "ocr_processing",
        "document_parsing",
        "spreadsheet_parsing",
        "presentation_parsing",
        "batch_processing",
        "entity_extraction",
        "sentiment_analysis",
        "structured_data_extraction"
    ],
    "supported_formats": {
        "pdf": [".pdf"],
        "text": [".txt", ".md", ".csv", ".json", ".xml"],
        "image": [".jpg", ".jpeg", ".png", ".bmp", ".tiff"],
        "document": [".doc", ".docx", ".rtf"],
        "spreadsheet": [".xls", ".xlsx", ".ods"],
        "presentation": [".ppt", ".pptx", ".odp"]
    },
    "dependencies": [
        "parse_document_operon",
        "extract_entities_operon",
        "ocr_service",
        "pdf_parser",
        "document_parser"
    ],
    "integrations": {
        "ocr": "Tesseract/Google Vision API",
        "pdf": "PyPDF2/pdfplumber",
        "documents": "python-docx",
        "spreadsheets": "pandas/openpyxl",
        "presentations": "python-pptx"
    }
}
