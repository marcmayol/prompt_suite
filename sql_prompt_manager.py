from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import json

class SQLConfig(BaseModel):
    """Configuración para el backend SQL"""
    connection: Any  # Objeto de conexión SQL (ej: psycopg2, sqlite3, etc.)
    create_tables: bool = True  # Si se deben crear las tablas automáticamente
    table_prefix: str = "prompt_"  # Prefijo para las tablas
    custom_queries: Optional[Dict[str, str]] = None  # Sentencias SQL personalizadas

class Prompt(BaseModel):
    prompt_name: str
    models: Dict[str, str] = Field(default_factory=dict)
    parameters: List[str] = Field(default_factory=list)

class SQLPromptManager:
    def __init__(self, sql_config: SQLConfig):
        """
        Inicializar el gestor de prompts con backend SQL
        :param sql_config: Configuración SQL que incluye la conexión y opciones
        """
        self.config = sql_config
        self.prompts: Dict[str, Prompt] = {}
        
        # Definir las sentencias SQL por defecto
        self.default_queries = {
            "create_table": f"""
                CREATE TABLE IF NOT EXISTS {self.config.table_prefix}prompts (
                    prompt_name VARCHAR(255) PRIMARY KEY,
                    models JSON,
                    parameters JSON
                )
            """,
            "insert": f"""
                INSERT INTO {self.config.table_prefix}prompts (prompt_name, models, parameters)
                VALUES (%s, %s, %s)
                ON CONFLICT (prompt_name) DO UPDATE
                SET models = EXCLUDED.models, parameters = EXCLUDED.parameters
            """,
            "select": f"SELECT * FROM {self.config.table_prefix}prompts",
            "select_by_name": f"SELECT * FROM {self.config.table_prefix}prompts WHERE prompt_name = %s",
            "delete": f"DELETE FROM {self.config.table_prefix}prompts WHERE prompt_name = %s"
        }
        
        # Usar queries personalizadas si están definidas
        self.queries = self.config.custom_queries or self.default_queries
        
        # Crear tablas si es necesario
        if self.config.create_tables:
            self._create_tables()
        
        # Cargar prompts existentes
        self._load_prompts()

    def _create_tables(self):
        """Crear las tablas necesarias si no existen"""
        with self.config.connection.cursor() as cursor:
            cursor.execute(self.queries["create_table"])
            self.config.connection.commit()

    def _load_prompts(self):
        """Cargar prompts desde la base de datos"""
        with self.config.connection.cursor() as cursor:
            cursor.execute(self.queries["select"])
            for row in cursor.fetchall():
                prompt_name, models_json, parameters_json = row
                self.prompts[prompt_name] = Prompt(
                    prompt_name=prompt_name,
                    models=json.loads(models_json),
                    parameters=json.loads(parameters_json)
                )

    def add_model_to_prompt(self, prompt_name: str, model_name: str, model_content: str) -> Prompt:
        """
        Añadir un nuevo modelo a un prompt existente
        :param prompt_name: Nombre del prompt
        :param model_name: Nombre del nuevo modelo
        :param model_content: Contenido del prompt para el nuevo modelo
        :return: Prompt actualizado
        """
        if prompt_name not in self.prompts:
            raise ValueError(f"El prompt '{prompt_name}' no existe")
        
        prompt = self.prompts[prompt_name]
        if model_name in prompt.models:
            raise ValueError(f"El modelo '{model_name}' ya existe en el prompt '{prompt_name}'")
        
        # Añadir el nuevo modelo
        prompt.models[model_name] = model_content
        
        # Actualizar en la base de datos
        with self.config.connection.cursor() as cursor:
            cursor.execute(
                self.queries["insert"],
                (prompt_name, json.dumps(prompt.models), json.dumps(prompt.parameters))
            )
            self.config.connection.commit()
        
        return prompt

    def create_prompt(self, prompt_name: str, models: Dict[str, str], parameters: List[str] = None) -> Prompt:
        """Crear un nuevo prompt"""
        if prompt_name in self.prompts:
            raise ValueError(f"El prompt '{prompt_name}' ya existe")
        
        prompt = Prompt(
            prompt_name=prompt_name,
            models=models,
            parameters=parameters or []
        )
        
        with self.config.connection.cursor() as cursor:
            cursor.execute(
                self.queries["insert"],
                (prompt_name, json.dumps(models), json.dumps(parameters or []))
            )
            self.config.connection.commit()
        
        self.prompts[prompt_name] = prompt
        return prompt

    def update_prompt(self, prompt_name: str, models: Optional[Dict[str, str]] = None, 
                     parameters: Optional[List[str]] = None) -> Prompt:
        """Actualizar un prompt existente"""
        if prompt_name not in self.prompts:
            raise ValueError(f"El prompt '{prompt_name}' no existe")
        
        prompt = self.prompts[prompt_name]
        if models is not None:
            prompt.models.update(models)
        if parameters is not None:
            prompt.parameters = parameters
        
        with self.config.connection.cursor() as cursor:
            cursor.execute(
                self.queries["insert"],
                (prompt_name, json.dumps(prompt.models), json.dumps(prompt.parameters))
            )
            self.config.connection.commit()
        
        return prompt

    def delete_prompt(self, prompt_name: str):
        """Eliminar un prompt"""
        if prompt_name not in self.prompts:
            raise ValueError(f"El prompt '{prompt_name}' no existe")
        
        with self.config.connection.cursor() as cursor:
            cursor.execute(self.queries["delete"], (prompt_name,))
            self.config.connection.commit()
        
        del self.prompts[prompt_name]

    def get_prompt(self, prompt_name: str, model: str, parameters: Dict[str, str] = None) -> str:
        """Obtener el contenido del prompt para un modelo específico"""
        if prompt_name not in self.prompts:
            raise ValueError(f"El prompt '{prompt_name}' no existe")
        
        prompt = self.prompts[prompt_name]
        if model not in prompt.models:
            raise ValueError(f"El modelo '{model}' no existe para el prompt '{prompt_name}'")
        
        content = prompt.models[model]
        
        if parameters:
            # Verificar que todos los parámetros requeridos estén presentes
            missing_params = set(prompt.parameters) - set(parameters.keys())
            if missing_params:
                raise ValueError(f"Faltan parámetros requeridos: {missing_params}")
            
            # Reemplazar los parámetros en el contenido
            for key, value in parameters.items():
                content = content.replace(f"{{{key}}}", str(value))
        
        return content

    def list_prompts(self) -> List[str]:
        """Listar todos los prompts disponibles"""
        return list(self.prompts.keys())

    def get_prompt_info(self, prompt_name: str) -> Dict:
        """Obtener información detallada de un prompt"""
        if prompt_name not in self.prompts:
            raise ValueError(f"El prompt '{prompt_name}' no existe")
        
        prompt = self.prompts[prompt_name]
        return {
            'prompt_name': prompt.prompt_name,
            'models': list(prompt.models.keys()),
            'parameters': prompt.parameters
        } 