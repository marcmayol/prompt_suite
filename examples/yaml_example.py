from prompt_manager import PromptManager
import os

def main():
    print("\n=== Ejemplo de uso con YAML ===")
    
    # Obtener la ruta absoluta del directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(current_dir, "prompts.yaml")
    
    # Crear un gestor de prompts con YAML
    pm = PromptManager(yaml_path, format="yaml")
    
    # Mostrar los prompts disponibles
    print("\nPrompts disponibles:")
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