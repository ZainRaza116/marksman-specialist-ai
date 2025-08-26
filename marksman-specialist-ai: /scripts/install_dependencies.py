#!/usr/bin/env python3
"""
Automated dependency installation script
Script de instalación automática de dependencias
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Ejecutar comando con manejo de errores"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e.stderr}")
        return False

def check_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Se requiere Python 3.8 o superior")
        return False
    
    print("✅ Versión de Python compatible")
    return True

def install_marksman():
    """Instalar Marksman LSP"""
    print("🔧 Instalando Marksman LSP...")
    
    # Verificar si Node.js está disponible
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        print("✅ Node.js encontrado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js no encontrado. Instalar desde: https://nodejs.org/")
        return False
    
    # Instalar Marksman
    return run_command(
        "npm install -g @artempyanykh/marksman",
        "Instalación de Marksman"
    )

def install_python_dependencies():
    """Instalar dependencias de Python"""
    requirements_path = Path(__file__).parent.parent / "requirements.txt"
    
    if requirements_path.exists():
        return run_command(
            f"pip install -r {requirements_path}",
            "Instalación de dependencias Python"
        )
    else:
        # Instalar dependencias básicas manualmente
        basic_deps = [
            "pyyaml>=6.0",
            "pathlib2>=2.3.0"
        ]
        
        for dep in basic_deps:
            if not run_command(f"pip install {dep}", f"Instalación de {dep}"):
                return False
        
        return True

def verify_installation():
    """Verificar que todo esté instalado correctamente"""
    print("🔍 Verificando instalación...")
    
    # Verificar Marksman
    try:
        result = subprocess.run(["marksman", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Marksman: {result.stdout.strip()}")
        else:
            print("❌ Marksman no responde correctamente")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("❌ Marksman no encontrado o no responde")
        return False
    
    # Verificar dependencias Python
    try:
        import yaml
        print("✅ PyYAML disponible")
    except ImportError:
        print("❌ PyYAML no encontrado")
        return False
    
    # Verificar que se puede importar el módulo principal
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from marksman_specialist_ai import MarksmanlSpecialistAI
        print("✅ Módulo principal importable")
    except ImportError as e:
        print(f"❌ Error importando módulo principal: {e}")
        return False
    
    return True

def main():
    """Función principal de instalación"""
    print("🚀 MARKSMAN SPECIALIST AI - INSTALACIÓN AUTOMÁTICA")
    print("=" * 60)
    
    # Verificar Python
    if not check_python_version():
        return 1
    
    # Instalar dependencias Python
    if not install_python_dependencies():
        print("❌ Error instalando dependencias Python")
        return 1
    
    # Instalar Marksman
    if not install_marksman():
        print("⚠️  Marksman no se pudo instalar automáticamente")
        print("   Instalar manualmente:")