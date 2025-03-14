from prompt_manager import PromptManager
import os

def main():
    print("\n=== Ejemplo de uso con JSON ===")
    
    # Obtener la ruta absoluta del directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "prompts.json")
    
    # Crear un gestor de prompts con JSON
    pm = PromptManager(json_path, format="json")
    
    # Crear varios prompts
    prompts = {
        "traductor": {
            "models": {
                "gpt-4": "Traduce el siguiente texto al {idioma}: {texto}",
                "gpt-3.5-turbo": "Traduce: {texto}"
            },
            "parameters": ["idioma", "texto"]
        },
        "analizador_sentimiento": {
            "models": {
                "gpt-4": "Analiza el sentimiento del siguiente texto: {texto}",
                "gpt-3.5-turbo": "¿Qué sentimiento expresa este texto?: {texto}"
            },
            "parameters": ["texto"]
        },
        "resumidor": {
            "models": {
                "gpt-4": "Resume el siguiente texto en {num_palabras} palabras: {texto}",
                "gpt-3.5-turbo": "Haz un resumen de {num_palabras} palabras: {texto}"
            },
            "parameters": ["texto", "num_palabras"]
        }
    }
    
    # Crear los prompts
    for name, data in prompts.items():
        pm.create_prompt(
            prompt_name=name,
            models=data["models"],
            parameters=data["parameters"]
        )
    
    print(f"\nArchivo JSON creado en: {json_path}")
    
    # Mostrar los prompts creados
    print("\nPrompts creados:")
    for prompt_name in pm.list_prompts():
        print(f"\nInformación del prompt '{prompt_name}':")
        print(pm.get_prompt_info(prompt_name))
    
    # Ejemplos de uso
    print("\nEjemplos de uso:")
    
    # Ejemplo 1: Traductor
    print("\n1. Traductor:")
    texto = pm.get_prompt(
        prompt_name="traductor",
        model="gpt-4",
        parameters={
            "idioma": "inglés",
            "texto": "Hola, ¿cómo estás?"
        }
    )
    print(f"Prompt generado: {texto}")
    
    # Ejemplo 2: Analizador de sentimiento
    print("\n2. Analizador de sentimiento:")
    texto = pm.get_prompt(
        prompt_name="analizador_sentimiento",
        model="gpt-4",
        parameters={
            "texto": "Me encanta este producto, es increíble"
        }
    )
    print(f"Prompt generado: {texto}")
    
    # Ejemplo 3: Resumidor
    print("\n3. Resumidor:")
    texto = pm.get_prompt(
        prompt_name="resumidor",
        model="gpt-4",
        parameters={
            "texto": "Este es un texto largo que necesita ser resumido...",
            "num_palabras": "50"
        }
    )
    print(f"Prompt generado: {texto}")

if __name__ == "__main__":
    main() 