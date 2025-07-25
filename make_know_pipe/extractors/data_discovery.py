"""
Data Discovery - Intelligently scan and sample data to auto-generate SOURCE_ANALYSIS

Handles large files by smart chunking and sampling to understand data patterns
without overwhelming the LLM with full file contents.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

from .llm_router import LLMRouter, ContentType

logger = logging.getLogger(__name__)

class DataSample:
    """Represents a sample from a data source"""
    def __init__(self, source_path: str, sample_type: str, content: str, metadata: Dict[str, Any]):
        self.source_path = source_path
        self.sample_type = sample_type  # "structure", "example", "schema"
        self.content = content
        self.metadata = metadata

class DataPattern:
    """Represents discovered patterns in the data"""
    def __init__(self, pattern_type: str, description: str, examples: List[str], confidence: float):
        self.pattern_type = pattern_type
        self.description = description
        self.examples = examples
        self.confidence = confidence

class DataDiscovery:
    """Intelligently discover and analyze data patterns for auto-generating SOURCE_ANALYSIS"""
    
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        
        # Chunking limits
        self.json_sample_size = 50  # Lines to sample from JSON
        self.md_chunk_size = 3000   # Characters per MD chunk
        self.max_samples_per_file = 3  # Max samples per large file
        
    async def discover_data_patterns(self, data_dir: str) -> Dict[str, List[DataPattern]]:
        """
        Discover patterns in data directory through intelligent sampling
        
        Args:
            data_dir: Directory containing data files
            
        Returns:
            Dictionary mapping data types to discovered patterns
        """
        logger.info(f"🔍 Discovering data patterns in: {data_dir}")
        
        # Step 1: Scan and categorize files
        file_inventory = self._scan_directory(data_dir)
        logger.info(f"Found {sum(len(files) for files in file_inventory.values())} files")
        
        # Step 2: Sample representative content from each file type
        samples = {}
        for file_type, files in file_inventory.items():
            logger.info(f"Sampling {file_type} files...")
            samples[file_type] = await self._sample_files(file_type, files)
        
        # Step 3: Analyze patterns in samples
        patterns = {}
        for file_type, type_samples in samples.items():
            if type_samples:
                logger.info(f"Analyzing patterns in {file_type}...")
                patterns[file_type] = await self._analyze_data_patterns(file_type, type_samples)
        
        return patterns
    
    def _scan_directory(self, data_dir: str) -> Dict[str, List[str]]:
        """Scan directory and categorize files by type"""
        data_path = Path(data_dir)
        if not data_path.exists():
            logger.warning(f"Data directory not found: {data_dir}")
            return {}
        
        file_inventory = {
            'json_api_docs': [],
            'markdown_docs': [],
            'text_docs': [],
            'config_files': [],
            'other': []
        }
        
        for file_path in data_path.rglob('*'):
            if file_path.is_file():
                self._categorize_file(str(file_path), file_inventory)
        
        return file_inventory
    
    def _categorize_file(self, file_path: str, inventory: Dict[str, List[str]]):
        """Categorize a file based on its characteristics"""
        path = Path(file_path)
        suffix = path.suffix.lower()
        name = path.name.lower()
        
        # JSON files (likely API docs based on user context)
        if suffix == '.json':
            inventory['json_api_docs'].append(file_path)
        
        # Markdown documentation
        elif suffix in ['.md', '.markdown']:
            inventory['markdown_docs'].append(file_path)
        
        # Text documentation
        elif suffix in ['.txt', '.rst']:
            inventory['text_docs'].append(file_path)
        
        # Configuration files
        elif suffix in ['.yaml', '.yml', '.toml', '.ini'] or name in ['config', 'settings']:
            inventory['config_files'].append(file_path)
        
        # Other files
        else:
            inventory['other'].append(file_path)
    
    async def _sample_files(self, file_type: str, files: List[str]) -> List[DataSample]:
        """Sample content from files of a specific type"""
        samples = []
        
        # Limit number of files to process
        selected_files = files[:20] if len(files) > 20 else files
        
        for file_path in selected_files:
            try:
                if file_type == 'json_api_docs':
                    file_samples = self._sample_json_file(file_path)
                elif file_type in ['markdown_docs', 'text_docs']:
                    file_samples = self._sample_text_file(file_path)
                elif file_type == 'config_files':
                    file_samples = self._sample_config_file(file_path)
                else:
                    continue
                
                samples.extend(file_samples)
                
            except Exception as e:
                logger.warning(f"Could not sample file {file_path}: {e}")
        
        return samples
    
    def _sample_json_file(self, file_path: str) -> List[DataSample]:
        """Sample JSON file with smart chunking for API docs"""
        samples = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # First, try to get file structure
                f.seek(0)
                first_lines = []
                for i, line in enumerate(f):
                    if i >= self.json_sample_size:
                        break
                    first_lines.append(line.strip())
                
                structure_sample = '\\n'.join(first_lines)
                samples.append(DataSample(
                    source_path=file_path,
                    sample_type="structure",
                    content=structure_sample,
                    metadata={"sample_method": "first_lines", "line_count": len(first_lines)}
                ))
                
                # Try to parse and extract key patterns
                f.seek(0)
                try:
                    data = json.load(f)
                    
                    # Extract API endpoint examples if this looks like API docs
                    if isinstance(data, dict):
                        # Look for common API doc patterns
                        api_examples = self._extract_api_examples(data)
                        if api_examples:
                            samples.append(DataSample(
                                source_path=file_path,
                                sample_type="api_examples",
                                content=json.dumps(api_examples, indent=2),
                                metadata={"extraction_method": "api_patterns"}
                            ))
                        
                        # Extract schema patterns
                        schema_examples = self._extract_schema_patterns(data)
                        if schema_examples:
                            samples.append(DataSample(
                                source_path=file_path,
                                sample_type="schema_patterns",
                                content=json.dumps(schema_examples, indent=2),
                                metadata={"extraction_method": "schema_analysis"}
                            ))
                
                except json.JSONDecodeError:
                    # If JSON parsing fails, just use the structure sample
                    pass
                
        except Exception as e:
            logger.warning(f"Error sampling JSON file {file_path}: {e}")
        
        return samples
    
    def _extract_api_examples(self, data: Dict) -> Dict[str, Any]:
        """Extract API endpoint examples from JSON data"""
        examples = {}
        
        # Common API doc patterns
        api_keys = ['endpoints', 'paths', 'operations', 'methods', 'apis', 'resources']
        
        for key in api_keys:
            if key in data:
                examples[key] = self._get_limited_sample(data[key], 3)
        
        # Look for OpenAPI/Swagger patterns
        if 'openapi' in data or 'swagger' in data:
            if 'paths' in data:
                examples['paths'] = self._get_limited_sample(data['paths'], 2)
            if 'components' in data and 'schemas' in data['components']:
                examples['schemas'] = self._get_limited_sample(data['components']['schemas'], 2)
        
        return examples
    
    def _extract_schema_patterns(self, data: Dict) -> Dict[str, Any]:
        """Extract schema/structure patterns from JSON data"""
        patterns = {}
        
        # Look for schema definitions
        schema_keys = ['schema', 'schemas', 'definitions', 'models', 'types']
        
        for key in schema_keys:
            if key in data:
                patterns[key] = self._get_limited_sample(data[key], 2)
        
        # Extract request/response patterns
        if isinstance(data, dict):
            for key, value in data.items():
                if 'request' in key.lower() or 'response' in key.lower():
                    patterns[key] = self._get_limited_sample(value, 1)
        
        return patterns
    
    def _get_limited_sample(self, data: Any, limit: int) -> Any:
        """Get a limited sample of data structure"""
        if isinstance(data, dict):
            items = list(data.items())[:limit]
            return dict(items)
        elif isinstance(data, list):
            return data[:limit]
        else:
            return data
    
    def _sample_text_file(self, file_path: str) -> List[DataSample]:
        """Sample text/markdown file with character limits"""
        samples = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # If file is small enough, use whole content
            if len(content) <= self.md_chunk_size:
                samples.append(DataSample(
                    source_path=file_path,
                    sample_type="full_content",
                    content=content,
                    metadata={"total_chars": len(content)}
                ))
            else:
                # Sample from beginning, middle, and end
                chunk_size = self.md_chunk_size
                
                # Beginning
                samples.append(DataSample(
                    source_path=file_path,
                    sample_type="beginning",
                    content=content[:chunk_size],
                    metadata={"position": "start", "total_chars": len(content)}
                ))
                
                # Middle (if file is long enough)
                if len(content) > chunk_size * 3:
                    mid_start = len(content) // 2 - chunk_size // 2
                    samples.append(DataSample(
                        source_path=file_path,
                        sample_type="middle",
                        content=content[mid_start:mid_start + chunk_size],
                        metadata={"position": "middle", "total_chars": len(content)}
                    ))
                
                # End
                samples.append(DataSample(
                    source_path=file_path,
                    sample_type="end",
                    content=content[-chunk_size:],
                    metadata={"position": "end", "total_chars": len(content)}
                ))
        
        except Exception as e:
            logger.warning(f"Error sampling text file {file_path}: {e}")
        
        return samples
    
    def _sample_config_file(self, file_path: str) -> List[DataSample]:
        """Sample configuration files"""
        samples = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Config files are usually small, include full content
            if len(content) <= 2000:
                samples.append(DataSample(
                    source_path=file_path,
                    sample_type="config",
                    content=content,
                    metadata={"file_type": Path(file_path).suffix}
                ))
        
        except Exception as e:
            logger.warning(f"Error sampling config file {file_path}: {e}")
        
        return samples
    
    async def _analyze_data_patterns(self, file_type: str, samples: List[DataSample]) -> List[DataPattern]:
        """Analyze samples to identify patterns"""
        if not samples:
            return []
        
        # Combine samples for analysis
        combined_content = "\\n\\n=== SAMPLE ===\\n\\n".join([
            f"File: {sample.source_path}\\nType: {sample.sample_type}\\nContent:\\n{sample.content}"
            for sample in samples[:5]  # Limit to 5 samples
        ])
        
        prompt = self._get_pattern_analysis_prompt(file_type)
        
        try:
            result = await self.llm_router.analyze_content(
                combined_content, ContentType.TEXT, prompt
            )
            
            # Parse patterns from result
            patterns = self._parse_pattern_analysis(result, file_type)
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing patterns for {file_type}: {e}")
            return []
    
    def _get_pattern_analysis_prompt(self, file_type: str) -> str:
        """Get pattern analysis prompt based on file type"""
        base_prompt = f"""Analyze these {file_type} samples and identify key patterns for knowledge extraction.

Focus on:
1. **Data Structure Patterns**: What are the common structures and formats?
2. **Content Patterns**: What types of information are present?
3. **Use Case Patterns**: What would someone want to learn from this data?
4. **Knowledge Extraction Goals**: What tutorials or guides could be generated?

For each pattern, provide:
- **Pattern Type**: (structure/content/integration/workflow)
- **Description**: What the pattern represents
- **Examples**: Key examples from the data
- **Knowledge Value**: What someone could learn from this

Provide insights that would help generate a comprehensive SOURCE_ANALYSIS for knowledge extraction."""
        
        if file_type == 'json_api_docs':
            base_prompt += """

Specifically for API documentation, look for:
- API endpoint patterns and structures
- Request/response formats
- Authentication patterns
- Integration workflows
- Common use cases and examples"""
        
        return base_prompt
    
    def _parse_pattern_analysis(self, analysis: str, file_type: str) -> List[DataPattern]:
        """Parse LLM analysis into DataPattern objects"""
        patterns = []
        
        # Simple parsing - look for pattern sections
        sections = analysis.split('\\n\\n')
        
        for section in sections:
            if 'pattern' in section.lower() and len(section) > 50:
                # Try to extract pattern info
                lines = section.split('\\n')
                pattern_type = file_type
                description = section[:200]  # First 200 chars as description
                examples = []
                
                # Look for examples in the section
                for line in lines:
                    if 'example' in line.lower() and len(line) > 20:
                        examples.append(line.strip())
                
                patterns.append(DataPattern(
                    pattern_type=pattern_type,
                    description=description,
                    examples=examples[:3],  # Max 3 examples
                    confidence=0.8
                ))
        
        # If no patterns found, create a general one
        if not patterns:
            patterns.append(DataPattern(
                pattern_type=file_type,
                description=f"General patterns found in {file_type}",
                examples=[analysis[:100]],  # First 100 chars
                confidence=0.6
            ))
        
        return patterns[:5]  # Max 5 patterns per file type