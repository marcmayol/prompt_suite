from yaml_example import main as yaml_main
from json_example import main as json_main
from sql_example import main as sql_main

def main():
    print("=== Ejecutando todos los ejemplos ===")
    
    # Ejecutar ejemplo YAML
    yaml_main()
    
    # Ejecutar ejemplo JSON
    json_main()
    
    # Ejecutar ejemplo SQL
    sql_main()

if __name__ == "__main__":
    main() 