#!/usr/bin/env python3
"""
Markdown LSP Analyzer - AI Assistant for Marksman LSP Integration
VERSIÓN CORREGIDA - Extrae TODO el contenido, no solo títulos
Funciona completamente con JSON y todos los módulos

Author: Senior Developer with 15+ years experience
Budget: 12k PKR implementation
Target: LM Studio integration
"""

import json
import subprocess
import logging
import os
import re
import sys
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import time
from datetime import datetime
import threading
import asyncio
import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('markdown_analyzer.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MarkdownSection:
    """Estructura para secciones completas de Markdown"""
    title: str
    level: int
    content: str
    line_start: int
    line_end: int
    subsections: List['MarkdownSection']
    metadata: Dict[str, Any]

@dataclass
class MarkdownContent:
    """Estructura completa del contenido extraído"""
    raw_text: str
    plain_text: str
    paragraphs: List[Dict[str, Any]]
    sentences: List[str]
    word_count: int
    character_count: int

@dataclass
class MarkdownStructure:
    """Estructura completa de datos de Markdown - CORREGIDA"""
    title: str
    raw_content: str  # TODO EL CONTENIDO RAW
    content: MarkdownContent  # CONTENIDO PROCESADO
    sections: List[MarkdownSection]  # SECCIONES COMPLETAS CON CONTENIDO
    headers: List[Dict[str, Any]]
    links: List[Dict[str, str]]
    images: List[Dict[str, str]]
    code_blocks: List[Dict[str, str]]
    tables: List[Dict[str, Any]]
    lists: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    hidden_zones: List[Dict[str, Any]]
    patterns: Dict[str, List[Dict[str, Any]]]  # FIXED: Now dict for consistency
    semantic_analysis: Dict[str, Any]
    file_path: str
    analysis_timestamp: str
    lsp_symbols: List[Dict[str, Any]]  # Símbolos del LSP

class MarkdownContentExtractor:
    """Extractor completo de contenido - NO SOLO TÍTULOS"""
    
    def __init__(self):
        self.section_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.paragraph_pattern = re.compile(r'\n\s*\n')
        
    def extract_complete_content(self, content: str) -> MarkdownContent:
        """Extrae TODO el contenido del markdown"""
        logger.info("Extrayendo contenido completo del markdown...")
        
        # Texto raw completo
        raw_text = content
        
        # Texto plano (sin markdown)
        plain_text = self._convert_to_plain_text(content)
        
        # Extraer párrafos completos
        paragraphs = self._extract_paragraphs(content)
        
        # Extraer oraciones
        sentences = self._extract_sentences(plain_text)
        
        # Contar palabras y caracteres
        word_count = len(re.findall(r'\b\w+\b', plain_text))
        character_count = len(content)
        
        return MarkdownContent(
            raw_text=raw_text,
            plain_text=plain_text,
            paragraphs=paragraphs,
            sentences=sentences,
            word_count=word_count,
            character_count=character_count
        )
    
    def _convert_to_plain_text(self, content: str) -> str:
        """Convierte markdown a texto plano"""
        # Remover bloques de código
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`[^`]+`', '', content)
        
        # Remover enlaces pero mantener texto
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
        
        # Remover imágenes
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', content)
        
        # Remover markdown de formato
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*([^*]+)\*', r'\1', content)      # Italic
        content = re.sub(r'~~([^~]+)~~', r'\1', content)      # Strikethrough
        
        # Remover headers markdown
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
        
        # Remover listas
        content = re.sub(r'^\s*[-*+]\s+', '', content, flags=re.MULTILINE)
        content = re.sub(r'^\s*\d+\.\s+', '', content, flags=re.MULTILINE)
        
        # Remover comentarios HTML
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        # Limpiar espacios extras
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()
        
        return content
    
    def _extract_paragraphs(self, content: str) -> List[Dict[str, Any]]:
        """Extrae párrafos completos con metadatos"""
        paragraphs = []
        
        # Dividir por doble salto de línea
        raw_paragraphs = self.paragraph_pattern.split(content)
        
        line_number = 1
        for i, para in enumerate(raw_paragraphs):
            para = para.strip()
            if not para:
                continue
                
            # Contar líneas hasta este párrafo
            para_line_start = line_number
            para_line_end = line_number + para.count('\n')
            
            # Determinar tipo de párrafo
            para_type = self._determine_paragraph_type(para)
            
            paragraphs.append({
                'index': i,
                'content': para,
                'plain_text': self._convert_to_plain_text(para),
                'type': para_type,
                'line_start': para_line_start,
                'line_end': para_line_end,
                'word_count': len(re.findall(r'\b\w+\b', para)),
                'char_count': len(para)
            })
            
            line_number = para_line_end + 2  # +2 por el doble salto
        
        return paragraphs
    
    def _determine_paragraph_type(self, paragraph: str) -> str:
        """Determina el tipo de párrafo"""
        if re.match(r'^#{1,6}\s+', paragraph):
            return 'header'
        elif re.match(r'^\s*[-*+]\s+', paragraph):
            return 'list'
        elif re.match(r'^\s*\d+\.\s+', paragraph):
            return 'numbered_list'
        elif re.match(r'^```', paragraph):
            return 'code_block'
        elif re.match(r'^\s*\|.*\|', paragraph):
            return 'table'
        elif re.match(r'^>\s+', paragraph):
            return 'quote'
        else:
            return 'text'
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extrae oraciones del texto"""
        # Dividir por puntos, signos de exclamación y interrogación
        sentences = re.split(r'[.!?]+', text)
        
        # Limpiar y filtrar oraciones vacías
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def extract_sections_with_content(self, content: str) -> List[MarkdownSection]:
        """Extrae secciones completas CON TODO SU CONTENIDO"""
        logger.info("Extrayendo secciones completas con contenido...")
        
        sections = []
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for i, line in enumerate(lines):
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if header_match:
                # Guardar sección anterior si existe
                if current_section:
                    current_section.content = '\n'.join(current_content).strip()
                    current_section.line_end = i - 1
                    sections.append(current_section)
                
                # Crear nueva sección
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
                current_section = MarkdownSection(
                    title=title,
                    level=level,
                    content='',
                    line_start=i + 1,
                    line_end=i + 1,
                    subsections=[],
                    metadata={'header_line': i + 1}
                )
                current_content = []
            else:
                # Agregar contenido a la sección actual
                if current_section:
                    current_content.append(line)
        
        # Guardar última sección
        if current_section:
            current_section.content = '\n'.join(current_content).strip()
            current_section.line_end = len(lines)
            sections.append(current_section)
        
        # Procesar jerarquía de subsecciones
        sections = self._process_section_hierarchy(sections)
        
        return sections
    
    def _process_section_hierarchy(self, sections: List[MarkdownSection]) -> List[MarkdownSection]:
        """Procesa la jerarquía de secciones y subsecciones"""
        if not sections:
            return []
        
        result = []
        stack = []
        
        for section in sections:
            # Encontrar el nivel padre apropiado
            while stack and stack[-1].level >= section.level:
                stack.pop()
            
            if stack:
                # Es una subsección
                stack[-1].subsections.append(section)
            else:
                # Es una sección de nivel superior
                result.append(section)
            
            stack.append(section)
        
        return result

class FixedLSPClient:
    """Cliente LSP CORREGIDO - Maneja errores y funciona correctamente con un solo loop en thread dedicado"""
    
    def __init__(self, server_path: str = "marksman", workspace_path: str = "."):
        self.server_path = server_path
        self.workspace_path = Path(workspace_path).absolute()
        self.process: Optional[subprocess.Popen] = None  # Cambiado a sync Popen para compatibilidad
        self.request_id = 1
        self.initialized = False
        self.timeout = 10.0
        
        # Dedicated loop in background thread
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
    
    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def _run_async(self, coro):
        """Run async coro in the dedicated loop, synchronously"""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        try:
            return future.result(self.timeout)
        except concurrent.futures.TimeoutError:
            logger.error("Timeout en operación LSP")
            raise
    
    def start_server(self) -> bool:
        """Inicia el servidor Marksman LSP - CORREGIDO (sync wrapper)"""
        def _start():
            try:
                # Verificar si marksman está disponible
                result = subprocess.run([self.server_path, "--version"], 
                                     capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    logger.error(f"Marksman no encontrado en: {self.server_path}")
                    return False
                
                logger.info(f"Iniciando Marksman LSP server: {result.stdout.strip()}")
                
                # Iniciar servidor sync con Popen (para evitar attachment a loop específico)
                self.process = subprocess.Popen(
                    [self.server_path, "server"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.workspace_path,
                    text=True,
                    bufsize=1  # Line buffered
                )
                
                # Esperar un momento para que el servidor se inicie
                time.sleep(1)
                
                if self.process.poll() is not None:
                    stderr_output = self.process.stderr.read() if self.process.stderr else ""
                    logger.error(f"El servidor falló al iniciar: {stderr_output}")
                    return False
                
                logger.info(f"Marksman LSP server iniciado con PID: {self.process.pid}")
                return True
                
            except FileNotFoundError:
                logger.error(f"Marksman no encontrado. Instalar desde: https://github.com/artempyanykh/marksman/releases")
                return False
            except Exception as e:
                logger.error(f"Error al iniciar Marksman server: {e}")
                return False
        
        return _start()  # Sync call
    
    def send_request(self, method: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Envía petición JSON-RPC al servidor - CORREGIDO (sync wrapper)"""
        async def _send():
            if not self.process or self.process.poll() is not None:
                raise RuntimeError("LSP server no está ejecutándose")
            
            request = {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": method,
                "params": params or {}
            }
            
            self.request_id += 1
            
            # Formatear petición LSP
            request_json = json.dumps(request)
            request_content = f"Content-Length: {len(request_json)}\r\n\r\n{request_json}"
            
            try:
                # Enviar petición (sync via Popen)
                if self.process.stdin:
                    self.process.stdin.write(request_content)
                    self.process.stdin.flush()
                
                # Leer respuesta (async para no bloquear)
                response = await self._read_lsp_response_async()
                
                return response
                
            except Exception as e:
                logger.error(f"Error enviando petición LSP: {e}")
                return {"error": {"code": -2, "message": str(e)}}
        
        return self._run_async(_send())
    
    async def _read_lsp_response_async(self) -> Dict[str, Any]:
        """Lee respuesta LSP async"""
        if not self.process or not self.process.stdout:
            raise ConnectionError("Proceso LSP no disponible")
            
        # Leer header Content-Length
        header = ""
        while True:
            char = await asyncio.to_thread(self.process.stdout.read, 1)
            if not char:
                raise ConnectionError("Conexión LSP cerrada")
            header += char
            if header.endswith("\r\n\r\n"):
                break
        
        # Extraer longitud
        content_length = None
        for line in header.split('\r\n'):
            if line.startswith('Content-Length:'):
                content_length = int(line.split(':')[1].strip())
                break
        
        if content_length is None:
            raise ValueError("Content-Length header no encontrado")
        
        # Leer contenido JSON
        content = await asyncio.to_thread(self.process.stdout.read, content_length)
        response_data = json.loads(content)
        
        return response_data
    
    def initialize(self) -> bool:
        """Inicializa conexión LSP - CORREGIDO (sync wrapper)"""
        def _init():
            try:
                init_params = {
                    "processId": os.getpid(),
                    "rootUri": f"file://{self.workspace_path}",
                    "capabilities": {
                        "textDocument": {
                            "hover": {"contentFormat": ["markdown", "plaintext"]},
                            "completion": {"completionItem": {"snippetSupport": True}},
                            "definition": {},
                            "references": {},
                            "documentSymbol": {},
                            "publishDiagnostics": {}
                        },
                        "workspace": {
                            "didChangeWatchedFiles": {"dynamicRegistration": True},
                            "workspaceFolders": True
                        }
                    },
                    "initializationOptions": {},
                    "workspaceFolders": [{
                        "uri": f"file://{self.workspace_path}",
                        "name": "workspace"
                    }]
                }
                
                response = self.send_request("initialize", init_params)
                
                if "error" in response:
                    logger.error(f"Error en inicialización LSP: {response['error']}")
                    return False
                
                # Enviar notificación initialized
                self.send_notification("initialized", {})
                
                self.initialized = True
                logger.info("Cliente LSP inicializado correctamente")
                return True
                
            except Exception as e:
                logger.error(f"Error en inicialización LSP: {e}")
                return False
        
        return _init()
    
    def send_notification(self, method: str, params: Dict[str, Any] | None = None):
        """Envía notificación LSP (sync wrapper)"""
        def _send_notif():
            if not self.process or not self.process.stdin:
                raise RuntimeError("LSP server no disponible")
                
            notification = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params or {}
            }
            
            notification_json = json.dumps(notification)
            notification_content = f"Content-Length: {len(notification_json)}\r\n\r\n{notification_json}"
            
            self.process.stdin.write(notification_content)
            self.process.stdin.flush()
        
        _send_notif()
    
    def open_document(self, file_path: str, content: str) -> bool:
        """Abre documento en servidor LSP (sync)"""
        try:
            params = {
                "textDocument": {
                    "uri": f"file://{Path(file_path).absolute()}",
                    "languageId": "markdown",
                    "version": 1,
                    "text": content
                }
            }
            
            self.send_notification("textDocument/didOpen", params)
            return True
        except Exception as e:
            logger.error(f"Error abriendo documento: {e}")
            return False
    
    def get_document_symbols(self, file_path: str) -> List[Dict[str, Any]]:
        """Obtiene símbolos del documento desde LSP server (sync)"""
        try:
            params = {
                "textDocument": {
                    "uri": f"file://{Path(file_path).absolute()}"
                }
            }
            
            response = self.send_request("textDocument/documentSymbol", params)
            
            if "error" in response:
                logger.warning(f"Error obteniendo símbolos: {response['error']}")
                return []
            
            return response.get("result", [])
        except Exception as e:
            logger.error(f"Error obteniendo símbolos del documento: {e}")
            return []
    
    def shutdown(self):
        """Cierra servidor LSP correctamente (sync)"""
        if self.process and self.process.poll() is None:
            try:
                self.send_request("shutdown", {})
                self.send_notification("exit", {})
                
                # Esperar cierre del proceso
                try:
                    self.process.wait(timeout=5)
                except concurrent.futures.TimeoutError:
                    logger.warning("Timeout esperando cierre del servidor, terminando forzosamente")
                    self.process.terminate()
                    self.process.wait()
                
                logger.info("Servidor LSP cerrado correctamente")
            except Exception as e:
                logger.error(f"Error cerrando servidor LSP: {e}")
                if self.process:
                    self.process.terminate()
                    try:
                        self.process.wait()
                    except Exception:
                        pass

class FixedMarkdownPatternDetector:
    """Detector de patrones CORREGIDO - Encuentra TODO tipo de contenido"""
    
    def __init__(self):
        self.patterns = {
            'hidden_zones': [
                r'<!--\s*(.*?)\s*-->',  # Comentarios HTML
                r'<details[^>]*>(.*?)</details>',  # Secciones colapsables
                r'$$ comment $$:\s*#\s*$$ (.*?) $$',  # Comentarios markdown
                r'^\s*<!--.*?-->\s*$'  # Comentarios de línea
            ],
            'metadata_blocks': [
                r'^---\n(.*?)\n---',  # YAML frontmatter
                r'^\+\+\+\n(.*?)\n\+\+\+',  # TOML frontmatter
                r'^```(?:json|yaml|toml)\n(.*?)\n```'  # Bloques de datos
            ],
            'custom_annotations': [
                r'\[\[([^\]]+)\]\]',  # Enlaces wiki
                r'@(\w+)(?:\(([^)]+)\))?',  # Anotaciones custom
                r'::([^:]+)::',  # Marcadores custom
                r'#(\w+)(?:\s|$)',  # Hashtags
                r'\{\{([^}]+)\}\}',  # Variables
                r'%%([^%]+)%%'  # Marcadores especiales
            ],
            'structural_patterns': [
                r'^(#{1,6})\s+(.+)$',  # Headers
                r'^\s*[-*+]\s+(.+)$',  # Lista con viñetas
                r'^\s*\d+\.\s+(.+)$',  # Lista numerada
                r'^\s*\|.*\|$',  # Filas de tabla
                r'^```(\w+)?\n(.*?)\n```$',  # Bloques de código
                r'^>\s+(.+)$',  # Citas
                r'^\s*---+\s*$'  # Separadores
            ],
            'content_patterns': [
                r'\*\*([^*]+)\*\*',  # Texto en negrita
                r'\*([^*]+)\*',  # Texto en cursiva
                r'`([^`]+)`',  # Código inline
                r'~~([^~]+)~~',  # Texto tachado
                r'\[([^\]]+)\]\(([^)]+)\)',  # Enlaces
                r'!\[([^\]]*)\]\(([^)]+)\)',  # Imágenes
                r'https?://[^\s]+',  # URLs
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Emails
            ]
        }
    
    def detect_all_patterns(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """Detecta TODOS los patrones en el contenido"""
        logger.info("Detectando todos los patrones en el contenido...")
        
        detected = {}
        
        for pattern_type, pattern_list in self.patterns.items():
            detected[pattern_type] = []
            
            for pattern in pattern_list:
                try:
                    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                    for match in matches:
                        detected[pattern_type].append({
                            'pattern_type': pattern_type,
                            'pattern': pattern,
                            'match': match.group(0),
                            'groups': match.groups(),
                            'start_pos': match.start(),
                            'end_pos': match.end(),
                            'line_number': content[:match.start()].count('\n') + 1,
                            'context': self._extract_context(content, match.start(), match.end()),
                            'metadata': self._analyze_match_metadata(match.group(0), pattern_type)
                        })
                except re.error as e:
                    logger.warning(f"Error en patrón regex {pattern}: {e}")
                    continue
        
        return detected
    
    def _extract_context(self, content: str, start: int, end: int, context_size: int = 100) -> str:
        """Extrae contexto alrededor de una coincidencia"""
        context_start = max(0, start - context_size)
        context_end = min(len(content), end + context_size)
        return content[context_start:context_end].strip()
    
    def _analyze_match_metadata(self, match_text: str, pattern_type: str) -> Dict[str, Any]:
        """Analiza metadatos de una coincidencia"""
        metadata: Dict[str, Any] = {
            'length': len(match_text),
            'word_count': len(re.findall(r'\b\w+\b', match_text))
        }
        
        if pattern_type == 'structural_patterns':
            if match_text.startswith('#'):
                header_match = re.match(r'^#+', match_text)
                if header_match:
                    metadata['header_level'] = len(header_match.group(0))
            elif match_text.startswith(('- ', '* ', '+ ')):
                metadata['list_type'] = 'unordered'
            elif re.match(r'^\s*\d+\.', match_text):
                metadata['list_type'] = 'ordered'
        
        elif pattern_type == 'content_patterns':
            if '**' in match_text:
                metadata['formatting'] = 'bold'
            elif '*' in match_text:
                metadata['formatting'] = 'italic'
            elif '`' in match_text:
                metadata['formatting'] = 'code'
        
        return metadata

class FixedMarkdownAnalyzer:
    """Analizador principal CORREGIDO - Extrae TODO el contenido"""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.lsp_client = FixedLSPClient(workspace_path=str(self.workspace_path))
        self.pattern_detector = FixedMarkdownPatternDetector()
        self.content_extractor = MarkdownContentExtractor()
        self.analysis_cache = {}
        
        # Crear directorio de workspace si no existe
        self.workspace_path.mkdir(parents=True, exist_ok=True)
    
    def initialize(self) -> bool:
        """Inicializa el analizador con manejo de errores mejorado (sync)"""
        logger.info("Inicializando Markdown Analyzer...")
        
        try:
            # Intentar iniciar servidor LSP
            if self.lsp_client.start_server():
                if self.lsp_client.initialize():
                    logger.info("✅ LSP inicializado correctamente")
                else:
                    logger.warning("⚠️ LSP no se pudo inicializar, continuando sin LSP")
            else:
                logger.warning("⚠️ Servidor LSP no disponible, continuando sin LSP")
            
            logger.info("✅ Markdown Analyzer inicializado")
            return True
            
        except Exception as e:
            logger.error(f"Error en inicialización: {e}")
            logger.info("Continuando sin LSP...")
            return True  # Continuar sin LSP
    
    def read_markdown_file(self, file_path: str) -> str:
        """Lee archivo Markdown con manejo de errores mejorado"""
        file_path_obj = Path(file_path).absolute()  # FIXED: Validate path
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        try:
            with open(file_path_obj, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()
                logger.info(f"Archivo leído: {file_path} ({len(content)} caracteres)")
                return content
                
        except Exception as e:
            logger.error(f"Error leyendo archivo {file_path}: {e}")
            raise
    
    def analyze_file_complete(self, file_path: str) -> MarkdownStructure:
        """Análisis COMPLETO del archivo - Extrae TODO el contenido (sync wrapper)"""
        logger.info(f"🔍 Analizando archivo completo: {file_path}")
        
        # Leer contenido del archivo
        raw_content = self.read_markdown_file(file_path)
        if not raw_content.strip():
            raise ValueError(f"El archivo está vacío: {file_path}")
        
        # Extraer contenido completo
        content = self.content_extractor.extract_complete_content(raw_content)
        logger.info(f"📄 Contenido extraído: {content.word_count} palabras, {len(content.paragraphs)} párrafos")
        
        # Extraer secciones completas con contenido
        sections = self.content_extractor.extract_sections_with_content(raw_content)
        logger.info(f"📑 Secciones extraídas: {len(sections)}")
        
        # Extraer estructura básica
        basic_structure = self._extract_complete_structure(raw_content)
        
        # Detectar todos los patrones
        detected_patterns = self.pattern_detector.detect_all_patterns(raw_content)
        
        # Extraer zonas ocultas (merge from patterns and separate extractor)
        hidden_from_patterns = detected_patterns.get('hidden_zones', [])
        hidden_from_extractor = self._extract_hidden_zones(raw_content)
        hidden_zones = hidden_from_patterns + [z for z in hidden_from_extractor if z not in hidden_from_patterns]  # Avoid dups
        
        # Nota: Frontmatter/callouts/etc. quedan en patterns['metadata_blocks'] como diseño. Si quieres moverlos a hidden_zones, agrega aquí.
        
        # Análisis semántico
        semantic_analysis = self._perform_semantic_analysis(raw_content, content)
        
        # Extraer metadatos completos
        metadata = self._extract_complete_metadata(raw_content, content)
        
        # Intentar obtener símbolos LSP (sync)
        lsp_symbols = []
        try:
            if self.lsp_client.initialized:
                self.lsp_client.open_document(file_path, raw_content)
                lsp_symbols = self.lsp_client.get_document_symbols(file_path)
        except Exception as e:
            logger.warning(f"No se pudieron obtener símbolos LSP: {e}")
        
        # Crear estructura completa de análisis
        analysis = MarkdownStructure(
            title=self._extract_title(raw_content),
            raw_content=raw_content,
            content=content,
            sections=sections,
            headers=basic_structure['headers'],
            links=basic_structure['links'],
            images=basic_structure['images'],
            code_blocks=basic_structure['code_blocks'],
            tables=basic_structure['tables'],
            lists=basic_structure['lists'],
            metadata=metadata,
            hidden_zones=hidden_zones,
            patterns=detected_patterns,  # FIXED: Full dict now
            semantic_analysis=semantic_analysis,
            file_path=str(Path(file_path).absolute()),
            analysis_timestamp=datetime.now().isoformat(),
            lsp_symbols=lsp_symbols
        )
        
        # Guardar en caché
        self.analysis_cache[file_path] = analysis
        
        logger.info(f"✅ Análisis completo terminado para: {file_path}")
        return analysis
    
    def _extract_complete_structure(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extrae estructura completa con TODO el contenido"""
        structure = {
            'headers': [],
            'links': [],
            'images': [],
            'code_blocks': [],
            'tables': [],
            'lists': []
        }
        
        lines = content.split('\n')
        
        # Extraer headers con contenido completo
        for i, line in enumerate(lines):
            header_match = re.match(r'^(#{1,6})\s+(.+)', line)
            if header_match:
                structure['headers'].append({
                    'level': len(header_match.group(1)),
                    'text': header_match.group(2).strip(),
                    'line': i + 1,
                    'raw': line,
                    'anchor': self._create_anchor(header_match.group(2))
                })
        
        # Extraer enlaces con contexto
        for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content):
            structure['links'].append({
                'text': match.group(1),
                'url': match.group(2),
                'line': content[:match.start()].count('\n') + 1,
                'raw': match.group(0),
                'context': self._get_line_context(content, match.start())
            })
        
        # Extraer imágenes con detalles
        for match in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', content):
            structure['images'].append({
                'alt_text': match.group(1),
                'url': match.group(2),
                'line': content[:match.start()].count('\n') + 1,
                'raw': match.group(0),
                'context': self._get_line_context(content, match.start())
            })
        
        # Extraer bloques de código completos
        for match in re.finditer(r'^```(\w+)?\n(.*?)\n```', content, re.MULTILINE | re.DOTALL):
            structure['code_blocks'].append({
                'language': match.group(1) or 'text',
                'content': match.group(2),
                'line': content[:match.start()].count('\n') + 1,
                'raw': match.group(0),
                'line_count': match.group(2).count('\n') + 1,
                'char_count': len(match.group(2))
            })
        
        # Extraer tablas completas
        table_rows = []
        in_table = False
        table_start = 0
        
        for i, line in enumerate(lines):
            if re.match(r'^\s*\|.*\|', line):
                if not in_table:
                    in_table = True
                    table_start = i
                table_rows.append(line.strip())
            else:
                if in_table and table_rows:
                    structure['tables'].append({
                        'rows': table_rows,
                        'line_start': table_start + 1,
                        'line_end': i,
                        'row_count': len(table_rows),
                        'raw': '\n'.join(table_rows)
                    })
                    table_rows = []
                in_table = False
        
        # Extraer listas completas
        list_items = []
        in_list = False
        list_start = 0
        list_type = None
        
        for i, line in enumerate(lines):
            ordered_match = re.match(r'^\s*(\d+)\.\s+(.+)', line)
            unordered_match = re.match(r'^\s*[-*+]\s+(.+)', line)
            
            if ordered_match or unordered_match:
                if not in_list:
                    in_list = True
                    list_start = i
                    list_type = 'ordered' if ordered_match else 'unordered'
                
                if ordered_match:
                    list_items.append({
                        'type': 'ordered',
                        'number': int(ordered_match.group(1)),
                        'content': ordered_match.group(2),
                        'line': i + 1
                    })
                else:
                    if unordered_match:
                        list_items.append({
                            'type': 'unordered',
                            'content': unordered_match.group(1),
                            'line': i + 1
                        })
            else:
                if in_list and list_items:
                    structure['lists'].append({
                        'type': list_type,
                        'items': list_items,
                        'line_start': list_start + 1,
                        'line_end': i,
                        'item_count': len(list_items)
                    })
                    list_items = []
                in_list = False
                list_type = None
        
        return structure
    
    def _create_anchor(self, text: str) -> str:
        """Crea ancla URL-friendly para headers"""
        return re.sub(r'[^\w\s-]', '', text.lower()).replace(' ', '-')
    
    def _get_line_context(self, content: str, position: int) -> str:
        """Obtiene contexto de línea para una posición"""
        lines = content[:position].split('\n')
        return lines[-1] if lines else ""
    
    def _extract_hidden_zones(self, content: str) -> List[Dict[str, Any]]:
        """Extrae todas las zonas ocultas del contenido"""
        hidden_zones = []
        
        # Comentarios HTML
        for match in re.finditer(r'<!--\s*(.*?)\s*-->', content, re.DOTALL):
            hidden_zones.append({
                'type': 'html_comment',
                'content': match.group(1).strip(),
                'raw': match.group(0),
                'line': content[:match.start()].count('\n') + 1,
                'position': match.span(),
                'context': self._get_line_context(content, match.start())
            })
        
        # Secciones colapsables
        for match in re.finditer(r'<details[^>]*>\s*<summary>(.*?)</summary>(.*?)</details>', content, re.DOTALL):
            hidden_zones.append({
                'type': 'collapsible',
                'summary': match.group(1).strip(),
                'content': match.group(2).strip(),
                'raw': match.group(0),
                'line': content[:match.start()].count('\n') + 1,
                'position': match.span()
            })
        
        # Comentarios de referencia
        for match in re.finditer(r'\[comment\]:\s*#\s*\((.*?)\)', content):
            hidden_zones.append({
                'type': 'reference_comment',
                'content': match.group(1).strip(),
                'raw': match.group(0),
                'line': content[:match.start()].count('\n') + 1,
                'position': match.span()
            })
        
        return hidden_zones
    
    def _perform_semantic_analysis(self, raw_content: str, content: MarkdownContent) -> Dict[str, Any]:
        """Realiza análisis semántico completo del contenido"""
        analysis = {}
        
        # Análisis de tipo de documento
        doc_patterns = {
            'readme': r'(?i)(readme|getting\s+started|installation|setup)',
            'documentation': r'(?i)(api|documentation|docs|reference|guide)',
            'tutorial': r'(?i)(tutorial|walkthrough|step\s+\d+|lesson)',
            'changelog': r'(?i)(changelog|release\s+notes|version\s+history)',
            'license': r'(?i)(license|copyright|terms)',
            'contributing': r'(?i)(contributing|contribution|pull\s+request)',
            'configuration': r'(?i)(config|configuration|settings|env)'
        }
        
        doc_types = []
        for doc_type, pattern in doc_patterns.items():
            if re.search(pattern, raw_content):
                doc_types.append(doc_type)
        
        analysis['document_types'] = doc_types
        analysis['primary_type'] = doc_types[0] if doc_types else 'general'
        
        # Análisis de tecnologías mencionadas
        tech_patterns = {
            'languages': r'(?i)(python|javascript|typescript|java|c\+\+|c#|rust|go|kotlin|swift|php|ruby)',
            'frameworks': r'(?i)(react|vue|angular|django|flask|fastapi|express|spring|laravel)',
            'tools': r'(?i)(docker|kubernetes|git|npm|pip|yarn|webpack|babel|eslint)',
            'platforms': r'(?i)(aws|azure|gcp|heroku|vercel|netlify|github|gitlab)'
        }
        
        technologies = {}
        for tech_type, pattern in tech_patterns.items():
            matches = re.findall(pattern, raw_content)
            technologies[tech_type] = list(set([m.lower() for m in matches]))
        
        analysis['technologies'] = technologies
        
        # Análisis de complejidad
        analysis['complexity'] = {
            'readability_score': self._calculate_readability(content.plain_text),
            'technical_density': len(technologies['languages']) + len(technologies['frameworks']),
            'structure_complexity': len(content.paragraphs) / max(1, content.word_count / 100),
            'code_to_text_ratio': self._calculate_code_ratio(raw_content)
        }
        
        # Análisis de TODOs y tareas
        todo_patterns = [
            r'(?i)(todo|fixme|hack|xxx|note):\s*(.+)',
            r'(?i)<!--\s*(todo|fixme)\s*:?\s*(.+?)\s*-->',
            r'(?i)\[\s*(todo|fixme)\s*\]\s*(.+)'
        ]
        
        todos = []
        for pattern in todo_patterns:
            for match in re.finditer(pattern, raw_content):
                todos.append({
                    'type': match.group(1).lower(),
                    'content': match.group(2).strip(),
                    'line': raw_content[:match.start()].count('\n') + 1
                })
        
        analysis['todos'] = todos
        
        # Análisis de versiones y fechas
        version_matches = re.findall(r'v?\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+)?', raw_content)
        date_matches = re.findall(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}', raw_content)
        
        analysis['versions'] = list(set(version_matches))
        analysis['dates'] = list(set(date_matches))
        
        return analysis
    
    def _calculate_readability(self, text: str) -> float:
        """Calcula puntuación básica de legibilidad"""
        if not text.strip():
            return 0.0
        
        sentences = len(re.split(r'[.!?]+', text))
        words = len(re.findall(r'\b\w+\b', text))
        syllables = sum([self._count_syllables(word) for word in re.findall(r'\b\w+\b', text)])
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Fórmula simplificada de Flesch
        avg_sentence_length = words / sentences
        avg_syllables = syllables / words
        
        if words == 0:
            return 0.0
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
        return max(0, min(100, score))
    
    def _count_syllables(self, word: str) -> int:
        """Cuenta sílabas aproximadas en una palabra"""
        word = word.lower()
        vowels = 'aeiouy'
        syllables = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllables += 1
            prev_was_vowel = is_vowel
        
        if word.endswith('e'):
            syllables -= 1
        
        return max(1, syllables)
    
    def _calculate_code_ratio(self, content: str) -> float:
        """Calcula ratio de código vs texto"""
        code_blocks = re.findall(r'^```.*?```', content, re.MULTILINE | re.DOTALL)
        inline_code = re.findall(r'`[^`]+`', content)
        
        code_chars = sum(len(block) for block in code_blocks) + sum(len(code) for code in inline_code)
        total_chars = len(content)
        
        return code_chars / max(1, total_chars)
    
    def _extract_title(self, content: str) -> str:
        """Extrae título del documento"""
        # Buscar primer H1
        h1_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()
        
        # Buscar título en frontmatter
        frontmatter_match = re.search(r'^---\n.*?title:\s*["\']?([^"\'\n]+)["\']?.*?\n---', content, re.DOTALL)
        if frontmatter_match:
            return frontmatter_match.group(1).strip()
        
        # Buscar primer header de cualquier nivel
        header_match = re.search(r'^#{1,6}\s+(.+)', content, re.MULTILINE)
        if header_match:
            return header_match.group(1).strip()
        
        return "Sin título"
    
    def _extract_complete_metadata(self, raw_content: str, content: MarkdownContent) -> Dict[str, Any]:
        """Extrae metadatos completos del documento"""
        metadata = {}
        
        # Frontmatter YAML
        yaml_match = re.search(r'^---\n(.*?)\n---', raw_content, re.DOTALL)
        if yaml_match:
            try:
                import yaml
                frontmatter = yaml.safe_load(yaml_match.group(1))
                if isinstance(frontmatter, dict):
                    metadata.update(frontmatter)
            except (ImportError, Exception) as e:
                logger.warning(f"No se pudo parsear YAML frontmatter: {e}")
                # Parseo manual básico
                for line in yaml_match.group(1).split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip().strip('"\'')
        
        # Estadísticas del contenido
        metadata.update({
            'word_count': content.word_count,
            'character_count': content.character_count,
            'line_count': raw_content.count('\n') + 1,
            'paragraph_count': len(content.paragraphs),
            'sentence_count': len(content.sentences),
            'reading_time_minutes': max(1, content.word_count // 200),  # ~200 WPM
            'content_hash': hash(raw_content),
            'last_modified': datetime.now().isoformat()
        })
        
        # Estadísticas de estructura
        metadata.update({
            'header_count': len(re.findall(r'^#{1,6}\s+', raw_content, re.MULTILINE)),
            'link_count': len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', raw_content)),
            'image_count': len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', raw_content)),
            'code_block_count': len(re.findall(r'^```', raw_content, re.MULTILINE)),
            'list_count': len(re.findall(r'^\s*[-*+\d\.]\s+', raw_content, re.MULTILINE)),
            'table_count': len(re.findall(r'^\s*\|.*\|', raw_content, re.MULTILINE))
        })
        
        return metadata
    
    def export_complete_json(self, analysis: MarkdownStructure, output_path: str | None = None) -> str:
        """Exporta análisis completo a JSON con formato correcto"""
        logger.info("Exportando análisis completo a JSON...")
        
        # Convertir dataclasses a diccionarios
        def convert_to_dict(obj):
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    if isinstance(value, list):
                        result[key] = [convert_to_dict(item) for item in value]
                    elif isinstance(value, dict):
                        result[key] = {k: convert_to_dict(v) for k, v in value.items()}
                    elif hasattr(value, '__dict__'):
                        result[key] = convert_to_dict(value)
                    else:
                        result[key] = value
                return result
            else:
                return obj
        
        # Crear estructura JSON completa
        json_data = {
            'analysis_info': {
                'version': '1.0.0',
                'timestamp': analysis.analysis_timestamp,
                'file_path': analysis.file_path,
                'analyzer': 'Markdown LSP Analyzer'
            },
            'document': {
                'title': analysis.title,
                'metadata': analysis.metadata,
                'semantic_analysis': analysis.semantic_analysis
            },
            'content': {
                'raw_content': analysis.raw_content,
                'plain_text': analysis.content.plain_text,
                'paragraphs': [convert_to_dict(p) for p in analysis.content.paragraphs],
                'sentences': analysis.content.sentences,
                'statistics': {
                    'word_count': analysis.content.word_count,
                    'character_count': analysis.content.character_count,
                    'paragraph_count': len(analysis.content.paragraphs),
                    'sentence_count': len(analysis.content.sentences)
                }
            },
            'structure': {
                'sections': [convert_to_dict(s) for s in analysis.sections],
                'headers': analysis.headers,
                'links': analysis.links,
                'images': analysis.images,
                'code_blocks': analysis.code_blocks,
                'tables': analysis.tables,
                'lists': analysis.lists
            },
            'patterns': {k: [convert_to_dict(m) for m in v] for k, v in analysis.patterns.items()},  # FIXED: Handle dict
            'hidden_zones': [convert_to_dict(z) for z in analysis.hidden_zones],
            'lsp_symbols': analysis.lsp_symbols
        }
        
        # Serializar a JSON con formato bonito
        json_string = json.dumps(json_data, indent=2, ensure_ascii=False, sort_keys=True)
        
        # Guardar archivo si se especifica ruta
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as file:
                    file.write(json_string)
                logger.info(f"✅ Análisis exportado a: {output_path}")
            except Exception as e:
                logger.error(f"Error guardando JSON: {e}")
                raise
        
        return json_string
    
    def batch_analyze_complete(self, file_patterns: List[str]) -> Dict[str, MarkdownStructure]:
        """Análisis completo por lotes (sync)"""
        logger.info(f"Iniciando análisis por lotes: {file_patterns}")
        
        results = {}
        total_files = 0
        
        for pattern in file_patterns:
            files = list(self.workspace_path.glob(pattern))
            for file_path in files:
                if file_path.suffix.lower() in ['.md', '.markdown', '.mdown', '.mkd']:
                    total_files += 1
                    try:
                        logger.info(f"Analizando {total_files}: {file_path}")
                        analysis = self.analyze_file_complete(str(file_path))
                        results[str(file_path)] = analysis
                    except Exception as e:
                        logger.error(f"Error analizando {file_path}: {e}")
                        continue
        
        logger.info(f"✅ Análisis por lotes completado: {len(results)}/{total_files} archivos")
        return results
    
    def shutdown(self):
        """Cierre limpio del analizador (sync)"""
        logger.info("Cerrando Markdown Analyzer...")
        try:
            self.lsp_client.shutdown()
        except Exception as e:
            logger.error(f"Error cerrando LSP client: {e}")
        logger.info("✅ Markdown Analyzer cerrado")
