# Markdown LSP Analyzer

**Professional Markdown analysis tool with LSP integration, modern GUI, and complete content extraction**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.0+-purple.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

## 🎯 **Overview**

The Markdown LSP Analyzer is a comprehensive tool that provides:
- **Complete content extraction** (not just headers/titles)
- **Modern GUI interface** with real-time preview
- **Marksman LSP integration** for advanced language server analysis
- **JSON-based API** compatible with LM Studio
- **Pattern detection** for hidden zones and custom annotations
- **Batch processing** capabilities
- **Professional Python package** structure

**Budget**: 12,000 PKR ✅ **COMPLETED**  
**Platform**: Cross-platform (Windows, macOS, Linux) ✅  
**LM Studio**: Fully compatible ✅

## 🚀 **Quick Start**

### **One-Command Installation**
```bash
# Download and run the installation script
chmod +x install.sh && ./install.sh
```

### **Manual Installation**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install package in development mode
pip install -e .

# 3. Install GUI dependencies (optional)
pip install -e .[gui]
```

### **Launch Applications**
```bash
# Modern GUI Interface
marksman-gui

# Command Line Tool  
marksman-analyzer analyze document.md

# API Server (for LM Studio)
marksman-server
```

## 📋 **Features**

### ✅ **Complete Content Extraction**
Unlike other tools that only extract headers, this analyzer captures:
- **Full text content** - every word and paragraph
- **Plain text conversion** - markdown-free content
- **Sentence-level analysis** - individual sentences extracted
- **Paragraph metadata** - type, line numbers, word counts
- **Complete structure** - sections with their full content

### ✅ **Modern GUI Interface**
- **File navigator** - browse and select markdown files
- **Syntax-aware editor** - edit markdown with highlighting
- **Real-time analysis** - results update as you type
- **Tabbed results** - Content, Structure, and Patterns views
- **Export functionality** - save analysis as JSON
- **Server integration** - start/stop API server from GUI
- **Dark/Light themes** - modern CustomTkinter design

### ✅ **Advanced Pattern Detection**
- **Hidden zones**: HTML comments, collapsible sections
- **Custom annotations**: `[[wiki-links]]`, `@annotations()`, `::markers::`
- **Structural patterns**: Headers, lists, tables, code blocks
- **Technology detection**: Programming languages, frameworks
- **TODO/FIXME extraction**: Task and note identification
- **Semantic analysis**: Document type classification

### ✅ **LSP Integration**
- **Marksman server** integration for advanced analysis
- **JSON-RPC communication** like TypeScript Language Server
- **Document symbols** extraction
- **Real-time diagnostics** and suggestions
- **Workspace management** for multiple files

### ✅ **API & LM Studio Compatible**
- **REST API** with FastAPI
- **JSON schema** for structured responses
- **Batch processing** for multiple files
- **Health monitoring** and status endpoints
- **Interactive documentation** at `/docs`

## 🏗️ **Project Structure**

```
marksman-analyzer/
├── 📁 src/marksman_analyzer/          # Main package
│   ├── 📄 __init__.py                 # Package initialization
│   ├── 📄 cli.py                      # Command-line interface
│   ├── 📁 core/                       # Core analysis modules
│   │   ├── 📄 __init__.py
│   │   └── 📄 analyzer.py             # Main analyzer engine
│   ├── 📁 gui/                        # GUI interface
│   │   ├── 📄 __init__.py
│   │   └── 📄 interface.py            # Modern GUI application
│   └── 📁 api/                        # API server
│       ├── 📄 __init__.py
│       └── 📄 server.py               # FastAPI server
├── 📁 assets/                         # GUI assets
│   ├── 📁 icons/                      # Application icons
│   └── 📁 themes/                     # GUI themes
├── 📁 tests/                          # Test suite
│   ├── 📄 __init__.py
│   └── 📄 test_analyzer.py            # Automated tests
├── 📁 workspace/                      # Example files
│   ├── 📄 example.md                  # Basic example
│   └── 📄 complex_example.md          # Advanced example
├── 📁 docs/                           # Documentation
├── 📁 examples/                       # Usage examples
│   ├── 📄 python_client.py            # Python API client
│   └── 📄 curl_examples.sh            # cURL examples
├── 📄 setup.py                        # Package setup
├── 📄 pyproject.toml                  # Modern Python config
├── 📄 requirements.txt                # Dependencies
├── 📄 install.sh                      # Installation script
├── 📄 README.md                       # This file
└── 📄 LICENSE                         # MIT license
```

## 💻 **Usage Examples**

### **GUI Application**
```bash
# Launch the modern GUI
marksman-gui

# Open specific file
marksman-gui --file document.md
```

**GUI Features:**
- 📁 **File Navigator**: Browse and select markdown files
- ✏️ **Editor**: Edit markdown with syntax awareness
- 👁️ **Real-time Preview**: Analysis updates as you type
- 📊 **Results Tabs**: Content, Structure, Patterns views
- 💾 **Export**: Save analysis as JSON
- 🚀 **Server Control**: Start/stop API server

### **Command Line Interface**
```bash
# Analyze single file
marksman-analyzer analyze document.md

# Export analysis to JSON
marksman-analyzer analyze document.md --output analysis.json

# Analyze without LSP (faster)
marksman-analyzer analyze document.md --no-lsp

# Launch GUI from CLI
marksman-analyzer gui

# Start API server
marksman-analyzer server --port 8000
```

### **API Server Usage**
```bash
# Start server
marksman-server

# Or with custom settings
marksman-server --host 0.0.0.0 --port 8080
```

**API Endpoints:**
- `POST /analyze` - Complete file analysis
- `POST /content` - Content-only extraction
- `POST /patterns` - Pattern detection
- `POST /batch-analyze` - Multiple file processing
- `GET /health` - Service status
- `GET /docs` - Interactive documentation

### **Python API Usage**
```python
import asyncio
from marksman_analyzer.core.analyzer import FixedMarkdownAnalyzer

async def analyze_document():
    # Initialize analyzer
    analyzer = FixedMarkdownAnalyzer()
    await analyzer.initialize()
    
    # Analyze file - extracts ALL content
    analysis = await analyzer.analyze_file_complete("document.md")
    
    # Access complete content
    print(f"Title: {analysis.title}")
    print(f"Word count: {analysis.content.word_count}")
    print(f"Paragraphs: {len(analysis.content.paragraphs)}")
    print(f"Full text: {analysis.content.plain_text}")
    
    # Access structure
    print(f"Headers: {len(analysis.headers)}")
    print(f"Links: {len(analysis.links)}")
    print(f"Code blocks: {len(analysis.code_blocks)}")
    
    # Access patterns
    patterns_found = sum(len(v) for v in analysis.patterns.values())
    print(f"Patterns detected: {patterns_found}")
    
    # Export to JSON
    json_output = analyzer.export_complete_json(analysis, "output.json")
    
    await analyzer.shutdown()

# Run analysis
asyncio.run(analyze_document())
```

### **REST API Usage**
```python
import requests

# Analyze file via API
response = requests.post("http://localhost:8000/analyze", json={
    "file_path": "document.md",
    "extract_content": True,
    "include_patterns": True
})

if response.status_code == 200:
    analysis = response.json()
    data = analysis["data"]
    
    # Access extracted content
    content = data["content"]
    print(f"Word count: {content['statistics']['word_count']}")
    print(f"Raw content: {content['raw_content']}")
    print(f"Plain text: {content['plain_text']}")
    
    # Access structure
    structure = data["structure"]
    print(f"Headers: {len(structure['headers'])}")
    print(f"Sections: {len(structure['sections'])}")
```

### **cURL Examples**
```bash
# Analyze file
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"file_path": "workspace/example.md"}'

# Extract content only
curl -X POST "http://localhost:8000/content" \
     -H "Content-Type: application/json" \
     -d '{"file_path": "document.md", "extract_sections": true}'

# Detect patterns
curl -X POST "http://localhost:8000/patterns" \
     -H "Content-Type: application/json" \
     -d '{"file_path": "document.md"}'

# Health check
curl -X GET "http://localhost:8000/health"
```

## 📊 **Sample Analysis Output**

```json
{
  "status": "success",
  "data": {
    "analysis_info": {
      "version": "2.0.0",
      "timestamp": "2025-01-20T10:30:00",
      "file_path": "/path/to/document.md"
    },
    "content": {
      "raw_content": "# Title\n\nThis is the complete content...",
      "plain_text": "Title\n\nThis is the complete content without markdown...",
      "paragraphs": [
        {
          "content": "This is the first complete paragraph with **formatting**",
          "plain_text": "This is the first complete paragraph with formatting",
          "type": "text",
          "line_start": 3,
          "word_count": 8
        }
      ],
      "sentences": ["First sentence.", "Second sentence."],
      "statistics": {
        "word_count": 287,
        "character_count": 1543,
        "paragraph_count": 8,
        "sentence_count": 15
      }
    },
    "structure": {
      "sections": [
        {
          "title": "Introduction",
          "level": 2,
          "content": "Complete section content with all text...",
          "line_start": 5,
          "line_end": 12
        }
      ],
      "headers": [...],
      "links": [...],
      "code_blocks": [...],
      "tables": [...],
      "lists": [...]
    },
    "patterns": {
      "hidden_zones": [...],
      "custom_annotations": [...],
      "structural_patterns": [...]
    },
    "semantic_analysis": {
      "document_types": ["readme", "documentation"],
      "primary_type": "readme",
      "technologies": {
        "languages": ["python", "javascript"],
        "frameworks": ["fastapi", "react"]
      },
      "todos": [...],
      "complexity": {...}
    }
  }
}
```

## 🔧 **Installation Requirements**

### **System Requirements**
- **Python 3.8+** (3.9+ recommended)
- **pip** package manager
- **Git** (for installation)

### **Core Dependencies**
```txt
fastapi>=0.104.0           # REST API framework
uvicorn[standard]>=0.24.0  # ASGI server
pydantic>=2.5.0           # Data validation
aiofiles>=23.2.1          # Async file operations
requests>=2.31.0          # HTTP client
PyYAML>=6.0.1             # YAML processing
python-magic>=0.4.0       # File type detection
colorama>=0.4.0           # Console colors
```

### **GUI Dependencies (Optional)**
```txt
customtkinter>=5.0.0      # Modern GUI framework
Pillow>=9.0.0            # Image processing
```

### **LSP Dependencies (Optional)**
- **Marksman LSP Server** - Automatically installed by setup script

## 🛠️ **Development Setup**

### **For Contributors**
```bash
# Clone repository
git clone <repository-url>
cd marksman-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev,gui]

# Run tests
python -m pytest tests/

# Run linting
black src/
flake8 src/
```

### **Project Development**
```bash
# Install development dependencies
pip install -e .[dev]

# Available dev tools
pytest>=7.0.0            # Testing framework
black>=22.0.0            # Code formatting
flake8>=4.0.0            # Code linting
mypy>=1.0.0              # Type checking
```

## 🧪 **Testing**

### **Automated Tests**
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=marksman_analyzer

# Run specific test
python -m pytest tests/test_analyzer.py::TestMarkdownAnalyzer::test_content_extraction
```

### **Manual Testing**
```bash
# Test CLI
marksman-analyzer analyze workspace/example.md

# Test GUI
marksman-gui

# Test API
marksman-server
curl -X GET "http://localhost:8000/health"
```

## 🐳 **Docker Deployment**

### **Using Docker Compose**
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### **Manual Docker Build**
```bash
# Build image
docker build -t marksman-analyzer .

# Run container
docker run -p 8000:8000 -v ./workspace:/app/workspace marksman-analyzer
```

## 📚 **Documentation**

### **API Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### **Additional Resources**
- **Troubleshooting Guide**: `docs/troubleshooting.md`
- **API Usage Guide**: `docs/api_guide.md`
- **Example Scripts**: `examples/`

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Installation Problems**
```bash
# Python version too old
python3 --version  # Should be 3.8+

# Missing pip
python3 -m pip --version

# Package installation fails
pip install --upgrade pip
pip install -e . --no-cache-dir
```

#### **GUI Issues**
```bash
# GUI won't start
pip install customtkinter Pillow

# Import errors
pip install -e .[gui]
```

#### **Marksman LSP Issues**
```bash
# Check if Marksman is installed
marksman --version

# Install manually (Linux)
wget -O marksman https://github.com/artempyanykh/marksman/releases/latest/download/marksman-linux-x64
chmod +x marksman
sudo mv marksman /usr/local/bin/

# Install via Homebrew (macOS)
brew install marksman
```

#### **API Server Issues**
```bash
# Port already in use
marksman-server --port 8001

# Permission denied
sudo marksman-server --port 80
```

### **Debug Mode**
```bash
# Enable debug logging
export DEBUG_MODE=true
marksman-analyzer analyze document.md

# Check log files
tail -f marksman_analyzer.log
tail -f lm_studio_plugin.log
```

### **Getting Help**
1. Check the troubleshooting guide: `docs/troubleshooting.md`
2. Review log files for error details
3. Test with example files: `workspace/example.md`
4. Verify installation: `python -c "import marksman_analyzer; print('OK')"`

## 🤝 **Contributing**

### **How to Contribute**
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Make** your changes
4. **Add** tests for new functionality
5. **Run** tests: `python -m pytest`
6. **Format** code: `black src/`
7. **Submit** a pull request

### **Code Style**
- **Black** for code formatting
- **Type hints** for all functions
- **Docstrings** for all public methods
- **Tests** for new features
- **Error handling** for all operations

### **Areas for Contribution**
- **Additional file formats** (ReStructuredText, AsciiDoc)
- **More pattern types** (custom annotation systems)
- **GUI improvements** (themes, plugins)
- **Performance optimizations**
- **Documentation improvements**

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Markdown LSP Analyzer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🎯 **Project Status & Roadmap**

### **Current Status: ✅ PRODUCTION READY**
- ✅ Complete content extraction (not just headers)
- ✅ Modern GUI interface with real-time preview
- ✅ LSP integration with Marksman
- ✅ REST API compatible with LM Studio
- ✅ Pattern detection and semantic analysis
- ✅ Batch processing capabilities
- ✅ Professional package structure
- ✅ Comprehensive test suite
- ✅ Docker deployment ready
- ✅ Complete documentation

### **Roadmap**
- **v2.1**: Additional file format support
- **v2.2**: Plugin system for custom analyzers
- **v2.3**: Web-based GUI interface
- **v2.4**: Integration with more LSP servers
- **v3.0**: Machine learning-based analysis

## 📞 **Support & Contact**

### **Professional Support**
This project was delivered as part of a **12,000 PKR development contract** and includes:
- ✅ **Complete implementation** of all requirements
- ✅ **GUI interface** with modern design
- ✅ **Proper project structure** 
- ✅ **Fixed dependencies** and installation
- ✅ **Comprehensive documentation**
- ✅ **Professional testing suite**

### **Getting Help**
1. **Documentation**: Start with this README and `docs/` folder
2. **Examples**: Check `examples/` and `workspace/` folders  
3. **Issues**: Use the GitHub issue tracker
4. **Testing**: Run the test suite to verify installation

---

## 🏆 **Acknowledgments**

- **Marksman LSP** - Excellent Markdown language server
- **CustomTkinter** - Modern GUI framework
- **FastAPI** - High-performance API framework
- **Python Community** - Amazing ecosystem and tools

---

**⭐ If this project helps you, please give it a star!**

**📈 Production ready • 🛠️ Professional quality • 🎯 Complete solution**