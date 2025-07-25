"""
Multimodal Processor - Handle images, PDFs, and logs for knowledge extraction

Processes visual materials, PDF documents, and execution logs to extract
implementation insights and architectural knowledge.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from .llm_router import LLMRouter, ContentType

logger = logging.getLogger(__name__)

class MultimodalInsight:
    """Represents insights extracted from multimodal content"""
    def __init__(self, content_type: str, title: str, insights: List[str], 
                 implementation_notes: List[str], gotchas: List[str], source_file: str):
        self.content_type = content_type
        self.title = title
        self.insights = insights
        self.implementation_notes = implementation_notes
        self.gotchas = gotchas
        self.source_file = source_file

class MultimodalProcessor:
    """Process images, PDFs, and logs for implementation knowledge"""
    
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        
        # Supported file types
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'}
        self.pdf_extensions = {'.pdf'}
        self.log_extensions = {'.log', '.txt', '.out'}
    
    async def process_multimodal_sources(self, source_paths: List[str]) -> Dict[str, List[MultimodalInsight]]:
        """
        Process multimodal sources for implementation insights
        
        Args:
            source_paths: List of directories or files containing images, PDFs, logs
            
        Returns:
            Dictionary mapping content types to insights
        """
        logger.info(f"Processing {len(source_paths)} multimodal sources")
        
        # Categorize files by type
        images = []
        pdfs = []
        logs = []
        
        for path in source_paths:
            path_obj = Path(path)
            if path_obj.is_file():
                if path_obj.suffix.lower() in self.image_extensions:
                    images.append(str(path_obj))
                elif path_obj.suffix.lower() in self.pdf_extensions:
                    pdfs.append(str(path_obj))
                elif path_obj.suffix.lower() in self.log_extensions:
                    logs.append(str(path_obj))
            elif path_obj.is_dir():
                # Find files in directory
                for ext in self.image_extensions:
                    images.extend([str(f) for f in path_obj.rglob(f'*{ext}')])
                for ext in self.pdf_extensions:
                    pdfs.extend([str(f) for f in path_obj.rglob(f'*{ext}')])
                for ext in self.log_extensions:
                    logs.extend([str(f) for f in path_obj.rglob(f'*{ext}')])
        
        logger.info(f"Found {len(images)} images, {len(pdfs)} PDFs, {len(logs)} log files")
        
        results = {}
        
        # Process images
        if images:
            results['images'] = await self._process_images(images[:10])  # Limit to 10 images
        
        # Process PDFs
        if pdfs:
            results['pdfs'] = await self._process_pdfs(pdfs[:5])  # Limit to 5 PDFs
        
        # Process logs
        if logs:
            results['logs'] = await self._process_logs(logs[:10])  # Limit to 10 log files
        
        return results
    
    async def _process_images(self, image_paths: List[str]) -> List[MultimodalInsight]:
        """Process images for architectural and implementation insights"""
        insights = []
        
        for image_path in image_paths:
            try:
                insight = await self._analyze_image(image_path)
                if insight:
                    insights.append(insight)
            except Exception as e:
                logger.warning(f"Could not process image {image_path}: {e}")
        
        return insights
    
    async def _analyze_image(self, image_path: str) -> Optional[MultimodalInsight]:
        """Analyze a single image for implementation insights"""
        
        prompt = """Analyze this image and extract insights that would help someone build a similar system.

Focus on:

1. **System Architecture**: If this shows system architecture, what are the key components and how do they interact?

2. **Implementation Insights**: What does this reveal about how to implement similar functionality?

3. **Design Patterns**: What architectural or design patterns are demonstrated?

4. **Technology Stack**: What technologies, frameworks, or tools are shown or implied?

5. **Data Flow**: How does data or information flow through the system?

6. **Integration Points**: What external systems or services are integrated?

7. **Implementation Gotchas**: What potential challenges or pitfalls does this reveal?

Provide practical insights that would guide someone building a similar system. If this is a UI mockup, focus on implementation approaches. If it's an architecture diagram, focus on system design decisions."""
        
        try:
            result = await self.llm_router.analyze_content(
                image_path, ContentType.IMAGE, prompt
            )
            
            return self._parse_multimodal_analysis(
                result, image_path, 'image', Path(image_path).name
            )
            
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return None
    
    async def _process_pdfs(self, pdf_paths: List[str]) -> List[MultimodalInsight]:
        """Process PDFs for implementation knowledge"""
        insights = []
        
        for pdf_path in pdf_paths:
            try:
                # Extract text from PDF (simplified - would use proper PDF extraction)
                text_content = self._extract_pdf_text(pdf_path)
                if text_content:
                    insight = await self._analyze_pdf_content(pdf_path, text_content)
                    if insight:
                        insights.append(insight)
            except Exception as e:
                logger.warning(f"Could not process PDF {pdf_path}: {e}")
        
        return insights
    
    def _extract_pdf_text(self, pdf_path: str) -> Optional[str]:
        """Extract text from PDF (simplified implementation)"""
        try:
            # This is a placeholder - in a real implementation, you'd use PyPDF2 or similar
            logger.info(f"PDF text extraction not fully implemented for {pdf_path}")
            return f"PDF content from {Path(pdf_path).name} - text extraction would be implemented here"
        except Exception as e:
            logger.error(f"Error extracting PDF text from {pdf_path}: {e}")
            return None
    
    async def _analyze_pdf_content(self, pdf_path: str, content: str) -> Optional[MultimodalInsight]:
        """Analyze PDF content for implementation insights"""
        
        prompt = """Analyze this PDF content and extract implementation insights.

Focus on:

1. **Technical Specifications**: What technical requirements or specifications are defined?

2. **Architecture Decisions**: What system design decisions are documented and why?

3. **Implementation Approaches**: How should the described functionality be implemented?

4. **Integration Requirements**: What external systems or APIs need to be integrated?

5. **Configuration and Setup**: What configuration or setup procedures are described?

6. **Common Issues**: What problems, gotchas, or challenges are mentioned?

Provide actionable insights that would help someone implement the described system or functionality."""
        
        try:
            result = await self.llm_router.analyze_content(
                content, ContentType.DOCUMENTATION, prompt
            )
            
            return self._parse_multimodal_analysis(
                result, pdf_path, 'pdf', Path(pdf_path).name
            )
            
        except Exception as e:
            logger.error(f"Error analyzing PDF content {pdf_path}: {e}")
            return None
    
    async def _process_logs(self, log_paths: List[str]) -> List[MultimodalInsight]:
        """Process log files for implementation insights and gotchas"""
        insights = []
        
        for log_path in log_paths:
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Read a sample of the log file (to avoid overwhelming the LLM)
                    content = f.read(50000)  # First 50KB
                
                if content.strip():
                    insight = await self._analyze_log_content(log_path, content)
                    if insight:
                        insights.append(insight)
                        
            except Exception as e:
                logger.warning(f"Could not process log file {log_path}: {e}")
        
        return insights
    
    async def _analyze_log_content(self, log_path: str, content: str) -> Optional[MultimodalInsight]:
        """Analyze log content for implementation insights and gotchas"""
        
        prompt = """Analyze these application logs and extract insights for building similar systems.

Focus on:

1. **Error Patterns**: What common errors or failures occur and how should they be handled?

2. **System Behavior**: What does this reveal about how the system operates in production?

3. **Performance Issues**: What performance problems are evident and how can they be avoided?

4. **Integration Gotchas**: What integration challenges or external service issues are shown?

5. **Implementation Insights**: What does this teach about implementing robust systems?

6. **Monitoring and Alerting**: What should be monitored based on these logs?

7. **Common Pitfalls**: What mistakes or issues should be avoided in similar implementations?

Provide practical insights that would help someone build a more robust system and avoid common pitfalls."""
        
        try:
            result = await self.llm_router.analyze_content(
                content, ContentType.LOGS, prompt
            )
            
            return self._parse_multimodal_analysis(
                result, log_path, 'logs', Path(log_path).name
            )
            
        except Exception as e:
            logger.error(f"Error analyzing log content {log_path}: {e}")
            return None
    
    def _parse_multimodal_analysis(self, analysis: str, file_path: str, 
                                 content_type: str, title: str) -> MultimodalInsight:
        """Parse LLM analysis into MultimodalInsight"""
        
        # Extract different types of insights from the analysis
        insights = []
        implementation_notes = []
        gotchas = []
        
        lines = analysis.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify sections
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['insights', 'architecture', 'system']):
                current_section = 'insights'
            elif any(keyword in line_lower for keyword in ['implementation', 'approach', 'how to']):
                current_section = 'implementation'
            elif any(keyword in line_lower for keyword in ['gotcha', 'pitfall', 'avoid', 'challenge', 'issue']):
                current_section = 'gotchas'
            elif line.startswith('- ') or line.startswith('* ') or line.startswith('• '):
                # This is a bullet point
                point = line[2:].strip() if line.startswith('- ') else line[1:].strip()
                
                if current_section == 'insights':
                    insights.append(point)
                elif current_section == 'implementation':
                    implementation_notes.append(point)
                elif current_section == 'gotchas':
                    gotchas.append(point)
                else:
                    # Default to insights if no section identified
                    insights.append(point)
        
        # If no structured sections found, extract general insights
        if not insights and not implementation_notes and not gotchas:
            # Split analysis into sentences and categorize
            sentences = [s.strip() for s in analysis.replace('\n', ' ').split('.') if s.strip()]
            for sentence in sentences[:10]:  # Limit to first 10 sentences
                if any(keyword in sentence.lower() for keyword in ['implement', 'build', 'create']):
                    implementation_notes.append(sentence)
                elif any(keyword in sentence.lower() for keyword in ['avoid', 'gotcha', 'pitfall', 'issue']):
                    gotchas.append(sentence)
                else:
                    insights.append(sentence)
        
        return MultimodalInsight(
            content_type=content_type,
            title=title,
            insights=insights,
            implementation_notes=implementation_notes,
            gotchas=gotchas,
            source_file=file_path
        )