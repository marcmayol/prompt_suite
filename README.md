# Prompt Suite

**Prompt Suite** is a lightweight and extensible Python library for managing prompts with version control, model-specific variations, and flexible storage. It is built on the idea that **prompts are not just text — they are code**.

## 🚀 Features

* 🧠 **Model-specific prompts**: Store and retrieve prompt variations for different models (e.g., GPT-4, Claude, Gemini).
* 🔄 **Version control**: Keep track of different versions of each prompt.
* 📆 **Flexible storage**: Use YAML, JSON, or SQL to store your prompts.
* 🧹 **Placeholders system**: Create prompts with dynamic fields and fill them easily at runtime.
* 💡 **Customizable structure**: Easily adapt to your workflow and integration needs.

## 📆 Installation

```bash
pip install prompt-suite
```

## 🛠️ Basic Usage

### JSON/YAML-based

```python
from prompt_suite import PromptManager

# Load from JSON or YAML
manager = PromptManager.load("prompts.json")

# Get a prompt for a specific model
prompt = manager.get_prompt("generate_summary", model="gpt-4", params={"topic": "AI in healthcare"})

print(prompt)
```

### SQL-based

```python
from prompt_suite_sql import PromptSuiteSQL

# Create the instance (with default table creation)
db = PromptSuiteSQL(connection=my_conn, create_tables=True)

# Add a prompt and a version
db.add_prompt("generate_summary", description="Summary generator prompt")
db.add_version("generate_summary", model="gpt-4", prompt="Please summarize this: {{topic}}")

# Retrieve a prompt with parameters
prompt = db.get_prompt("generate_summary", model="gpt-4", params={"topic": "AI in healthcare"})

print(prompt)
```

## 📂 Prompt Structure (YAML/JSON example)

```yaml
- prompt_name: generate_summary
  parameters: [topic]
  versions:
    default:
      prompt: "Summarize this: {{topic}}"
    gpt-4:
      prompt: "Please provide a concise summary of: {{topic}}"
```

## 🔧 SQL Support

Use `PromptSuiteSQL` for SQL-based storage.
It supports:

* PostgreSQL
* MySQL
* SQLite
* And other SQL engines (driver-agnostic)

Custom queries and placeholder logic are supported for flexibility and integration into enterprise systems.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check [issues page](https://github.com/marcmayol/prompt-suite/issues) or submit a pull request.

## 📄 License

This project is licensed under the MIT License.
