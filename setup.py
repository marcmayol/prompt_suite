from setuptools import setup, find_packages

setup(
    name="prompt_suite",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0.1",
        "pydantic>=2.5.2",
        "psycopg2-binary>=2.9.9",  # Para soporte de PostgreSQL
    ],
    author="Marc Mayol",
    author_email="marcmyolorell@gmail.com",
    description="Prompt Suite is a library focused on prompt management, based on the idea that prompts are not just text,they are code. It allows you to store your prompts by model, keep version control, and save everything in YAML, JSON, or SQL. It also includes a powerful placeholder system to help you dynamically complete your prompts.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tu-usuario/prompt_suite",
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
