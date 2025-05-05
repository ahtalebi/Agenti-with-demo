import os
import PyPDF2
import pandas as pd
from typing import Dict, List, Optional
import unicodedata
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process different file types into text for RAG embedding"""
    
    def __init__(self):
        self.supported_extensions = {
            '.txt': self.read_text,
            '.pdf': self.read_pdf,
            '.csv': self.read_csv,
            '.xlsx': self.read_excel,
            '.xls': self.read_excel,
            '.md': self.read_text,
            '.tex': self.read_text,
            '.docx': self.read_docx,
            '.doc': self.read_docx
        }
        logger.info(f"Initialized DocumentProcessor with support for: {', '.join(self.supported_extensions.keys())}")
    
    def read_text(self, file_path: str) -> str:
        """Read simple text files with encoding fallback"""
        logger.info(f"Reading text file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                logger.info(f"Successfully read text file: {file_path} ({len(content)} characters)")
                return content
        except UnicodeDecodeError:
            logger.warning(f"UTF-8 decode failed for {file_path}, trying latin-1")
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    content = file.read()
                    # Try to normalize unicode characters
                    normalized_content = unicodedata.normalize('NFKD', content)
                    logger.info(f"Successfully read with latin-1 encoding: {file_path}")
                    return normalized_content
            except Exception as e:
                logger.error(f"Failed to read text file with any encoding: {file_path} - {e}")
                return ""
    
    def read_pdf(self, file_path: str) -> str:
        """Read PDF files using PyPDF2"""
        logger.info(f"Reading PDF file: {file_path}")
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                logger.info(f"PDF has {num_pages} pages")
                
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"Page {page_num + 1}:\n{page_text}\n\n"
                            logger.debug(f"Extracted text from page {page_num + 1}: {len(page_text)} characters")
                        else:
                            logger.warning(f"No text found on page {page_num + 1}")
                    except Exception as e:
                        logger.error(f"Error extracting text from page {page_num + 1}: {e}")
                
                if text:
                    logger.info(f"Successfully read PDF: {file_path} ({len(text)} characters total)")
                else:
                    logger.warning(f"No text could be extracted from PDF: {file_path}")
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
        return text
    
    def read_csv(self, file_path: str) -> str:
        """Read CSV files and convert to text"""
        logger.info(f"Reading CSV file: {file_path}")
        try:
            df = pd.read_csv(file_path)
            rows, cols = df.shape
            logger.info(f"CSV dimensions: {rows} rows x {cols} columns")
            
            # Convert to string with headers
            content = f"CSV File: {os.path.basename(file_path)}\n\n{df.to_string(index=False)}"
            logger.info(f"Successfully read CSV: {file_path} ({len(content)} characters)")
            return content
        except Exception as e:
            logger.error(f"Error reading CSV {file_path}: {e}")
            return ""
    
    def read_excel(self, file_path: str) -> str:
        """Read Excel files and convert to text"""
        logger.info(f"Reading Excel file: {file_path}")
        try:
            # Read all sheets
            xls = pd.ExcelFile(file_path)
            logger.info(f"Excel file has {len(xls.sheet_names)} sheets: {', '.join(xls.sheet_names)}")
            
            sheets_text = []
            
            for sheet_name in xls.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    rows, cols = df.shape
                    logger.info(f"Sheet '{sheet_name}': {rows} rows x {cols} columns")
                    
                    sheet_content = f"Sheet: {sheet_name}\n{df.to_string(index=False)}\n"
                    sheets_text.append(sheet_content)
                except Exception as e:
                    logger.error(f"Error reading sheet '{sheet_name}': {e}")
            
            content = f"Excel File: {os.path.basename(file_path)}\n\n" + "\n\n".join(sheets_text)
            logger.info(f"Successfully read Excel: {file_path} ({len(content)} characters)")
            return content
        except Exception as e:
            logger.error(f"Error reading Excel {file_path}: {e}")
            return ""
    
    def read_docx(self, file_path: str) -> str:
        """Read Word documents"""
        logger.info(f"Reading Word document: {file_path}")
        try:
            from docx import Document
            doc = Document(file_path)
            text = []
            
            paragraph_count = 0
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():  # Skip empty paragraphs
                    text.append(paragraph.text)
                    paragraph_count += 1
            
            logger.info(f"Extracted {paragraph_count} paragraphs from Word document")
            
            content = f"Word Document: {os.path.basename(file_path)}\n\n" + "\n".join(text)
            logger.info(f"Successfully read Word document: {file_path} ({len(content)} characters)")
            return content
        except ImportError:
            logger.error(f"python-docx package not installed. Cannot read Word document: {file_path}")
            return ""
        except Exception as e:
            logger.error(f"Error reading Word document {file_path}: {e}")
            return ""
    
    def process_file(self, file_path: str) -> Optional[Dict[str, str]]:
        """Process a single file and return its content"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        logger.info(f"Processing file: {file_path}")
        logger.info(f"File extension: {ext}")
        
        if ext in self.supported_extensions:
            try:
                content = self.supported_extensions[ext](file_path)
                if content:
                    logger.info(f"  ✓ Successfully processed {file_path}")
                    result = {
                        'filename': os.path.basename(file_path),
                        'content': content,
                        'type': ext,
                        'path': file_path
                    }
                    logger.info(f"  Document info: {len(content)} characters, type: {ext}")
                    return result
                else:
                    logger.warning(f"  ✗ No content extracted from {file_path}")
            except Exception as e:
                logger.error(f"  ✗ Error processing {file_path}: {e}")
        else:
            logger.info(f"  ⚠ Unsupported file type: {ext}")
        
        return None
    
    def process_directory(self, directory: str) -> List[Dict[str, str]]:
        """Process all supported files in a directory"""
        documents = []
        
        logger.info(f"Scanning directory: {directory}")
        
        if not os.path.exists(directory):
            logger.error(f"Directory does not exist: {directory}")
            return documents
        
        files = os.listdir(directory)
        logger.info(f"Found {len(files)} items in directory")
        
        for filename in files:
            file_path = os.path.join(directory, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                logger.info(f"Skipping directory: {filename}")
                continue
            
            # Skip hidden files
            if filename.startswith('.'):
                logger.info(f"Skipping hidden file: {filename}")
                continue
            
            doc = self.process_file(file_path)
            if doc:
                documents.append(doc)
        
        logger.info(f"Successfully processed {len(documents)} out of {len(files)} items")
        
        # Summary
        if documents:
            logger.info("=== PROCESSED DOCUMENTS ===")
            for doc in documents:
                logger.info(f"  • {doc['filename']} ({doc['type']}) - {len(doc['content'])} chars")
            logger.info("==========================")
        else:
            logger.warning("No documents were successfully processed")
        
        return documents