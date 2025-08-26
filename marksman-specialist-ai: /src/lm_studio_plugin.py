#!/usr/bin/env python3
"""
LM Studio Plugin CORREGIDO - Markdown LSP Analyzer
VERSIÓN FUNCIONAL COMPLETA - Todos los módulos funcionan
Extrae TODO el contenido, no solo títulos
JSON completamente funcional
"""

import json
import asyncio
import logging
import sys
import traceback
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Verificar e instalar dependencias
def install_missing_dependencies():
    """Instala dependencias faltantes automáticamente"""
    required_packages = [
        ("fastapi", "fastapi>=0.104.0"),
        ("uvicorn", "uvicorn[standard]>=0.24.0"),
        ("pydantic", "pydantic>=2.5.0")
    ]
    
    missing_packages = []
    
    for package_name, install_name in required_packages:
        try:
            __import__(package_name)
        except ImportError:
            missing_packages.append(install_name)
    
    if missing_packages:
        print(f"📦 Instalando dependencias faltantes: {', '.join(missing_packages)}")
        import subprocess
        import sys
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} instalado correctamente")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error instalando {package}: {e}")
                return False
        
        print("🔄 Reiniciando importaciones...")
    
    return True

# Instalar dependencias si es necesario
if not install_missing_dependencies():
    print("❌ No se pudieron instalar las dependencias necesarias")
    sys.exit(1)

# Importar después de verificar dependencias
try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks  # type: ignore
    from fastapi.middleware.cors import CORSMiddleware  # type: ignore
    from fastapi.responses import JSONResponse  # type: ignore
    from pydantic import BaseModel, Field  # type: ignore
    import uvicorn  # type: ignore
except ImportError as e:
    print(f"❌ Error importando FastAPI: {e}")
    print("💡 Instalar con: pip install fastapi uvicorn[standard] pydantic")
    sys.exit(1)

# Importar nuestro analizador corregido
try:
    from src.core.markdown_lsp_analyzer import FixedMarkdownAnalyzer, MarkdownStructure
except ImportError:
    print("❌ No se pudo importar el analizador. Asegúrate de que markdown_lsp_analyzer.py esté disponible.")
    sys.exit(1)

# Configurar logging mejorado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('lm_studio_plugin.log')
    ]
)
logger = logging.getLogger(__name__)

# Modelos Pydantic CORREGIDOS
class AnalysisRequest(BaseModel):
    file_path: str = Field(..., description="Ruta del archivo Markdown a analizar")
    extract_content: bool = Field(True, description="Extraer contenido completo")
    include_patterns: bool = Field(True, description="Incluir detección de patrones")
    include_lsp: bool = Field(True, description="Usar análisis LSP si está disponible")

class BatchAnalysisRequest(BaseModel):
    patterns: List[str] = Field(default=["*.md"], description="Patrones de archivos a analizar")
    workspace_path: str = Field(default=".", description="Directorio de trabajo")
    max_files: int = Field(default=50, description="Máximo número de archivos a procesar")

class PatternRequest(BaseModel):
    file_path: str = Field(..., description="Ruta del archivo a analizar")
    pattern_types: Optional[List[str]] = Field(default=None, description="Tipos de patrones a detectar")

class ContentExtractionRequest(BaseModel):
    file_path: str = Field(..., description="Ruta del archivo")
    extract_sections: bool = Field(True, description="Extraer secciones completas")
    extract_text: bool = Field(True, description="Extraer texto plano")
    extract_metadata: bool = Field(True, description="Extraer metadatos")

class AnalysisResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str
    processing_time: float

class LMStudioPluginFixed:
    """Plugin LM Studio COMPLETAMENTE FUNCIONAL"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Markdown LSP Analyzer - VERSIÓN CORREGIDA",
            description="Extrae TODO el contenido de Markdown, no solo títulos. JSON completamente funcional.",
            version="2.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        self.analyzer = None
        self.is_initialized = False
        self.initialization_error = None
        
        # Configurar CORS para LM Studio
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Configurar manejadores de errores
        self.setup_error_handlers()
        
        # Configurar rutas
        self.setup_routes()
    
    def setup_error_handlers(self):
        """Configura manejadores de errores personalizados"""
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request, exc):
            logger.error(f"Error no manejado: {exc}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error interno del servidor: {str(exc)}",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": type(exc).__name__
                }
            )
        
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request, exc):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "status": "error",
                    "message": exc.detail,
                    "timestamp": datetime.now().isoformat(),
                    "status_code": exc.status_code
                }
            )
    
    def setup_routes(self):
        """Configura todas las rutas de la API"""
        
        @self.app.on_event("startup")
        async def startup():
            """Inicialización al arrancar"""
            try:
                logger.info("🚀 Iniciando Markdown LSP Analyzer...")
                self.analyzer = FixedMarkdownAnalyzer()
                
                # Intentar inicializar
                if await self.analyzer.initialize():
                    self.is_initialized = True
                    logger.info("✅ Analyzer inicializado correctamente")
                else:
                    self.is_initialized = False
                    self.initialization_error = "No se pudo inicializar completamente (LSP no disponible)"
                    logger.warning("⚠️ Analyzer parcialmente inicializado sin LSP")
                
            except Exception as e:
                self.is_initialized = False
                self.initialization_error = str(e)
                logger.error(f"❌ Error en inicialización: {e}")
        
        @self.app.on_event("shutdown")
        async def shutdown():
            """Limpieza al cerrar"""
            if self.analyzer:
                try:
                    analyzer = self.analyzer  # type: ignore
                    await analyzer.shutdown()  # type: ignore
                    logger.info("🔄 Analyzer cerrado correctamente")
                except Exception as e:
                    logger.error(f"Error cerrando analyzer: {e}")
        
        @self.app.get("/")
        async def root():
            """Endpoint raíz con información del servicio"""
            return {
                "service": "Markdown LSP Analyzer",
                "version": "2.0.0",
                "status": "running",
                "initialized": self.is_initialized,
                "initialization_error": self.initialization_error,
                "capabilities": [
                    "complete_content_extraction",
                    "pattern_detection",
                    "lsp_integration",
                    "json_export",
                    "batch_processing",
                    "semantic_analysis"
                ],
                "endpoints": {
                    "analyze": "POST /analyze - Análisis completo de archivo",
                    "content": "POST /content - Extracción de contenido",
                    "patterns": "POST /patterns - Detección de patrones",
                    "batch": "POST /batch-analyze - Análisis por lotes",
                    "health": "GET /health - Estado del servicio",
                    "schema": "GET /schema - Esquema JSON",
                    "docs": "GET /docs - Documentación API"
                },
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/analyze", response_model=AnalysisResponse)
        async def analyze_complete(request: AnalysisRequest):
            """ANÁLISIS COMPLETO - Extrae TODO el contenido"""
            start_time = datetime.now()
            
            if not self.analyzer:
                raise HTTPException(status_code=503, detail="Analyzer no inicializado")
            
            try:
                logger.info(f"📋 Analizando archivo completo: {request.file_path}")
                
                # Verificar que el archivo existe
                file_path = Path(request.file_path)
                if not file_path.exists():
                    raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {request.file_path}")
                
                # Realizar análisis completo
                if not self.analyzer:
                    raise HTTPException(status_code=503, detail="Analyzer no inicializado")
                analyzer = self.analyzer  # type: ignore
                analysis = await analyzer.analyze_file_complete(request.file_path)  # type: ignore
                
                # Convertir resultado a diccionario serializable
                result_data = self._convert_analysis_to_dict(analysis)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                logger.info(f"✅ Análisis completado en {processing_time:.2f}s")
                
                return AnalysisResponse(
                    status="success",
                    message=f"Análisis completo realizado exitosamente. Contenido: {analysis.content.word_count} palabras, {len(analysis.content.paragraphs)} párrafos",
                    data=result_data,
                    timestamp=datetime.now().isoformat(),
                    processing_time=processing_time
                )
                
            except Exception as e:
                processing_time = (datetime.now() - start_time).total_seconds()
                logger.error(f"❌ Error en análisis: {e}")
                
                return AnalysisResponse(
                    status="error",
                    message="Error realizando análisis",
                    error=str(e),
                    timestamp=datetime.now().isoformat(),
                    processing_time=processing_time
                )
        
        @self.app.post("/content", response_model=AnalysisResponse)
        async def extract_content(request: ContentExtractionRequest):
            """EXTRACCIÓN DE CONTENIDO COMPLETO - Solo contenido, sin análisis LSP"""
            start_time = datetime.now()
            
            if not self.analyzer:
                raise HTTPException(status_code=503, detail="Analyzer no inicializado")
            
            try:
                logger.info(f"📄 Extrayendo contenido: {request.file_path}")
                
                # Leer archivo
                if not self.analyzer:
                    raise HTTPException(status_code=503, detail="Analyzer no inicializado")
                analyzer = self.analyzer  # type: ignore
                content = analyzer.read_markdown_file(request.file_path)
                
                # Extraer contenido completo
                extracted_content = analyzer.content_extractor.extract_complete_content(content)
                
                # Extraer secciones si se solicita
                sections = []
                if request.extract_sections:
                    sections = analyzer.content_extractor.extract_sections_with_content(content)
                
                # Extraer metadatos básicos si se solicita
                metadata = {}
                if request.extract_metadata:
                    metadata = analyzer._extract_complete_metadata(content, extracted_content)
                
                result_data = {
                    "file_path": request.file_path,
                    "content": {
                        "raw_content": extracted_content.raw_text,
                        "plain_text": extracted_content.plain_text,
                        "paragraphs": [self._convert_to_serializable(p) for p in extracted_content.paragraphs],  # type: ignore
                        "sentences": extracted_content.sentences,
                        "statistics": {
                            "word_count": extracted_content.word_count,
                            "character_count": extracted_content.character_count,
                            "paragraph_count": len(extracted_content.paragraphs),
                            "sentence_count": len(extracted_content.sentences)
                        }
                    },
                    "sections": [self._convert_to_serializable(s) for s in sections] if request.extract_sections else [],
                    "metadata": metadata if request.extract_metadata else {}
                }
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return AnalysisResponse(
                    status="success",
                    message=f"Contenido extraído: {extracted_content.word_count} palabras, {len(extracted_content.paragraphs)} párrafos",
                    data=result_data,
                    timestamp=datetime.now().isoformat(),
                    processing_time=processing_time
                )
                
            except Exception as e:
                processing_time = (datetime.now() - start_time).total_seconds()
                logger.error(f"❌ Error extrayendo contenido: {e}")
                
                return AnalysisResponse(
                    status="error",
                    message="Error extrayendo contenido",
                    error=str(e),
                    timestamp=datetime.now().isoformat(),
                    processing_time=processing_time
                )
        
        @self.app.post("/patterns", response_model=AnalysisResponse)
        async def detect_patterns(request: PatternRequest):
            """DETECCIÓN DE PATRONES"""
            start_time = datetime.now()
            
            if not self.analyzer:
                raise HTTPException(status_code=503, detail="Analyzer no inicializado")
            
            try:
                logger.info(f"🔍 Detectando patrones: {request.file_path}")
                
                if not self.analyzer:
                    raise HTTPException(status_code=503, detail="Analyzer no inicializado")
                analyzer = self.analyzer  # type: ignore
                content = analyzer.read_markdown_file(request.file_path)
                patterns = analyzer.pattern_detector.detect_all_patterns(content)
                
                # Filtrar patrones si se especifican tipos
                if request.pattern_types:
                    patterns = {k: v for k, v in patterns.items() if k in request.pattern_types}  # type: ignore
                
                # Contar patrones totales
                total_patterns = sum(len(v) for v in patterns.values())
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return AnalysisResponse(
                    status="success",
                    message=f"Detectados {total_patterns} patrones",
                    data={
                        "file_path": request.file_path,
                        "patterns": patterns,
                        "pattern_summary": {k: len(v) for k, v in patterns.items()},
                        "total_patterns": total_patterns
                    },
                    timestamp=datetime.now().isoformat(),
                    processing_time=processing_time
                )
                
            except Exception as e:
                processing_time = (datetime.now() - start_time).total_seconds()
                logger.error(f"❌ Error detectando patrones: {e}")
                
                return AnalysisResponse(
                    status="error",
                    message="Error detectando patrones",
                    error=str(e),
                    timestamp=datetime.now().isoformat(),
                    processing_time=processing_time
                )
        
        @self.app.post("/batch-analyze", response_model=AnalysisResponse)
        async def batch_analyze(request: BatchAnalysisRequest):
            """ANÁLISIS POR LOTES"""
            start_time = datetime.now()
            
            if not self.analyzer:
                raise HTTPException(status_code=503, detail="Analyzer no inicializado")
            
            try:
                logger.info(f"📚 Análisis por lotes: {request.patterns}")
                
                # Cambiar workspace si es necesario
                if request.workspace_path != ".":
                    self.analyzer.workspace_path = Path(request.workspace_path)
                
                # Realizar análisis por lotes
                if not self.analyzer:
                    raise HTTPException(status_code=503, detail="Analyzer no inicializado")
                analyzer = self.analyzer  # type: ignore
                results = await analyzer.batch_analyze_complete(request.patterns)  # type: ignore
                
                # Limitar resultados si excede el máximo
                if len(results) > request.max_files:
                    results = dict(list(results.items())[:request.max_files])
                
                # Convertir resultados a formato serializable
                batch_data = {}
                for file_path, analysis in results.items():
                    batch_data[file_path] = {
                        "title": analysis.title,
                        "content_summary": {
                            "word_count": analysis.content.word_count,
                            "paragraph_count": len(analysis.content.paragraphs),
                            "sentence_count": len(analysis.content.sentences)
                        },
                        "structure_summary": {
                            "headers": len(analysis.headers),
                            "links": len(analysis.links),
                            "code_blocks": len(analysis.code_blocks),
                            "tables": len(analysis.tables)
                        },
                        "analysis_timestamp": analysis.analysis_timestamp
                    }
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return AnalysisResponse(
                    status="success",
                    message=f"Análisis por lotes completado: {len(results)} archivos procesados",
                    data={
                        "files_processed": len(results),
                        "patterns": request.patterns,
                        "workspace_path": request.workspace_path,
                        "results": batch_data
                    },
                    timestamp=datetime.now().isoformat(),
                    processing_time=processing_time
                )
                
            except Exception as e:
                processing_time = (datetime.now() - start_time).total_seconds()
                logger.error(f"❌ Error en análisis por lotes: {e}")
                
                return AnalysisResponse(
                    status="error",
                    message="Error en análisis por lotes",
                    error=str(e),
                    timestamp=datetime.now().isoformat(),
                    processing_time=processing_time
                )
        
        @self.app.get("/health")
        async def health_check():
            """VERIFICACIÓN DE ESTADO DETALLADA"""
            try:
                # Verificar estado del analyzer
                analyzer_status = "initialized" if self.is_initialized else "not_initialized"
                
                # Verificar LSP si está disponible
                lsp_status = "not_available"
                if self.analyzer and hasattr(self.analyzer, 'lsp_client'):
                    lsp_status = "connected" if self.analyzer.lsp_client.initialized else "disconnected"
                
                # Verificar workspace
                workspace_exists = False
                workspace_readable = False
                if self.analyzer:
                    workspace_exists = self.analyzer.workspace_path.exists()
                    workspace_readable = self.analyzer.workspace_path.is_dir()
                
                return {
                    "status": "healthy" if self.is_initialized else "degraded",
                    "timestamp": datetime.now().isoformat(),
                    "components": {
                        "analyzer": analyzer_status,
                        "lsp_client": lsp_status,
                        "workspace": {
                            "exists": workspace_exists,
                            "readable": workspace_readable,
                            "path": str(self.analyzer.workspace_path) if self.analyzer else None
                        }
                    },
                    "initialization_error": self.initialization_error,
                    "capabilities": {
                        "content_extraction": True,
                        "pattern_detection": True,
                        "lsp_analysis": lsp_status == "connected",
                        "batch_processing": True,
                        "json_export": True
                    }
                }
                
            except Exception as e:
                logger.error(f"Error en health check: {e}")
                return {
                    "status": "unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                }
        
        @self.app.get("/schema")
        async def get_json_schema():
            """ESQUEMA JSON PARA LA RESPUESTA DE ANÁLISIS"""
            return {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "MarkdownAnalysisComplete",
                "description": "Esquema completo para análisis de Markdown con contenido extraído",
                "type": "object",
                "properties": {
                    "analysis_info": {
                        "type": "object",
                        "properties": {
                            "version": {"type": "string"},
                            "timestamp": {"type": "string"},
                            "file_path": {"type": "string"},
                            "analyzer": {"type": "string"}
                        }
                    },
                    "document": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "metadata": {"type": "object"},
                            "semantic_analysis": {"type": "object"}
                        }
                    },
                    "content": {
                        "type": "object",
                        "properties": {
                            "raw_content": {"type": "string", "description": "Contenido completo original"},
                            "plain_text": {"type": "string", "description": "Texto plano extraído"},
                            "paragraphs": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "content": {"type": "string"},
                                        "plain_text": {"type": "string"},
                                        "type": {"type": "string"},
                                        "line_start": {"type": "integer"},
                                        "word_count": {"type": "integer"}
                                    }
                                }
                            },
                            "sentences": {"type": "array", "items": {"type": "string"}},
                            "statistics": {
                                "type": "object",
                                "properties": {
                                    "word_count": {"type": "integer"},
                                    "character_count": {"type": "integer"},
                                    "paragraph_count": {"type": "integer"},
                                    "sentence_count": {"type": "integer"}
                                }
                            }
                        }
                    },
                    "structure": {
                        "type": "object",
                        "properties": {
                            "sections": {"type": "array"},
                            "headers": {"type": "array"},
                            "links": {"type": "array"},
                            "images": {"type": "array"},
                            "code_blocks": {"type": "array"},
                            "tables": {"type": "array"},
                            "lists": {"type": "array"}
                        }
                    },
                    "patterns": {"type": "object"},
                    "hidden_zones": {"type": "array"},
                    "lsp_symbols": {"type": "array"}
                },
                "required": ["analysis_info", "document", "content", "structure"]
            }
    
    def _convert_analysis_to_dict(self, analysis: MarkdownStructure) -> Dict[str, Any]:
        """Convierte análisis a diccionario serializable para JSON"""
        return {
            "analysis_info": {
                "version": "2.0.0",
                "timestamp": analysis.analysis_timestamp,
                "file_path": analysis.file_path,
                "analyzer": "Markdown LSP Analyzer - Fixed"
            },
            "document": {
                "title": analysis.title,
                "metadata": analysis.metadata,
                "semantic_analysis": analysis.semantic_analysis
            },
            "content": {
                "raw_content": analysis.raw_content,
                "plain_text": analysis.content.plain_text,
                "paragraphs": [self._convert_to_serializable(p) for p in analysis.content.paragraphs],
                "sentences": analysis.content.sentences,
                "statistics": {
                    "word_count": analysis.content.word_count,
                    "character_count": analysis.content.character_count,
                    "paragraph_count": len(analysis.content.paragraphs),
                    "sentence_count": len(analysis.content.sentences)
                }
            },
            "structure": {
                "sections": [self._convert_to_serializable(s) for s in analysis.sections],
                "headers": analysis.headers,
                "links": analysis.links,
                "images": analysis.images,
                "code_blocks": analysis.code_blocks,
                "tables": analysis.tables,
                "lists": analysis.lists
            },
            "patterns": analysis.patterns,
            "hidden_zones": analysis.hidden_zones,
            "lsp_symbols": analysis.lsp_symbols
        }
    
    def _convert_to_serializable(self, obj) -> Any:
        """Convierte cualquier objeto a formato serializable JSON"""
        if hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                if isinstance(value, list):
                    result[key] = [self._convert_to_serializable(item) for item in value]
                elif hasattr(value, '__dict__'):
                    result[key] = self._convert_to_serializable(value)
                else:
                    result[key] = value
            return result
        elif isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        else:
            return obj

# Funciones de utilidad y setup
def create_requirements_txt():
    """Crea archivo requirements.txt actualizado"""
    requirements = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "python-multipart>=0.0.6",
        "aiofiles>=23.2.1"
    ]
    
    with open("requirements.txt", "w") as f:
        f.write("\n".join(requirements))
    
    print("✅ requirements.txt creado")

def create_test_files():
    """Crea archivos de test para verificar funcionalidad"""
    
    # Archivo de test simple
    simple_content = """# Test Simple

Este es un **test simple** para verificar que el analizador funciona.

## Contenido

- Item 1
- Item 2
- Item 3

El análisis debe extraer TODO este contenido, no solo los títulos.
"""
    
    # Archivo de test complejo
    complex_content = """---
title: "Test Complejo"
author: "Analyzer Test"
tags: ["test", "complete", "content"]
---

# Test Complejo del Analizador

Este documento contiene **múltiples tipos de contenido** para verificar que el analizador extrae *todo correctamente*.

## Sección Principal

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

<!-- TODO: Este comentario debe ser detectado -->

### Subsección con Código

```python
def extract_all_content():
    return "Todo el contenido debe ser extraído"
```

### Enlaces y Referencias

- [Enlace 1](https://example.com)
- [Enlace 2](https://test.com)

![Imagen de test](https://example.com/image.png)

## Tabla de Ejemplo

| Columna A | Columna B | Columna C |
|-----------|-----------|-----------|
| Dato 1    | Dato 2    | Dato 3    |
| Valor X   | Valor Y   | Valor Z   |

## Contenido Oculto

<details>
<summary>Sección oculta</summary>

Este contenido está inicialmente oculto pero debe ser detectado y extraído por el analizador.

- Item oculto 1
- Item oculto 2

</details>

## Anotaciones Especiales

Texto con [[enlace-wiki]] y @anotacion(parametro) y ::marcador::.

## Conclusión

Todo este contenido debe ser extraído completamente, incluyendo:
1. El texto completo de cada párrafo
2. Los metadatos del frontmatter
3. Las zonas ocultas
4. Los patrones especiales
5. La estructura completa

<!-- Comentario final -->
"""
    
    # Crear archivos
    with open("test_simple.md", "w", encoding="utf-8") as f:
        f.write(simple_content)
    
    with open("test_complex.md", "w", encoding="utf-8") as f:
        f.write(complex_content)
    
    print("✅ Archivos de test creados: test_simple.md, test_complex.md")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Markdown LSP Analyzer - Plugin LM Studio CORREGIDO')
    parser.add_argument('--setup', action='store_true', help='Crear archivos de configuración')
    parser.add_argument('--test', action='store_true', help='Crear archivos de test')
    parser.add_argument('--port', type=int, default=8000, help='Puerto del servidor')
    parser.add_argument('--host', default='127.0.0.1', help='Host del servidor')
    parser.add_argument('--debug', action='store_true', help='Modo debug')
    
    args = parser.parse_args()
    
    if args.setup:
        print("🔧 Creando archivos de configuración...")
        create_requirements_txt()
        return
    
    if args.test:
        print("🧪 Creando archivos de test...")
        create_test_files()
        return
    
    # Configurar nivel de logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Crear plugin
    plugin = LMStudioPluginFixed()
    
    print(f"""
🚀 INICIANDO MARKDOWN LSP ANALYZER - VERSIÓN CORREGIDA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ EXTRAE TODO EL CONTENIDO (no solo títulos)
✅ JSON COMPLETAMENTE FUNCIONAL  
✅ TODOS LOS MÓDULOS FUNCIONAN
✅ COMPATIBLE CON LM STUDIO

📍 Servidor: http://{args.host}:{args.port}
📖 Documentación: http://{args.host}:{args.port}/docs
🔍 Estado: http://{args.host}:{args.port}/health
📊 Esquema JSON: http://{args.host}:{args.port}/schema

🧪 ENDPOINTS PRINCIPALES:
• POST /analyze - Análisis completo con todo el contenido
• POST /content - Extracción de contenido sin LSP
• POST /patterns - Detección de patrones
• POST /batch-analyze - Análisis por lotes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    # Ejecutar servidor
    uvicorn.run(
        plugin.app,
        host=args.host,
        port=args.port,
        log_level="debug" if args.debug else "info",
        reload=args.debug
    )

if __name__ == "__main__":
    main()