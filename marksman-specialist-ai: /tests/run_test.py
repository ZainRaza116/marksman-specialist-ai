#!/usr/bin/env python3
"""
Automated Test Suite for Markdown LSP Analyzer
Comprehensive testing to verify all functionality works correctly
"""

import asyncio
import json
import time
import requests
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

class TestRunner:
    """Comprehensive test runner for the Markdown LSP Analyzer"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.server_process = None
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "data": data
        })
    
    def create_test_files(self):
        """Create test markdown files"""
        print("📁 Creating test files...")
        
        # Simple test file
        simple_content = """# Simple Test Document

This is a **simple test** document to verify basic functionality.

## Content Section

Here is some content that should be extracted completely:

- First item in list
- Second item with *italic text*
- Third item with `code`

The analyzer should extract ALL of this content, not just the headers.

### Code Example

```python
def test_function():
    return "This code should be detected"
```

End of document.
"""
        
        # Complex test file
        complex_content = "\n".join([
            "---",
            'title: "Complex Test Document"',
            'author: "Test Suite"',
            'tags: ["test", "complex", "analysis"]',
            'version: "1.0.0"',
            'date: "2025-01-20"',
            "---",
            "",
            "# Complex Test Document",
            "",
            "This document tests **all features** of the Markdown LSP Analyzer.",
            "",
            "<!-- TODO: This comment should be detected as a hidden zone -->",
            "",
            "## Main Content Section",
            "",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation.",
            "",
            "### Subsection with Various Elements",
            "",
            "Here we have multiple types of content:",
            "",
            "1. **Ordered list item** with formatting",
            "2. *Italic text* in list",
            "3. `Inline code` example",
            "",
            "#### Links and Images",
            "",
            "- [External Link](https://example.com)",
            "- [Another Link](https://test.com/page)",
            "",
            '![Test Image](https://example.com/image.png "Image title")',
            "",
            "### Code Blocks",
            "",
            "```javascript",
            "function testFunction() {",
            "    console.log(\"This is a JavaScript code block\");",
            "    return true;",
            "}",
            "```",
            "",
            "```python",
            "def another_test():",
            '    """This is a Python code block"""',
            '    data = {"key": "value"}',
            "    return data",
            "```",
            "",
            "### Tables",
            "",
            "| Column A | Column B | Column C |",
            "|----------|----------|----------|",
            "| Data 1   | Data 2   | Data 3   |",
            "| Value X  | Value Y  | Value Z  |",
            "| Test A   | Test B   | Test C   |",
            "",
            "### Hidden and Special Content",
            "",
            "<details>",
            "<summary>Click to expand hidden section</summary>",
            "",
            "This content is initially hidden but should be detected and extracted by the analyzer.",
            "",
            "- Hidden item 1",
            "- Hidden item 2",
            "- Hidden item 3",
            "",
            "</details>",
            "",
            "### Custom Annotations",
            "",
            "Text with [[wiki-link]] and @annotation(parameter) and ::custom-marker:: patterns.",
            "",
            "Some hashtags: #python #testing #markdown",
            "",
            "### Quotes and More",
            "",
            "> This is a blockquote that should be detected.",
            "> It spans multiple lines.",
            "",
            "<!-- Another hidden comment with TODO: Add more examples -->",
            "",
            "## Technology Mentions",
            "",
            "This document mentions several technologies:",
            "- Python programming language",
            "- JavaScript and TypeScript",
            "- Docker containers",
            "- React framework",
            "- FastAPI web framework",
            "",
            "## Conclusion",
            "",
            "This complex document contains:",
            "1. Complete text content in paragraphs",
            "2. Metadata in YAML frontmatter",
            "3. Various structural elements",
            "4. Hidden zones and comments",
            "5. Custom annotation patterns",
            "6. Technology references",
            "7. Multiple content types",
            "",
            "Everything should be extracted and analyzed properly.",
            "",
            "<!-- Final hidden comment -->"
        ])
        
        # Write test files
        with open("test_simple.md", "w", encoding="utf-8") as f:
            f.write(simple_content)
        
        with open("test_complex.md", "w", encoding="utf-8") as f:
            f.write(complex_content)
        
        # Create workspace directory and example
        os.makedirs("workspace", exist_ok=True)
        with open("workspace/example.md", "w", encoding="utf-8") as f:
            f.write("# Workspace Example\n\nThis is an example file in the workspace.\n")
        
        print("✅ Test files created successfully")
    
    def start_server(self) -> bool:
        """Start the analyzer server"""
        print("🚀 Starting analyzer server...")
        
        try:
            # Start server in background
            self.server_process = subprocess.Popen(
                [sys.executable, "lm_studio_plugin.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            max_wait = 30
            for i in range(max_wait):
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Server started successfully (took {i+1}s)")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    continue
            
            print("❌ Server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def stop_server(self):
        """Stop the analyzer server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🔄 Server stopped")
    
    def test_server_health(self):
        """Test server health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Server Health Check",
                    True,
                    f"Status: {data.get('status', 'unknown')}",
                    data
                )
            else:
                self.log_test(
                    "Server Health Check",
                    False,
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            self.log_test("Server Health Check", False, str(e))
    
    def test_simple_analysis(self):
        """Test simple file analysis"""
        try:
            payload = {"file_path": "test_simple.md"}
            response = requests.post(
                f"{self.base_url}/analyze",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if data.get("status") == "success" and "data" in data:
                    content_data = data["data"].get("content", {})
                    
                    # Check if content was extracted
                    raw_content = content_data.get("raw_content", "")
                    paragraphs = content_data.get("paragraphs", [])
                    word_count = content_data.get("statistics", {}).get("word_count", 0)
                    
                    if raw_content and paragraphs and word_count > 0:
                        self.log_test(
                            "Simple Analysis - Content Extraction",
                            True,
                            f"Extracted {word_count} words, {len(paragraphs)} paragraphs",
                            {"word_count": word_count, "paragraph_count": len(paragraphs)}
                        )
                    else:
                        self.log_test(
                            "Simple Analysis - Content Extraction",
                            False,
                            "Missing content data"
                        )
                    
                    # Check structure extraction
                    structure = data["data"].get("structure", {})
                    headers = structure.get("headers", [])
                    
                    if headers:
                        self.log_test(
                            "Simple Analysis - Structure Extraction",
                            True,
                            f"Found {len(headers)} headers"
                        )
                    else:
                        self.log_test(
                            "Simple Analysis - Structure Extraction",
                            False,
                            "No headers found"
                        )
                        
                else:
                    self.log_test(
                        "Simple Analysis",
                        False,
                        f"Invalid response structure: {data.get('status', 'unknown')}"
                    )
            else:
                self.log_test(
                    "Simple Analysis",
                    False,
                    f"HTTP {response.status_code}: {response.text[:100]}"
                )
                
        except Exception as e:
            self.log_test("Simple Analysis", False, str(e))
    
    def test_complex_analysis(self):
        """Test complex file analysis with all features"""
        try:
            payload = {
                "file_path": "test_complex.md",
                "extract_content": True,
                "include_patterns": True,
                "include_lsp": True
            }
            
            response = requests.post(
                f"{self.base_url}/analyze",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    analysis_data = data["data"]
                    
                    # Test content extraction
                    content = analysis_data.get("content", {})
                    stats = content.get("statistics", {})
                    
                    word_count = stats.get("word_count", 0)
                    paragraph_count = stats.get("paragraph_count", 0)
                    
                    if word_count > 100 and paragraph_count > 5:
                        self.log_test(
                            "Complex Analysis - Content",
                            True,
                            f"Rich content: {word_count} words, {paragraph_count} paragraphs"
                        )
                    else:
                        self.log_test(
                            "Complex Analysis - Content",
                            False,
                            f"Insufficient content: {word_count} words, {paragraph_count} paragraphs"
                        )
                    
                    # Test metadata extraction
                    metadata = analysis_data.get("document", {}).get("metadata", {})
                    if "title" in metadata or "author" in metadata:
                        self.log_test(
                            "Complex Analysis - Metadata",
                            True,
                            f"Metadata fields: {list(metadata.keys())}"
                        )
                    else:
                        self.log_test(
                            "Complex Analysis - Metadata",
                            False,
                            "No metadata extracted"
                        )
                    
                    # Test pattern detection
                    patterns = analysis_data.get("patterns", {})
                    total_patterns = sum(len(v) for v in patterns.values())
                    
                    if total_patterns > 5:
                        self.log_test(
                            "Complex Analysis - Patterns",
                            True,
                            f"Detected {total_patterns} patterns"
                        )
                    else:
                        self.log_test(
                            "Complex Analysis - Patterns",
                            False,
                            f"Only {total_patterns} patterns detected"
                        )
                    
                    # Test hidden zones
                    hidden_zones = analysis_data.get("hidden_zones", [])
                    if len(hidden_zones) >= 2:  # Should find comments
                        self.log_test(
                            "Complex Analysis - Hidden Zones",
                            True,
                            f"Found {len(hidden_zones)} hidden zones"
                        )
                    else:
                        self.log_test(
                            "Complex Analysis - Hidden Zones",
                            False,
                            f"Expected more hidden zones, found {len(hidden_zones)}"
                        )
                        
                else:
                    self.log_test(
                        "Complex Analysis",
                        False,
                        f"Analysis failed: {data.get('message', 'unknown error')}"
                    )
            else:
                self.log_test(
                    "Complex Analysis",
                    False,
                    f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Complex Analysis", False, str(e))
    
    def test_content_extraction_only(self):
        """Test content-only extraction endpoint"""
        try:
            payload = {
                "file_path": "test_simple.md",
                "extract_sections": True,
                "extract_text": True,
                "extract_metadata": True
            }
            
            response = requests.post(
                f"{self.base_url}/content",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    content_data = data["data"]["content"]
                    
                    # Check for complete content
                    raw_content = content_data.get("raw_content", "")
                    plain_text = content_data.get("plain_text", "")
                    
                    if raw_content and plain_text and len(raw_content) > len(plain_text):
                        self.log_test(
                            "Content Extraction Only",
                            True,
                            f"Raw: {len(raw_content)} chars, Plain: {len(plain_text)} chars"
                        )
                    else:
                        self.log_test(
                            "Content Extraction Only",
                            False,
                            "Content extraction incomplete"
                        )
                else:
                    self.log_test(
                        "Content Extraction Only",
                        False,
                        data.get("message", "unknown error")
                    )
            else:
                self.log_test(
                    "Content Extraction Only",
                    False,
                    f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Content Extraction Only", False, str(e))
    
    def test_pattern_detection(self):
        """Test pattern detection endpoint"""
        try:
            payload = {
                "file_path": "test_complex.md",
                "pattern_types": ["hidden_zones", "custom_annotations"]
            }
            
            response = requests.post(
                f"{self.base_url}/patterns",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    patterns = data["data"]["patterns"]
                    total_patterns = data["data"]["total_patterns"]
                    
                    if total_patterns > 0:
                        self.log_test(
                            "Pattern Detection",
                            True,
                            f"Detected {total_patterns} patterns"
                        )
                    else:
                        self.log_test(
                            "Pattern Detection",
                            False,
                            "No patterns detected"
                        )
                else:
                    self.log_test(
                        "Pattern Detection",
                        False,
                        data.get("message", "unknown error")
                    )
            else:
                self.log_test(
                    "Pattern Detection",
                    False,
                    f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Pattern Detection", False, str(e))
    
    def test_batch_analysis(self):
        """Test batch analysis endpoint"""
        try:
            payload = {
                "patterns": ["test_*.md"],
                "workspace_path": ".",
                "max_files": 10
            }
            
            response = requests.post(
                f"{self.base_url}/batch-analyze",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    files_processed = data["data"]["files_processed"]
                    
                    if files_processed >= 2:  # Should find our test files
                        self.log_test(
                            "Batch Analysis",
                            True,
                            f"Processed {files_processed} files"
                        )
                    else:
                        self.log_test(
                            "Batch Analysis",
                            False,
                            f"Only processed {files_processed} files"
                        )
                else:
                    self.log_test(
                        "Batch Analysis",
                        False,
                        data.get("message", "unknown error")
                    )
            else:
                self.log_test(
                    "Batch Analysis",
                    False,
                    f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Batch Analysis", False, str(e))
    
    def test_json_schema(self):
        """Test JSON schema endpoint"""
        try:
            response = requests.get(f"{self.base_url}/schema", timeout=10)
            
            if response.status_code == 200:
                schema = response.json()
                
                # Check for required schema elements
                if "$schema" in schema and "properties" in schema:
                    self.log_test(
                        "JSON Schema",
                        True,
                        "Valid JSON schema returned"
                    )
                else:
                    self.log_test(
                        "JSON Schema",
                        False,
                        "Invalid schema structure"
                    )
            else:
                self.log_test(
                    "JSON Schema",
                    False,
                    f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("JSON Schema", False, str(e))
    
    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        try:
            # Test non-existent file
            payload = {"file_path": "non_existent_file.md"}
            response = requests.post(
                f"{self.base_url}/analyze",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 404 or (response.status_code == 200 and 
                                               response.json().get("status") == "error"):
                self.log_test(
                    "Error Handling - Non-existent File",
                    True,
                    "Properly handled missing file"
                )
            else:
                self.log_test(
                    "Error Handling - Non-existent File",
                    False,
                    f"Unexpected response: {response.status_code}"
                )
            
            # Test invalid JSON
            try:
                response = requests.post(
                    f"{self.base_url}/analyze",
                    data="invalid json",
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 422:  # Validation error
                    self.log_test(
                        "Error Handling - Invalid JSON",
                        True,
                        "Properly handled invalid JSON"
                    )
                else:
                    self.log_test(
                        "Error Handling - Invalid JSON",
                        False,
                        f"Unexpected response: {response.status_code}"
                    )
            except:
                self.log_test(
                    "Error Handling - Invalid JSON",
                    True,
                    "Request properly rejected"
                )
                
        except Exception as e:
            self.log_test("Error Handling", False, str(e))
    
    def test_json_serialization(self):
        """Test that JSON response is properly serializable"""
        try:
            payload = {"file_path": "test_complex.md"}
            response = requests.post(
                f"{self.base_url}/analyze",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Try to serialize the response back to JSON
                try:
                    json_string = json.dumps(data, indent=2)
                    
                    # Verify it's valid JSON by parsing it back
                    parsed_back = json.loads(json_string)
                    
                    if parsed_back == data:
                        self.log_test(
                            "JSON Serialization",
                            True,
                            f"Response properly serializable ({len(json_string)} chars)"
                        )
                    else:
                        self.log_test(
                            "JSON Serialization",
                            False,
                            "Data changed during serialization"
                        )
                        
                except (TypeError, ValueError) as e:
                    self.log_test(
                        "JSON Serialization",
                        False,
                        f"Serialization error: {e}"
                    )
            else:
                self.log_test(
                    "JSON Serialization",
                    False,
                    f"No data to test (HTTP {response.status_code})"
                )
                
        except Exception as e:
            self.log_test("JSON Serialization", False, str(e))
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 STARTING COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        
        # Setup
        self.create_test_files()
        
        if not self.start_server():
            print("❌ Cannot start server, aborting tests")
            return False
        
        try:
            # Run all tests
            print("\n📋 Running API Tests...")
            self.test_server_health()
            self.test_json_schema()
            
            print("\n📄 Running Content Extraction Tests...")
            self.test_simple_analysis()
            self.test_complex_analysis()
            self.test_content_extraction_only()
            
            print("\n🔍 Running Pattern Detection Tests...")
            self.test_pattern_detection()
            
            print("\n📚 Running Batch Processing Tests...")
            self.test_batch_analysis()
            
            print("\n⚠️ Running Error Handling Tests...")
            self.test_error_handling()
            
            print("\n🔧 Running JSON Functionality Tests...")
            self.test_json_serialization()
            
        finally:
            self.stop_server()
        
        # Generate report
        self.generate_report()
        
        return all(result["success"] for result in self.test_results)
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n📄 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}: {result['message']}")
        
        # Save report to file
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "results": self.test_results
        }
        
        with open("test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Test report saved: test_report.json")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! System is fully functional.")
        else:
            print(f"\n⚠️ {failed_tests} tests failed. Check issues above.")

def main():
    """Main test function"""
    print("🚀 Markdown LSP Analyzer - Test Suite")
    print("Testing all functionality to ensure everything works correctly")
    print("-" * 60)
    
    # Check if required files exist
    required_files = ["markdown_lsp_analyzer.py", "lm_studio_plugin.py"]
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Please ensure all project files are in the current directory")
        return 1
    
    # Run tests
    runner = TestRunner()
    success = runner.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)