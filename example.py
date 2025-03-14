from prompt_manager import PromptManager

def main():
    # Ejemplo 1: Usar YAML
    print("\n=== Ejemplo 1: Usando YAML ===")
    pm_yaml = PromptManager("prompts.yaml", format="yaml")
    
    # Crear un prompt con YAML
    pm_yaml.create_prompt(
        prompt_name="traductor_yaml",
        models={
            "gpt-4": "Traduce al {idioma}: {texto}"
        },
        parameters=["idioma", "texto"]
    )
    print("\nPrompt creado en YAML:")
    print(pm_yaml.get_prompt_info("traductor_yaml"))
    
    # Ejemplo 2: Usar JSON
    print("\n=== Ejemplo 2: Usando JSON ===")
    pm_json = PromptManager("prompts.json", format="json")
    
    # Crear un prompt con JSON
    pm_json.create_prompt(
        prompt_name="traductor_json",
        models={
            "gpt-4": "Traduce al {idioma}: {texto}"
        },
        parameters=["idioma", "texto"]
    )
    print("\nPrompt creado en JSON:")
    print(pm_json.get_prompt_info("traductor_json"))
    
    # Ejemplo 3: Cargar desde diferentes formatos
    print("\n=== Ejemplo 3: Cargar desde diferentes formatos ===")
    
    # Cargar desde YAML
    pm_yaml.load_from_file("prompts.yaml", format="yaml")
    print("\nPrompts cargados desde YAML:")
    print(pm_yaml.list_prompts())
    
    # Cargar desde JSON
    pm_json.load_from_file("prompts.json", format="json")
    print("\nPrompts cargados desde JSON:")
    print(pm_json.list_prompts())
    
    # Ejemplo 4: Usar los prompts
    print("\n=== Ejemplo 4: Usar los prompts ===")
    
    # Usar prompt de YAML
    texto_yaml = pm_yaml.get_prompt(
        prompt_name="traductor_yaml",
        model="gpt-4",
        parameters={
            "idioma": "inglés",
            "texto": "Hola, ¿cómo estás?"
        }
    )
    print("\nPrompt YAML generado:")
    print(texto_yaml)
    
    # Usar prompt de JSON
    texto_json = pm_json.get_prompt(
        prompt_name="traductor_json",
        model="gpt-4",
        parameters={
            "idioma": "inglés",
            "texto": "Hola, ¿cómo estás?"
        }
    )
    print("\nPrompt JSON generado:")
    print(texto_json)

if __name__ == "__main__":
    main() 