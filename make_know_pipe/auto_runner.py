#!/usr/bin/env python3
"""
Auto Runner for Make Know Pipe

Enhanced runner that automatically discovers data patterns and generates
contextual SOURCE_ANALYSIS.md before running knowledge extraction.

Usage:
    python auto_runner.py data/apps "I have 500 JSON API docs for make.com integrations"
"""

import asyncio
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
from extractors.data_discovery import DataDiscovery
from extractors.code_analyzer import CodeAnalyzer
from extractors.doc_processor import DocProcessor
from extractors.multimodal_processor import MultimodalProcessor
from generators.source_analysis_generator import SourceAnalysisGenerator
from generators.tutorial_generator import TutorialGenerator

class AutoMakeKnowPipe:
    """Enhanced orchestrator with automatic data discovery and SOURCE_ANALYSIS generation"""
    
    def __init__(self):
        self.llm_router = LLMRouter()
        
        # Initialize discovery and generation
        self.data_discovery = DataDiscovery(self.llm_router)
        self.source_analysis_generator = SourceAnalysisGenerator(self.llm_router)
        
        # Initialize processors
        self.code_analyzer = CodeAnalyzer(self.llm_router)
        self.doc_processor = DocProcessor(self.llm_router)
        self.multimodal_processor = MultimodalProcessor(self.llm_router)
        
        # Initialize generator
        self.tutorial_generator = TutorialGenerator()
    
    async def run_auto_pipeline(self, data_dir: str, use_case_description: str = ""):
        """Run the complete auto-discovery and knowledge extraction pipeline"""
        logger.info("🚀 Starting Auto Make Know Pipe")
        
        # Check if LLM router is available
        if not self.llm_router.is_available():
            logger.error("❌ No LLM clients available. Please check your API keys.")
            logger.error("Set GROQ_API_KEY and/or GEMINI_API_KEY environment variables")
            return False
        
        # Check if data directory exists
        if not Path(data_dir).exists():
            logger.error(f"❌ Data directory not found: {data_dir}")
            return False
        
        try:
            # Phase 0: Auto-discover data patterns
            logger.info("🔍 Phase 0: Auto-discovering data patterns...")
            data_patterns = await self.data_discovery.discover_data_patterns(data_dir)
            
            if not data_patterns:
                logger.error("❌ No data patterns discovered")
                return False
            
            logger.info(f"✅ Discovered patterns in {len(data_patterns)} data types")
            
            # Phase 0.5: Generate contextual SOURCE_ANALYSIS.md
            logger.info("🎯 Phase 0.5: Generating contextual SOURCE_ANALYSIS.md...")
            source_analysis_content = await self.source_analysis_generator.generate_source_analysis(
                data_patterns, data_dir, use_case_description
            )
            
            # Save generated analysis
            analysis_file = await self.source_analysis_generator.save_generated_analysis(
                source_analysis_content, "./intake/auto_generated_analysis.md"
            )
            
            logger.info(f"✅ Generated contextual SOURCE_ANALYSIS.md")
            
            # Phase 1: Parse the generated analysis and extract knowledge
            logger.info("📋 Phase 1: Processing with generated analysis...")
            
            # Create source paths based on discovered patterns
            source_paths = self._create_source_paths_from_patterns(data_dir, data_patterns)
            
            # Extract knowledge from sources
            logger.info("🔍 Extracting knowledge from discovered sources...")
            
            code_patterns = {}
            doc_insights = {}
            multimodal_insights = {}
            
            # Process based on discovered data types
            if 'json_api_docs' in data_patterns:
                logger.info("💻 Processing JSON API documentation...")
                # Treat JSON API docs as structured data
                json_paths = [str(Path(data_dir).rglob('*.json'))]
                code_patterns['api_documentation'] = await self._process_json_as_structured_data(
                    list(Path(data_dir).rglob('*.json'))[:50]  # Limit to 50 files
                )
            
            if 'markdown_docs' in data_patterns or 'text_docs' in data_patterns:
                logger.info("📚 Processing documentation files...")
                doc_paths = []
                if 'markdown_docs' in data_patterns:
                    doc_paths.extend([str(f) for f in Path(data_dir).rglob('*.md')])
                if 'text_docs' in data_patterns:
                    doc_paths.extend([str(f) for f in Path(data_dir).rglob('*.txt')])
                
                if doc_paths:
                    doc_insights = await self.doc_processor.extract_documentation_knowledge(doc_paths[:20])
            
            # Phase 2: Generate tutorial library
            logger.info("📝 Phase 2: Generating contextual tutorial library...")
            
            generated_guides = await self.tutorial_generator.generate_all_tutorials(
                code_patterns, doc_insights, multimodal_insights
            )
            
            # Summary
            logger.info("✅ Auto Make Know Pipe completed successfully!")
            logger.info(f"📊 Generated {len(generated_guides)} tutorial guides")
            
            # Display results
            self._display_auto_results(generated_guides, data_patterns, source_paths, analysis_file)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Auto pipeline failed: {e}")
            logger.exception("Full error details:")
            return False
    
    def _create_source_paths_from_patterns(self, data_dir: str, data_patterns: Dict) -> Dict[str, List[str]]:
        """Create source paths based on discovered patterns"""
        source_paths = {
            'data_sources': [data_dir],
            'doc_sources': [],
            'multimodal_sources': []
        }
        
        data_path = Path(data_dir)
        
        # Add specific paths based on patterns
        if 'markdown_docs' in data_patterns:
            source_paths['doc_sources'].extend([str(f) for f in data_path.rglob('*.md')])
        
        if 'text_docs' in data_patterns:
            source_paths['doc_sources'].extend([str(f) for f in data_path.rglob('*.txt')])
        
        return source_paths
    
    async def _process_json_as_structured_data(self, json_files: List[Path]) -> List:
        """Process JSON files as structured API documentation data"""
        patterns = []
        
        # Sample a few JSON files to understand structure
        for json_file in json_files[:10]:  # Process max 10 files
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    # Read first 2000 characters to understand structure
                    sample_content = f.read(2000)
                
                # Create a pattern-like object for JSON API docs
                from extractors.code_analyzer import CodePattern
                pattern = CodePattern(
                    name=f"API Documentation - {json_file.stem}",
                    description=f"API documentation structure from {json_file.name}",
                    code_example=sample_content,
                    implementation_guide=f"This represents API documentation patterns found in {json_file.name}. "
                                        f"The structure shows how API endpoints, parameters, and responses are organized.",
                    file_path=str(json_file)
                )
                patterns.append(pattern)
                
            except Exception as e:
                logger.warning(f"Could not process JSON file {json_file}: {e}")
        
        return patterns
    
    def _display_auto_results(self, guides, data_patterns, source_paths, analysis_file):
        """Display auto-discovery results"""
        print("\\n" + "="*70)
        print("🤖 AUTO MAKE KNOW PIPE RESULTS")
        print("="*70)
        
        print(f"\\n🔍 DATA DISCOVERY:")
        for data_type, patterns in data_patterns.items():
            print(f"   • {data_type.replace('_', ' ').title()}: {len(patterns)} patterns discovered")
        
        print(f"\\n🎯 GENERATED ANALYSIS:")
        print(f"   • Contextual SOURCE_ANALYSIS.md: {analysis_file}")
        print(f"   • Tailored to your specific data structure and use case")
        
        print(f"\\n📝 TUTORIALS GENERATED:")
        
        # Group guides by type
        guide_types = {}
        for guide in guides:
            if guide.tutorial_type not in guide_types:
                guide_types[guide.tutorial_type] = []
            guide_types[guide.tutorial_type].append(guide)
        
        for guide_type, type_guides in guide_types.items():
            print(f"   • {guide_type.replace('_', ' ').title()}: {len(type_guides)} guides")
            for guide in type_guides[:2]:  # Show first 2
                print(f"     - {guide.title}")
            if len(type_guides) > 2:
                print(f"     - ... and {len(type_guides) - 2} more")
        
        print(f"\\n📁 OUTPUT LOCATIONS:")
        print(f"   • Generated Analysis: {analysis_file}")
        print(f"   • Tutorial Library: {self.tutorial_generator.output_dir.absolute()}")
        
        print(f"\\n🎉 NEXT STEPS:")
        print(f"   1. Review the auto-generated analysis: {analysis_file}")
        print(f"   2. Explore tutorials: {self.tutorial_generator.how_to_build_dir}")
        print(f"   3. Customize and iterate as needed")
        
        print("\\n" + "="*70)

async def main():
    """Main entry point for auto-discovery pipeline"""
    print("🤖 Auto Make Know Pipe - Intelligent Knowledge Discovery")
    print("Automatically discovers data patterns and generates contextual analysis")
    print("-" * 70)
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python auto_runner.py <data_directory> [use_case_description]")
        print("\\nExample:")
        print("  python auto_runner.py data/apps 'JSON API docs for make.com integrations'")
        sys.exit(1)
    
    data_dir = sys.argv[1]
    use_case_description = sys.argv[2] if len(sys.argv) > 2 else ""
    
    print(f"📂 Data Directory: {data_dir}")
    print(f"🎯 Use Case: {use_case_description}")
    print("-" * 70)
    
    # Initialize and run auto pipeline
    pipeline = AutoMakeKnowPipe()
    success = await pipeline.run_auto_pipeline(data_dir, use_case_description)
    
    if success:
        print("\\n🎉 Auto knowledge discovery completed successfully!")
        print("Check the knowledge_library/ directory for your generated tutorials.")
        print("Review intake/auto_generated_analysis.md for the contextual analysis.")
    else:
        print("\\n❌ Auto pipeline failed. Check the logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())