# Make Know Pipe: Knowledge Library Generator

A simplified system that extracts knowledge from codebases and generates comprehensive .md tutorial libraries.

## Vision

Transform codebases into educational knowledge libraries where each .md file teaches "how to build X" based on real implementations.

## Workflow

```
Input Sources → Analysis → Knowledge Extraction → .md Library Generation
```

## Project Structure

```
make_know_pipe/
├── intake/
│   ├── SOURCE_ANALYSIS.md      # Input template (like INITIAL.md)
│   └── extraction_plan.md      # Analysis plan (like PRP)
├── extractors/
│   ├── code_analyzer.py        # Extract patterns from code
│   ├── doc_processor.py        # Process documentation  
│   ├── api_analyzer.py         # Analyze API structures
│   └── multimodal_processor.py # Images, PDFs, logs
├── generators/
│   ├── tutorial_generator.py   # "How to build X" guides
│   ├── pattern_generator.py    # Reusable code patterns
│   └── gotcha_generator.py     # Common pitfalls docs
├── knowledge_library/          # Generated .md files
│   ├── how_to_build/          # Step-by-step guides
│   ├── patterns/              # Implementation patterns  
│   ├── architecture/          # System design docs
│   └── gotchas/              # Pitfalls and solutions
└── simple_runner.py          # Simple orchestration
```

## Core Philosophy

- **Educational Focus**: Each .md file teaches how to build something
- **Real-World Based**: Extracted from actual working systems
- **Comprehensive**: Implementation + architecture + gotchas
- **Context Engineering Workflow**: Based on proven Gemini patterns

## Quick Start

### 🤖 **Auto-Discovery Mode** (Recommended)

Let the system automatically discover your data patterns and generate contextual analysis:

```bash
# 1. Setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# 2. Auto-discover and generate
python auto_runner.py data/your_data "Your use case description"

# 3. Explore generated knowledge
ls knowledge_library/
ls intake/auto_generated_analysis.md  # See the contextual analysis
```

**Example for JSON API docs:**
```bash
python auto_runner.py data/apps "500 JSON files containing API docs for make.com integrations - need to build app copilot"
```

### 📋 **Manual Mode** (Traditional)

For more control over the analysis configuration:

```bash
# 1. Setup environment
pip install -r requirements.txt
cp .env.example .env

# 2. Configure analysis manually
cp intake/SOURCE_ANALYSIS.md intake/my_project_analysis.md
# Edit with your specific paths and goals

# 3. Run extraction
python simple_runner.py intake/my_project_analysis.md
```

## Example Workflow

```bash
# 1. Setup
git clone <this-repo>
cd make_know_pipe
pip install -r requirements.txt

# 2. Configure your API keys
echo "GROQ_API_KEY=your_key_here" > .env
echo "GEMINI_API_KEY=your_key_here" >> .env

# 3. Fill out analysis template
cp intake/EXAMPLE_filled_analysis.md intake/my_analysis.md
# Edit intake/my_analysis.md with your project details

# 4. Generate knowledge library
python simple_runner.py intake/my_analysis.md

# 5. Read generated tutorials
open knowledge_library/how_to_build/
```

## Generated Output Examples

- `how_to_build/user_authentication_system.md`
- `patterns/jwt_token_management.md`
- `architecture/microservices_communication.md`
- `gotchas/database_connection_pitfalls.md`