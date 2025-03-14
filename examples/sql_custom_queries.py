from prompt_manager import SQLPromptManager, SQLConfig
import psycopg2  # Solo como ejemplo, podría ser cualquier otro driver SQL

def main():
    print("\n=== Ejemplo de uso con SQL (consultas personalizadas obligatorias) ===")
    print("Este ejemplo muestra qué consulta SQL corresponde a cada función del SQLPromptManager")
    
    try:
        # 1. Crear conexión a la base de datos
        conn = psycopg2.connect(
            dbname="mi_base_datos",
            user="mi_usuario",
            password="mi_contraseña",
            host="localhost"
        )
        
        # 2. Crear un cursor
        cursor = conn.cursor()
        
        # 3. Configurar el gestor de prompts con SQL
        # NOTA: Cuando create_tables=False, DEBES proporcionar TODAS las consultas SQL necesarias
        config = SQLConfig(
            cursor=cursor,
            create_tables=False,  # No crear tablas
            table_prefix="prompt_",  # Prefijo de las tablas existentes
            # Consultas personalizadas OBLIGATORIAS
            custom_queries={
                # Función: get_prompt()
                # Uso: pm.get_prompt(prompt_name="traductor", model="gpt-4", parameters={...})
                "get_prompt": """
                    SELECT p.name, p.parameters, m.model_name, m.template
                    FROM prompt_prompts p
                    JOIN prompt_models m ON p.id = m.prompt_id
                    WHERE p.name = %s AND m.model_name = %s
                """,
                
                # Función: get_prompt_info()
                # Uso: pm.get_prompt_info(prompt_name="traductor")
                "get_prompt_info": """
                    SELECT p.name, p.parameters, 
                           json_agg(json_build_object(
                               'model_name', m.model_name,
                               'template', m.template
                           )) as models
                    FROM prompt_prompts p
                    LEFT JOIN prompt_models m ON p.id = m.prompt_id
                    WHERE p.name = %s
                    GROUP BY p.name, p.parameters
                """,
                
                # Función: get_all_prompts()
                # Uso: pm.get_all_prompts()
                "get_all_prompts": """
                    SELECT DISTINCT p.name, p.parameters
                    FROM prompt_prompts p
                """,
                
                # Función: create_prompt()
                # Uso: pm.create_prompt(prompt_name="traductor", models={...}, parameters=[...])
                "create_prompt": """
                    INSERT INTO prompt_prompts (name, parameters)
                    VALUES (%s, %s)
                    RETURNING id
                """,
                
                # Función: create_model()
                # Uso: Interno, llamado por create_prompt()
                "create_model": """
                    INSERT INTO prompt_models (prompt_id, model_name, template)
                    VALUES (%s, %s, %s)
                """,

                # Función: update_prompt()
                # Uso: pm.update_prompt(prompt_name="traductor", parameters=[...])
                "update_prompt": """
                    UPDATE prompt_prompts 
                    SET parameters = %s
                    WHERE name = %s
                """,

                # Función: update_model()
                # Uso: pm.update_model(prompt_name="traductor", model="gpt-4", template="...")
                "update_model": """
                    UPDATE prompt_models m
                    SET template = %s
                    FROM prompt_prompts p
                    WHERE m.prompt_id = p.id 
                    AND p.name = %s 
                    AND m.model_name = %s
                """,

                # Función: delete_prompt()
                # Uso: pm.delete_prompt(prompt_name="traductor")
                "delete_prompt": """
                    DELETE FROM prompt_prompts
                    WHERE name = %s
                """,

                # Función: delete_model()
                # Uso: pm.delete_model(prompt_name="traductor", model="gpt-4")
                "delete_model": """
                    DELETE FROM prompt_models m
                    USING prompt_prompts p
                    WHERE m.prompt_id = p.id 
                    AND p.name = %s 
                    AND m.model_name = %s
                """
            }
        )
        
        # 4. Crear el gestor de prompts
        pm = SQLPromptManager(config)
        
        # 5. Ejemplos de uso con explicación de las consultas
        print("\n1. Ejemplo de get_prompt():")
        print("   Consulta SQL: get_prompt")
        print("   Parámetros: prompt_name='traductor', model='gpt-4'")
        texto = pm.get_prompt(
            prompt_name="traductor",
            model="gpt-4",
            parameters={
                "idioma": "inglés",
                "texto": "Hola, ¿cómo estás?"
            }
        )
        print(f"   Resultado: {texto}")
        
        print("\n2. Ejemplo de get_prompt_info():")
        print("   Consulta SQL: get_prompt_info")
        print("   Parámetros: prompt_name='traductor'")
        info = pm.get_prompt_info("traductor")
        print(f"   Resultado: {info}")
        
        print("\n3. Ejemplo de get_all_prompts():")
        print("   Consulta SQL: get_all_prompts")
        print("   Parámetros: ninguno")
        prompts = pm.get_all_prompts()
        print("   Resultado:")
        for prompt in prompts:
            print(f"   - {prompt['name']}: {prompt['parameters']}")

        print("\n4. Ejemplo de update_prompt():")
        print("   Consulta SQL: update_prompt")
        print("   Parámetros: prompt_name='traductor', parameters=['idioma', 'texto', 'nivel']")
        pm.update_prompt("traductor", ["idioma", "texto", "nivel"])

        print("\n5. Ejemplo de update_model():")
        print("   Consulta SQL: update_model")
        print("   Parámetros: prompt_name='traductor', model='gpt-4', template='Nueva plantilla...'")
        pm.update_model("traductor", "gpt-4", "Nueva plantilla...")

        print("\n6. Ejemplo de delete_model():")
        print("   Consulta SQL: delete_model")
        print("   Parámetros: prompt_name='traductor', model='gpt-3.5-turbo'")
        pm.delete_model("traductor", "gpt-3.5-turbo")

        print("\n7. Ejemplo de delete_prompt():")
        print("   Consulta SQL: delete_prompt")
        print("   Parámetros: prompt_name='traductor'")
        pm.delete_prompt("traductor")
        
        print("\nIMPORTANTE: Cuando create_tables=False, DEBES proporcionar TODAS las consultas SQL necesarias.")
        print("Cada función del SQLPromptManager requiere su consulta SQL correspondiente en custom_queries.")
        
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 