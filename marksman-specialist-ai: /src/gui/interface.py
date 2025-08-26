#!/usr/bin/env python3
"""
GUI Interface for Markdown LSP Analyzer
Modern interface with real-time preview and file navigation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import webbrowser

# Try to import modern GUI libraries
try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
except ImportError:
    CTK_AVAILABLE = False

# Import our analyzer
try:
    from markdown_lsp_analyzer import FixedMarkdownAnalyzer
    from src.lm_studio_plugin import LMStudioPluginFixed
except ImportError as e:
    print(f"❌ Error importing analyzer modules: {e}")
    print("Please ensure markdown_lsp_analyzer.py and lm_studio_plugin.py are in the same directory")
    sys.exit(1)

class MarkdownAnalyzerGUI:
    """Modern GUI for Markdown LSP Analyzer"""
    
    def __init__(self):
        self.analyzer = None
        self.current_file = None
        self.analysis_result = None
        self.server_running = False
        
        # Setup GUI
        if CTK_AVAILABLE:
            self.setup_modern_gui()
        else:
            self.setup_classic_gui()
        
        # Start analyzer in background
        self.start_analyzer()
    
    def setup_modern_gui(self):
        """Setup modern GUI using CustomTkinter"""
        self.root = ctk.CTk()
        self.root.title("Markdown LSP Analyzer - Modern Interface")
        self.root.geometry("1400x900")
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Top toolbar
        self.toolbar = ctk.CTkFrame(self.main_frame)
        self.toolbar.pack(fill="x", padx=5, pady=5)
        
        # File operations
        self.btn_open = ctk.CTkButton(self.toolbar, text="📁 Open File", command=self.open_file)
        self.btn_open.pack(side="left", padx=5)
        
        self.btn_analyze = ctk.CTkButton(self.toolbar, text="🔍 Analyze", command=self.analyze_file)
        self.btn_analyze.pack(side="left", padx=5)
        
        self.btn_export = ctk.CTkButton(self.toolbar, text="💾 Export JSON", command=self.export_json)
        self.btn_export.pack(side="left", padx=5)
        
        self.btn_server = ctk.CTkButton(self.toolbar, text="🚀 Start Server", command=self.toggle_server)
        self.btn_server.pack(side="left", padx=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.toolbar, text="Ready")
        self.status_label.pack(side="right", padx=5)
        
        # Main content area
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel - File browser and navigation
        self.left_panel = ctk.CTkFrame(self.content_frame)
        self.left_panel.pack(side="left", fill="y", padx=5, pady=5)
        
        self.nav_label = ctk.CTkLabel(self.left_panel, text="📂 File Navigator", font=("Arial", 14, "bold"))
        self.nav_label.pack(pady=5)
        
        # File tree
        self.tree_frame = ctk.CTkFrame(self.left_panel)
        self.tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.file_tree = ttk.Treeview(self.tree_frame)
        self.file_tree.pack(fill="both", expand=True)
        self.file_tree.bind("<Double-1>", self.on_file_select)
        
        self.populate_file_tree()
        
        # Center panel - Editor
        self.center_panel = ctk.CTkFrame(self.content_frame)
        self.center_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        self.editor_label = ctk.CTkLabel(self.center_panel, text="📝 Markdown Editor", font=("Arial", 14, "bold"))
        self.editor_label.pack(pady=5)
        
        self.editor = ctk.CTkTextbox(self.center_panel, font=("Consolas", 12))
        self.editor.pack(fill="both", expand=True, padx=5, pady=5)
        self.editor.bind("<KeyRelease>", self.on_text_change)
        
        # Right panel - Analysis results
        self.right_panel = ctk.CTkFrame(self.content_frame)
        self.right_panel.pack(side="right", fill="y", padx=5, pady=5)
        
        self.results_label = ctk.CTkLabel(self.right_panel, text="📊 Analysis Results", font=("Arial", 14, "bold"))
        self.results_label.pack(pady=5)
        
        # Tabbed results
        self.results_notebook = ttk.Notebook(self.right_panel)
        self.results_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Content tab
        self.content_tab = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(self.content_tab, text="Content")
        
        self.content_results = ctk.CTkTextbox(self.content_tab, font=("Consolas", 10))
        self.content_results.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Structure tab
        self.structure_tab = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(self.structure_tab, text="Structure")
        
        self.structure_results = ctk.CTkTextbox(self.structure_tab, font=("Consolas", 10))
        self.structure_results.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Patterns tab
        self.patterns_tab = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(self.patterns_tab, text="Patterns")
        
        self.patterns_results = ctk.CTkTextbox(self.patterns_tab, font=("Consolas", 10))
        self.patterns_results.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Bottom status bar
        self.status_bar = ctk.CTkFrame(self.main_frame)
        self.status_bar.pack(fill="x", padx=5, pady=5)
        
        self.file_info = ctk.CTkLabel(self.status_bar, text="No file loaded")
        self.file_info.pack(side="left", padx=5)
        
        self.analysis_info = ctk.CTkLabel(self.status_bar, text="")
        self.analysis_info.pack(side="right", padx=5)
    
    def setup_classic_gui(self):
        """Setup classic GUI using standard Tkinter"""
        self.root = tk.Tk()
        self.root.title("Markdown LSP Analyzer - Classic Interface")
        self.root.geometry("1400x900")
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Toolbar
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(fill="x", pady=5)
        
        # Buttons
        self.btn_open = ttk.Button(self.toolbar, text="📁 Open File", command=self.open_file)
        self.btn_open.pack(side="left", padx=5)
        
        self.btn_analyze = ttk.Button(self.toolbar, text="🔍 Analyze", command=self.analyze_file)
        self.btn_analyze.pack(side="left", padx=5)
        
        self.btn_export = ttk.Button(self.toolbar, text="💾 Export JSON", command=self.export_json)
        self.btn_export.pack(side="left", padx=5)
        
        self.btn_server = ttk.Button(self.toolbar, text="🚀 Start Server", command=self.toggle_server)
        self.btn_server.pack(side="left", padx=5)
        
        # Status
        self.status_label = ttk.Label(self.toolbar, text="Ready")
        self.status_label.pack(side="right", padx=5)
        
        # Main content with paned window
        self.paned = ttk.PanedWindow(self.main_frame, orient="horizontal")
        self.paned.pack(fill="both", expand=True, pady=5)
        
        # Left panel
        self.left_frame = ttk.Frame(self.paned)
        self.paned.add(self.left_frame, weight=1)
        
        ttk.Label(self.left_frame, text="📂 File Navigator", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.file_tree = ttk.Treeview(self.left_frame)
        self.file_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.file_tree.bind("<Double-1>", self.on_file_select)
        
        self.populate_file_tree()
        
        # Center panel
        self.center_frame = ttk.Frame(self.paned)
        self.paned.add(self.center_frame, weight=3)
        
        ttk.Label(self.center_frame, text="📝 Markdown Editor", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.editor = tk.Text(self.center_frame, font=("Consolas", 12), wrap="word")
        editor_scroll = ttk.Scrollbar(self.center_frame, orient="vertical", command=self.editor.yview)
        self.editor.configure(yscrollcommand=editor_scroll.set)
        
        self.editor.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        editor_scroll.pack(side="right", fill="y")
        
        self.editor.bind("<KeyRelease>", self.on_text_change)
        
        # Right panel
        self.right_frame = ttk.Frame(self.paned)
        self.paned.add(self.right_frame, weight=2)
        
        ttk.Label(self.right_frame, text="📊 Analysis Results", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Results notebook
        self.results_notebook = ttk.Notebook(self.right_frame)
        self.results_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Content tab
        content_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(content_frame, text="Content")
        
        self.content_results = tk.Text(content_frame, font=("Consolas", 10), wrap="word")
        content_scroll = ttk.Scrollbar(content_frame, orient="vertical", command=self.content_results.yview)
        self.content_results.configure(yscrollcommand=content_scroll.set)
        
        self.content_results.pack(side="left", fill="both", expand=True)
        content_scroll.pack(side="right", fill="y")
        
        # Structure tab
        structure_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(structure_frame, text="Structure")
        
        self.structure_results = tk.Text(structure_frame, font=("Consolas", 10), wrap="word")
        struct_scroll = ttk.Scrollbar(structure_frame, orient="vertical", command=self.structure_results.yview)
        self.structure_results.configure(yscrollcommand=struct_scroll.set)
        
        self.structure_results.pack(side="left", fill="both", expand=True)
        struct_scroll.pack(side="right", fill="y")
        
        # Patterns tab
        patterns_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(patterns_frame, text="Patterns")
        
        self.patterns_results = tk.Text(patterns_frame, font=("Consolas", 10), wrap="word")
        patterns_scroll = ttk.Scrollbar(patterns_frame, orient="vertical", command=self.patterns_results.yview)
        self.patterns_results.configure(yscrollcommand=patterns_scroll.set)
        
        self.patterns_results.pack(side="left", fill="both", expand=True)
        patterns_scroll.pack(side="right", fill="y")
        
        # Status bar
        self.status_bar = ttk.Frame(self.main_frame)
        self.status_bar.pack(fill="x", pady=5)
        
        self.file_info = ttk.Label(self.status_bar, text="No file loaded")
        self.file_info.pack(side="left")
        
        self.analysis_info = ttk.Label(self.status_bar, text="")
        self.analysis_info.pack(side="right")
    
    def populate_file_tree(self):
        """Populate file tree with markdown files"""
        try:
            # Clear existing items
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            # Add current directory
            current_dir = Path(".")
            self.add_directory_to_tree("", current_dir, ".")
            
        except Exception as e:
            self.update_status(f"Error loading files: {e}")
    
    def add_directory_to_tree(self, parent, path, name):
        """Add directory and files to tree"""
        try:
            dir_id = self.file_tree.insert(parent, "end", text=name, values=[str(path)], open=True)
            
            # Add markdown files
            for file_path in sorted(path.glob("*.md")):
                if file_path.is_file():
                    self.file_tree.insert(dir_id, "end", text=file_path.name, values=[str(file_path)])
            
            # Add subdirectories
            for subdir in sorted(path.glob("*")):
                if subdir.is_dir() and not subdir.name.startswith('.'):
                    self.add_directory_to_tree(dir_id, subdir, subdir.name)
                    
        except Exception as e:
            print(f"Error adding directory {path}: {e}")
    
    def on_file_select(self, event):
        """Handle file selection from tree"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            file_path = self.file_tree.item(item, "values")[0]
            
            if Path(file_path).is_file() and file_path.endswith('.md'):
                self.load_file(file_path)
    
    def open_file(self):
        """Open file dialog and load selected file"""
        file_path = filedialog.askopenfilename(
            title="Select Markdown File",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """Load file into editor"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clear and populate editor
            if CTK_AVAILABLE:
                self.editor.delete("1.0", "end")
                self.editor.insert("1.0", content)
            else:
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", content)
            
            self.current_file = file_path
            self.update_file_info()
            self.update_status(f"Loaded: {Path(file_path).name}")
            
            # Auto-analyze if small file
            if len(content) < 10000:
                self.analyze_file()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file: {e}")
    
    def on_text_change(self, event=None):
        """Handle text changes in editor"""
        if self.current_file:
            self.update_file_info("Modified")
    
    def update_file_info(self, status=""):
        """Update file information in status bar"""
        if self.current_file:
            file_name = Path(self.current_file).name
            content = self.get_editor_content()
            word_count = len(content.split())
            char_count = len(content)
            
            info_text = f"{file_name} {status} - {word_count} words, {char_count} chars"
            
            if CTK_AVAILABLE:
                self.file_info.configure(text=info_text)
            else:
                self.file_info.config(text=info_text)
    
    def get_editor_content(self):
        """Get content from editor"""
        if CTK_AVAILABLE:
            return self.editor.get("1.0", "end-1c")
        else:
            return self.editor.get("1.0", tk.END + "-1c")
    
    def start_analyzer(self):
        """Start analyzer in background thread"""
        def init_analyzer():
            try:
                self.analyzer = FixedMarkdownAnalyzer()
                # Try to initialize (now sync)
                success = self.analyzer.initialize()
                
                if success:
                    self.update_status("Analyzer ready ✅")
                else:
                    self.update_status("Analyzer ready (no LSP) ⚠️")
                    
            except Exception as e:
                self.update_status(f"Analyzer error: {e}")
        
        thread = threading.Thread(target=init_analyzer, daemon=True)
        thread.start()
    
    def analyze_file(self):
        """Analyze current file"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please open a file first")
            return
        
        if not self.analyzer:
            messagebox.showerror("Error", "Analyzer not ready")
            return
        
        def run_analysis():
            try:
                self.update_status("Analyzing...")
                
                # Save current editor content to temp file if modified
                content = self.get_editor_content()
                
                # Create temporary file with current content
                temp_file = "temp_analysis.md"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Run analysis (now sync)
                analysis = self.analyzer.analyze_file_complete(temp_file)
                
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
                self.analysis_result = analysis
                self.display_analysis_results(analysis)
                self.update_status("Analysis complete ✅")
                
            except Exception as e:
                self.update_status(f"Analysis error: {e}")
                messagebox.showerror("Analysis Error", str(e))
        
        thread = threading.Thread(target=run_analysis, daemon=True)
        thread.start()
    
    def display_analysis_results(self, analysis):
        """Display analysis results in the GUI"""
        try:
            # Content tab
            content_info = f"""📄 CONTENT ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Title: {analysis.title}

📊 Statistics:
• Word count: {analysis.content.word_count}
• Character count: {analysis.content.character_count}
• Paragraph count: {len(analysis.content.paragraphs)}
• Sentence count: {len(analysis.content.sentences)}

📝 Content Preview:
{analysis.content.plain_text[:500]}{'...' if len(analysis.content.plain_text) > 500 else ''}

📋 Paragraphs:
"""
            
            for i, para in enumerate(analysis.content.paragraphs[:5]):
                content_info += f"\n{i+1}. [{para['type']}] {para['plain_text'][:100]}{'...' if len(para['plain_text']) > 100 else ''}"
            
            if len(analysis.content.paragraphs) > 5:
                content_info += f"\n... and {len(analysis.content.paragraphs) - 5} more paragraphs"
            
            self.set_text_widget(self.content_results, content_info)
            
            # Structure tab
            structure_info = f"""🏗️ STRUCTURE ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📑 Sections ({len(analysis.sections)}):
"""
            
            for section in analysis.sections:
                structure_info += f"\n{'  ' * (section.level - 1)}{'#' * section.level} {section.title}"
                if section.content:
                    structure_info += f"\n{'  ' * section.level}Content: {len(section.content)} chars"
            
            structure_info += f"""

🏷️ Headers ({len(analysis.headers)}):
"""
            for header in analysis.headers:
                structure_info += f"\nH{header['level']}: {header['text']} (line {header['line']})"
            
            structure_info += f"""

🔗 Links ({len(analysis.links)}):
"""
            for link in analysis.links[:10]:
                structure_info += f"\n• {link['text']} → {link['url']}"
            
            if len(analysis.links) > 10:
                structure_info += f"\n... and {len(analysis.links) - 10} more links"
            
            structure_info += f"""

💾 Code Blocks ({len(analysis.code_blocks)}):
"""
            for code in analysis.code_blocks:
                structure_info += f"\n• {code['language']}: {code['line_count']} lines"
            
            structure_info += f"""

📊 Tables: {len(analysis.tables)}
📋 Lists: {len(analysis.lists)}
🖼️ Images: {len(analysis.images)}
"""
            
            self.set_text_widget(self.structure_results, structure_info)
            
            # Patterns tab
            patterns_info = f"""🔍 PATTERN ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👁️ Hidden Zones ({len(analysis.hidden_zones)}):
"""
            
            for zone in analysis.hidden_zones:
                patterns_info += f"\n• {zone['type']}: {zone['content'][:100]}{'...' if len(zone['content']) > 100 else ''}"
            
            patterns_info += f"""

🔮 Detected Patterns:
"""
            
            # Defensive normalization for patterns (in case of old analysis data)
            patterns_dict = analysis.patterns
            if isinstance(analysis.patterns, list):
                patterns_dict = {"all": analysis.patterns}  # Normalize to dict if list
            
            total_patterns = sum(len(v) for v in patterns_dict.values())
            patterns_info += f"\nTotal patterns found: {total_patterns}\n"
            
            for pattern_type, matches in patterns_dict.items():
                if matches:
                    patterns_info += f"\n{pattern_type.replace('_', ' ').title()} ({len(matches)}):"
                    for match in matches[:5]:
                        patterns_info += f"\n  • {match['match'][:80]}{'...' if len(match['match']) > 80 else ''}"
                    if len(matches) > 5:
                        patterns_info += f"\n  ... and {len(matches) - 5} more"
            
            patterns_info += f"""

🧠 Semantic Analysis:
• Document type: {analysis.semantic_analysis.get('primary_type', 'unknown')}
• Technologies mentioned: {', '.join(analysis.semantic_analysis.get('technologies', {}).get('languages', [])[:5])}
• TODO items: {len(analysis.semantic_analysis.get('todos', []))}
• Versions found: {', '.join(analysis.semantic_analysis.get('versions', [])[:3])}
"""
            
            self.set_text_widget(self.patterns_results, patterns_info)
            
            # Update analysis info
            analysis_text = f"Analysis: {analysis.content.word_count} words, {total_patterns} patterns, {len(analysis.sections)} sections"
            if CTK_AVAILABLE:
                self.analysis_info.configure(text=analysis_text)
            else:
                self.analysis_info.config(text=analysis_text)
            
        except Exception as e:
            messagebox.showerror("Display Error", f"Error displaying results: {e}")
    
    def set_text_widget(self, widget, text):
        """Set text in text widget (compatible with both GUI types)"""
        try:
            if CTK_AVAILABLE and hasattr(widget, 'delete'):
                widget.delete("1.0", "end")
                widget.insert("1.0", text)
            else:
                widget.delete("1.0", tk.END)
                widget.insert("1.0", text)
        except:
            # Fallback for different widget types
            try:
                widget.config(state='normal')
                widget.delete("1.0", tk.END)
                widget.insert("1.0", text)
                widget.config(state='disabled')
            except:
                pass
    
    def export_json(self):
        """Export analysis results to JSON"""
        if not self.analysis_result:
            messagebox.showwarning("Warning", "No analysis results to export")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export Analysis Results",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                json_output = self.analyzer.export_complete_json(self.analysis_result, file_path)
                messagebox.showinfo("Success", f"Analysis exported to {file_path}")
                self.update_status(f"Exported to {Path(file_path).name}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export analysis: {e}")
    
    def toggle_server(self):
        """Toggle API server on/off"""
        if not self.server_running:
            self.start_api_server()
        else:
            self.stop_api_server()
    
    def start_api_server(self):
        """Start API server in background"""
        def run_server():
            try:
                import uvicorn
                from src.lm_studio_plugin import LMStudioPluginFixed
                
                plugin = LMStudioPluginFixed()
                self.server_running = True
                
                # Update button
                if CTK_AVAILABLE:
                    self.btn_server.configure(text="🛑 Stop Server")
                else:
                    self.btn_server.config(text="🛑 Stop Server")
                
                self.update_status("API Server starting...")
                
                uvicorn.run(plugin.app, host="127.0.0.1", port=8000, log_level="warning")
                
            except Exception as e:
                self.update_status(f"Server error: {e}")
                self.server_running = False
                
                if CTK_AVAILABLE:
                    self.btn_server.configure(text="🚀 Start Server")
                else:
                    self.btn_server.config(text="🚀 Start Server")
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        
        # Show server info
        self.root.after(2000, lambda: self.show_server_info())
    
    def show_server_info(self):
        """Show server information"""
        if self.server_running:
            self.update_status("API Server running on http://localhost:8000 🌐")
            
            # Ask if user wants to open browser
            result = messagebox.askyesno(
                "Server Started", 
                "API Server is running on http://localhost:8000\n\nWould you like to open the API documentation in your browser?"
            )
            
            if result:
                webbrowser.open("http://localhost:8000/docs")
    
    def stop_api_server(self):
        """Stop API server"""
        # Note: In a real implementation, you'd need proper server shutdown
        self.server_running = False
        
        if CTK_AVAILABLE:
            self.btn_server.configure(text="🚀 Start Server")
        else:
            self.btn_server.config(text="🚀 Start Server")
        
        self.update_status("API Server stopped")
    
    def update_status(self, message):
        """Update status label"""
        try:
            if CTK_AVAILABLE:
                self.status_label.configure(text=message)
            else:
                self.status_label.config(text=message)
        except:
            print(f"Status: {message}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("🚀 Starting Markdown LSP Analyzer GUI...")
    
    # Check for dependencies
    missing_deps = []
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Please install required packages:")
        for dep in missing_deps:
            print(f"  pip install {dep}")
        return 1
    
    try:
        app = MarkdownAnalyzerGUI()
        app.run()
        return 0
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
        return 0
    except Exception as e:
        print(f"❌ Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())