from prompt_manager import SQLPromptManager, SQLConfig
import psycopg2  # Solo como ejemplo, podría ser cualquier otro driver SQL

def main():
    print("\n=== Ejemplo de uso con SQL ===")
    
    try:
        # 1. Crear conexión a la base de datos (ejemplo con PostgreSQL)
        # Podría ser cualquier otra base de datos SQL (MySQL, SQLite, etc.)
        conn = psycopg2.connect(
            dbname="mi_base_datos",
            user="mi_usuario",
            password="mi_contraseña",
            host="localhost"
        )
        
        # 2. Crear un cursor genérico
        cursor = conn.cursor()
        
        # 3. Configurar el gestor de prompts con SQL
        config = SQLConfig(
            cursor=cursor,
            create_tables=True  # Crear tablas si no existen
        )
        
        # 4. Crear el gestor de prompts
        pm = SQLPromptManager(config)
        
        # 5. Crear un prompt de ejemplo
        pm.create_prompt(
            prompt_name="traductor",
            models={
                "gpt-4": "Traduce el siguiente texto al {idioma}: {texto}",
                "gpt-3.5-turbo": "Traduce: {texto}"
            },
            parameters=["idioma", "texto"]
        )
        
        # 6. Hacer commit de los cambios
        conn.commit()
        
        # 7. Usar el prompt
        texto = pm.get_prompt(
            prompt_name="traductor",
            model="gpt-4",
            parameters={
                "idioma": "inglés",
                "texto": "Hola, ¿cómo estás?"
            }
        )
        print(f"\nPrompt generado: {texto}")
        
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 