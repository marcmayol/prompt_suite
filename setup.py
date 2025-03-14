from setuptools import setup, find_packages

setup(
    name="prompt-manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0.1",
        "pydantic>=2.5.2",
        "psycopg2-binary>=2.9.9",  # Para soporte de PostgreSQL
    ],
    author="Tu Nombre",
    author_email="tu.email@ejemplo.com",
    description="Una biblioteca para gestionar prompts de IA con soporte para YAML y SQL",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tu-usuario/prompt-manager",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
) 