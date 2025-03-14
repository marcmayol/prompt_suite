# Prompt Manager

Una biblioteca Python para gestionar prompts de IA con soporte para almacenamiento en YAML, JSON y SQL.

## Características

- Gestión de prompts con múltiples modelos
- Soporte para parámetros dinámicos
- Almacenamiento en YAML o JSON con guardado automático
- Soporte para bases de datos SQL (SQLite, PostgreSQL, etc.)
- Validación de datos con Pydantic
- Interfaz simple y fácil de usar

## Instalación

### Instalación desde PyPI

```bash
pip install prompt-manager
```

### Instalación desde el código fuente

```bash
git clone https://github.com/tu-usuario/prompt-manager.git
cd prompt-manager
pip install -e .
```

## Uso básico

### Con almacenamiento YAML

```python
from prompt_manager import PromptManager

# Crear un gestor de prompts con YAML
pm = PromptManager("prompts.yaml", format="yaml")

# Crear un nuevo prompt
pm.create_prompt(
    prompt_name="traductor",
    models={
        "gpt-4": "Traduce el siguiente texto al {idioma}: {texto}"
    },
    parameters=["idioma", "texto"]
)

# Usar el prompt
texto = pm.get_prompt(
    prompt_name="traductor",
    model="gpt-4",
    parameters={
        "idioma": "inglés",
        "texto": "Hola, ¿cómo estás?"
    }
)
```

### Con almacenamiento JSON

```python
from prompt_manager import PromptManager

# Crear un gestor de prompts con JSON
pm = PromptManager("prompts.json", format="json")

# Crear un nuevo prompt
pm.create_prompt(
    prompt_name="traductor",
    models={
        "gpt-4": "Traduce el siguiente texto al {idioma}: {texto}"
    },
    parameters=["idioma", "texto"]
)
```

### Con almacenamiento SQL

```python
from prompt_manager import SQLPromptManager, SQLConfig
import sqlite3

# Configurar la conexión SQL
conn = sqlite3.connect("prompts.db")
config = SQLConfig(connection=conn)

# Crear el gestor de prompts
pm = SQLPromptManager(config)

# Crear un nuevo prompt
pm.create_prompt(
    prompt_name="traductor",
    models={
        "gpt-4": "Traduce el siguiente texto al {idioma}: {texto}"
    },
    parameters=["idioma", "texto"]
)
```

## Comparación de formatos

### YAML
- Más legible para humanos
- Soporta comentarios
- Mejor para configuraciones
- Ideal para desarrollo y pruebas

### JSON
- Más rápido de parsear
- Mejor para APIs web
- Más estricto y estructurado
- Ideal para producción

### SQL
- Mejor para múltiples usuarios
- Soporte para transacciones
- Mejor para datos dinámicos
- Ideal para aplicaciones en producción

## Requisitos

- Python >= 3.8
- pyyaml >= 6.0.1
- pydantic >= 2.5.2
- psycopg2-binary >= 2.9.9 (opcional, para soporte de PostgreSQL)

## Licencia

MIT License 