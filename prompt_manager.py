from typing import Dict, List, Optional, Any
import yaml
import json
from pathlib import Path
from pydantic import BaseModel, Field
import os

class ModelPrompt(BaseModel):
    model: str
    content: str

class Prompt(BaseModel):
    prompt_name: str
    models: Dict[str, str] = Field(default_factory=dict)
    parameters: List[str] = Field(default_factory=list)

class PromptManager:
    def __init__(self, file_path: Optional[str] = None, format: str = "yaml"):
        """
        Inicializa el gestor de prompts.
        
        Args:
            file_path (str, optional): Ruta al archivo donde se guardarán los prompts.
                                     Si no se proporciona, se creará en la raíz del proyecto.
            format (str): Formato de almacenamiento ("yaml" o "json")
        """
        self.format = format.lower()
        if self.format not in ["yaml", "json"]:
            raise ValueError("El formato debe ser 'yaml' o 'json'")
        
        # Si no se proporciona ruta, crear en la raíz del proyecto
        if file_path is None:
            # Obtener la raíz del proyecto (directorio que contiene prompt_manager)
            project_root = Path(__file__).parent.parent
            default_filename = f"prompts.{self.format}"
            self.file_path = str(project_root / default_filename)
        else:
            self.file_path = file_path
        
        self.prompts: Dict[str, Dict[str, Any]] = {}
        self._load_prompts()

    def _load_prompts(self) -> None:
        """Carga los prompts desde el archivo si existe."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                if self.format == "yaml":
                    self.prompts = yaml.safe_load(f) or {}
                else:  # json
                    self.prompts = json.load(f) or {}

    def _save_prompts(self) -> None:
        """Guarda los prompts en el archivo."""
        # Asegurar que el directorio existe (si no es la raíz)
        directory = os.path.dirname(self.file_path)
        if directory:  # Si no es la raíz
            os.makedirs(directory, exist_ok=True)
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            if self.format == "yaml":
                yaml.dump(self.prompts, f, allow_unicode=True, sort_keys=False)
            else:  # json
                json.dump(self.prompts, f, ensure_ascii=False, indent=2)

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
        
        # Guardar automáticamente
        self._save_prompts()
        
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
        self.prompts[prompt_name] = prompt
        
        # Guardar automáticamente
        self._save_prompts()
        
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
        
        # Guardar automáticamente
        self._save_prompts()
        
        return prompt

    def delete_prompt(self, prompt_name: str):
        """Eliminar un prompt"""
        if prompt_name not in self.prompts:
            raise ValueError(f"El prompt '{prompt_name}' no existe")
        
        del self.prompts[prompt_name]
        
        # Guardar automáticamente
        self._save_prompts()

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

    def load_from_file(self, file_path: str, format: str = "yaml"):
        """Cargar prompts desde un archivo"""
        self.file_path = Path(file_path)
        self.format = format.lower()
        self._load_prompts() 