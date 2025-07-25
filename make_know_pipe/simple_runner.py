#!/usr/bin/env python3
"""
Simple Runner for Make Know Pipe

A straightforward orchestration script that runs the knowledge extraction
and tutorial generation process based on SOURCE_ANALYSIS.md input.
"""

import asyncio
import os
import sys
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our modules
from extractors.llm_router import LLMRouter
from extractors.code_analyzer import CodeAnalyzer
from extractors.doc_processor import DocProcessor
from extractors.multimodal_processor import MultimodalProcessor
from generators.tutorial_generator import TutorialGenerator

class MakeKnowPipe:
    """Main orchestrator for the knowledge extraction pipeline"""
    
    def __init__(self, source_analysis_file: str = "./intake/SOURCE_ANALYSIS.md"):
        self.source_analysis_file = Path(source_analysis_file)
        self.llm_router = LLMRouter()
        
        # Initialize processors
        self.code_analyzer = CodeAnalyzer(self.llm_router)
        self.doc_processor = DocProcessor(self.llm_router)
        self.multimodal_processor = MultimodalProcessor(self.llm_router)
        
        # Initialize generator
        self.tutorial_generator = TutorialGenerator()
    
    async def run_full_pipeline(self):
        """Run the complete knowledge extraction and tutorial generation pipeline"""
        logger.info("🚀 Starting Make Know Pipe")
        
        # Check if LLM router is available
        if not self.llm_router.is_available():
            logger.error("❌ No LLM clients available. Please check your API keys.")
            logger.error("Set GROQ_API_KEY and/or GEMINI_API_KEY environment variables")
            return False
        
        # Check if source analysis file exists
        if not self.source_analysis_file.exists():
            logger.error(f"❌ Source analysis file not found: {self.source_analysis_file}")
            logger.error("Please fill out the SOURCE_ANALYSIS.md template first")
            return False
        
        try:
            # Parse source analysis file
            logger.info("📋 Parsing source analysis configuration...")
            config = await self._parse_source_analysis()
            
            if not config:
                logger.error("❌ Could not parse source analysis configuration")
                return False
            
            # Phase 1: Extract knowledge from all sources
            logger.info("🔍 Phase 1: Extracting knowledge from sources...")
            
            # Extract from code
            logger.info("💻 Analyzing source code...")
            code_patterns = {}
            if config.get('code_sources'):
                code_patterns = await self.code_analyzer.extract_implementation_patterns(
                    config['code_sources']
                )
                logger.info(f"Found patterns in {len(code_patterns)} feature areas")
            
            # Extract from documentation
            logger.info("📚 Processing documentation...")
            doc_insights = {}
            if config.get('doc_sources'):
                doc_insights = await self.doc_processor.extract_documentation_knowledge(
                    config['doc_sources']
                )
                logger.info(f"Extracted insights from {len(doc_insights)} document types")
            
            # Extract from multimodal sources
            logger.info("🎨 Processing images, PDFs, and logs...")
            multimodal_insights = {}
            if config.get('multimodal_sources'):
                multimodal_insights = await self.multimodal_processor.process_multimodal_sources(
                    config['multimodal_sources']
                )
                logger.info(f"Processed {len(multimodal_insights)} types of multimodal content")
            
            # Phase 2: Generate tutorial library
            logger.info("📝 Phase 2: Generating tutorial library...")
            
            generated_guides = await self.tutorial_generator.generate_all_tutorials(
                code_patterns, doc_insights, multimodal_insights
            )
            
            # Summary
            logger.info("✅ Make Know Pipe completed successfully!")
            logger.info(f"📊 Generated {len(generated_guides)} tutorial guides")
            
            # Display results
            self._display_results(generated_guides, code_patterns, doc_insights, multimodal_insights)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            logger.exception("Full error details:")
            return False
    
    async def _parse_source_analysis(self) -> dict:
        """Parse the SOURCE_ANALYSIS.md file to extract configuration"""
        try:
            with open(self.source_analysis_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            config = {
                'code_sources': [],
                'doc_sources': [],
                'multimodal_sources': []
            }
            
            # Simple parsing - look for directory/file paths
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                # Identify sections
                if 'PRIMARY SOURCE CODE' in line.upper():
                    current_section = 'code'
                elif 'DOCUMENTATION SOURCES' in line.upper():
                    current_section = 'doc'
                elif any(keyword in line.upper() for keyword in ['EXECUTION DATA', 'VISUAL MATERIALS', 'API & INTEGRATION']):
                    current_section = 'multimodal'
                
                # Extract paths (lines that look like paths)
                elif line.startswith('- ') and ('/' in line or '\\' in line):
                    # Extract path from bullet point
                    path_part = line[2:].strip()
                    if ':' in path_part:
                        path_part = path_part.split(':')[1].strip()
                    
                    # Remove backticks and quotes
                    path_part = path_part.strip('`"\'')
                    
                    # Skip if it's just an example
                    if path_part.startswith('./'):
                        path_part = path_part[2:]
                    
                    # Add to appropriate section
                    if current_section == 'code':
                        config['code_sources'].append(path_part)
                    elif current_section == 'doc':
                        config['doc_sources'].append(path_part)
                    elif current_section == 'multimodal':
                        config['multimodal_sources'].append(path_part)
            
            # Filter out obvious examples and ensure paths exist
            config = self._validate_and_filter_paths(config)
            
            logger.info(f"Configuration: {len(config['code_sources'])} code sources, "
                       f"{len(config['doc_sources'])} doc sources, "
                       f"{len(config['multimodal_sources'])} multimodal sources")
            
            return config
            
        except Exception as e:
            logger.error(f"Error parsing source analysis: {e}")
            return {}
    
    def _validate_and_filter_paths(self, config: dict) -> dict:
        """Validate and filter paths to only include existing ones"""
        validated_config = {
            'code_sources': [],
            'doc_sources': [],
            'multimodal_sources': []
        }
        
        for section, paths in config.items():
            for path in paths:
                # Skip obvious examples
                if any(example in path.lower() for example in ['example', 'placeholder', 'your_', 'insert_']):
                    continue
                
                # Check if path exists
                if Path(path).exists():
                    validated_config[section].append(path)
                else:
                    logger.warning(f"Path not found, skipping: {path}")
        
        return validated_config
    
    def _display_results(self, guides, code_patterns, doc_insights, multimodal_insights):
        """Display results summary"""
        print("\n" + "="*60)
        print("📚 MAKE KNOW PIPE RESULTS")
        print("="*60)
        
        print(f"\n🎯 KNOWLEDGE EXTRACTED:")
        print(f"   • Code Patterns: {sum(len(patterns) for patterns in code_patterns.values())} patterns from {len(code_patterns)} features")
        print(f"   • Documentation: {sum(len(insights) for insights in doc_insights.values())} insights from {len(doc_insights)} doc types")
        print(f"   • Multimodal: {sum(len(insights) for insights in multimodal_insights.values())} insights from {len(multimodal_insights)} content types")
        
        print(f"\n📝 TUTORIALS GENERATED:")
        
        # Group guides by type
        guide_types = {}
        for guide in guides:
            if guide.tutorial_type not in guide_types:
                guide_types[guide.tutorial_type] = []
            guide_types[guide.tutorial_type].append(guide)
        
        for guide_type, type_guides in guide_types.items():
            print(f"   • {guide_type.replace('_', ' ').title()}: {len(type_guides)} guides")
            for guide in type_guides[:3]:  # Show first 3
                print(f"     - {guide.title}")
            if len(type_guides) > 3:
                print(f"     - ... and {len(type_guides) - 3} more")
        
        print(f"\n📁 OUTPUT LOCATION:")
        print(f"   {self.tutorial_generator.output_dir.absolute()}")
        
        print(f"\n🔍 TO EXPLORE:")
        print(f"   • How-to guides: {self.tutorial_generator.how_to_build_dir}")
        print(f"   • Code patterns: {self.tutorial_generator.patterns_dir}")
        print(f"   • Architecture: {self.tutorial_generator.architecture_dir}")
        print(f"   • Gotchas: {self.tutorial_generator.gotchas_dir}")
        
        print("\n" + "="*60)

async def main():
    """Main entry point"""
    print("🧠 Make Know Pipe - Knowledge Library Generator")
    print("Based on Gemini Context Engineering patterns")
    print("-" * 50)
    
    # Check for source analysis file
    source_analysis_path = "./intake/SOURCE_ANALYSIS.md"
    if len(sys.argv) > 1:
        source_analysis_path = sys.argv[1]
    
    # Initialize and run pipeline
    pipeline = MakeKnowPipe(source_analysis_path)
    success = await pipeline.run_full_pipeline()
    
    if success:
        print("\n🎉 Knowledge library generation completed successfully!")
        print("Check the knowledge_library/ directory for your generated tutorials.")
    else:
        print("\n❌ Pipeline failed. Check the logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())