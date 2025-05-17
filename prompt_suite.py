import yaml, json, os
from pathlib import Path
from typing import Optional, Dict, List


class PromptSuite:
    def __init__(self, file_path: Optional[str] = None, file_format: Optional[str] = None):
        """
        Initializes the PromptSuite with format detection and validation.

        Args:
            file_path (Optional[str]): Path to the prompt file. If not provided, defaults to 'prompts.yaml' in the project root.
            file_format (Optional[str]): Desired format to work with ('json' or 'yaml').
                                         If not provided, it will be inferred from the file extension.

        Raises:
            RuntimeError: If initialization fails due to invalid configuration or loading issues.
        """
        try:
            self.file_path = file_path or str(Path(__file__).parent.parent / "prompts.yaml")

            # Infer or validate format
            inferred_format = None
            ext = os.path.splitext(self.file_path)[1].lower()
            if ext == ".json":
                inferred_format = "json"
            elif ext in [".yaml", ".yml"]:
                inferred_format = "yaml"

            if file_format:
                self.format = file_format.lower()
                if self.format not in ["json", "yaml"]:
                    raise ValueError("Invalid format. Must be 'json' or 'yaml'.")
                if inferred_format and self.format != inferred_format:
                    raise ValueError(
                        f"File extension '{ext}' does not match specified format '{self.format}'."
                    )
            else:
                if inferred_format:
                    self.format = inferred_format
                else:
                    raise ValueError("Could not infer file format. Please specify 'file_format' explicitly.")

            self._load_prompts()

        except Exception as e:
            raise RuntimeError(f"Error initializing PromptSuite: {e}")

    def _load_prompts(self):
        """
        Loads prompts from the specified YAML or JSON file into memory.

        If the file exists, it parses the content based on the selected format ('yaml' or 'json')
        and populates the `self.prompts` dictionary. If the file is empty or invalid, it initializes
        with an empty dictionary.

        This method is intended for internal use only.
        """
        self.prompts = {}
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) if self.format == "yaml" else json.load(f)
                self.prompts = data or {}

    def _save_prompts(self):
        """
        Saves the current prompts to the configured YAML or JSON file.

        Serializes the `self.prompts` dictionary and writes it to the file defined in `self.file_path`,
        using the appropriate format ('yaml' or 'json'). Handles Unicode and formatting options accordingly.

        Raises:
            RuntimeError: If an error occurs while writing to the file.
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                if self.format == "yaml":
                    yaml.dump(self.prompts, f, allow_unicode=True, sort_keys=False)
                else:
                    json.dump(self.prompts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise RuntimeError(f"Error saving prompts to file: {e}")

    def create_prompt(self, name: str, versions: Dict[str, str], parameters: Optional[List[str]] = None,
                      default: Optional[str] = None):
        """
        Creates and stores a new prompt with multiple model-specific versions.

        Args:
            name (str): The unique name identifier for the prompt.
            versions (Dict[str, str]): A dictionary where keys are model names (e.g., "gpt-4o", "gemini-pro")
                                       and values are the corresponding prompt strings.
            parameters (Optional[List[str]]): A list of parameter names expected in the prompt content.
            default (Optional[str]): The default model version to use if none is specified during retrieval.

        Returns:
            bool: True if the prompt was created successfully.

        Raises:
            ValueError: If a prompt with the same name already exists.
        """
        if name in self.prompts:
            raise ValueError("Prompt already exists.")
        data = {
            "name": name,
            "parameters": parameters or [],
            "versions": {k: {"prompt": v} for k, v in versions.items()}
        }
        if default:
            data["default"] = default
        self.prompts[name] = data
        self._save_prompts()
        return True

    def get_prompt(self, name: str, version: Optional[str] = None, params: Optional[Dict[str, str]] = None) -> str:
        """
        Retrieves and processes a prompt by version and parameter substitution.

        Args:
            name (str): The name of the prompt to retrieve.
            version (Optional[str]): The model version to use. If not provided, the default version is used (if defined).
            params (Optional[Dict[str, str]]): Dictionary of parameter values to replace in the prompt content.

        Returns:
            str: The final prompt string with all required parameters replaced.

        Raises:
            ValueError: If the prompt or version does not exist,
                        if no default version is set when needed,
                        or if required parameters are missing.
        """
        if name not in self.prompts:
            raise ValueError(f"Prompt '{name}' not found.")
        prompt_data = self.prompts[name]
        version = version or prompt_data.get("default")
        if not version:
            raise ValueError(f"No default version set for prompt '{name}'. Please specify a version.")
        if version not in prompt_data["versions"]:
            raise ValueError(f"Version '{version}' not found for prompt '{name}'.")

        prompt = prompt_data["versions"][version]["prompt"]
        expected_params = set(prompt_data.get("parameters", []))
        if expected_params:
            if not params:
                raise ValueError(f"Missing required parameters: {', '.join(expected_params)}")

            missing = expected_params - set(params.keys())
            if missing:
                raise ValueError(f"Missing required parameters: {', '.join(missing)}")
        if params:
            for k, v in params.items():
                prompt = prompt.replace(f"{{{k}}}", str(v))
        return prompt

    def add_version(self, name: str, version: str, content: str, set_as_default: bool = False):
        """
        Adds a new version to an existing prompt. Optionally sets it as the default version.

        Args:
            name (str): The name of the prompt to update.
            version (str): The version identifier to add (e.g., 'gpt-4o', 'gemini-pro').
            content (str): The prompt content for the specified version.
            set_as_default (bool): If True, sets this version as the default.

        Raises:
            ValueError: If the prompt does not exist, or if the version already exists.
        """
        if name not in self.prompts:
            raise ValueError(f"Prompt '{name}' not found.")

        if version in self.prompts[name]["versions"]:
            raise ValueError(f"Version '{version}' already exists for prompt '{name}'.")

        self.prompts[name]["versions"][version] = {"prompt": content}

        if set_as_default:
            self.prompts[name]["default"] = version

        self._save_prompts()
        return True

    def update_prompt(self, name: str, versions: Optional[Dict[str, str]] = None,
                      parameters: Optional[List[str]] = None, default: Optional[str] = None):
        """
        Updates an existing prompt with new versions, parameters, or default version.

        Args:
            name (str): The name of the prompt to update.
            versions (Optional[Dict[str, str]]): Dictionary of new or updated versions and their content.
            parameters (Optional[List[str]]): Updated list of expected parameters for the prompt.
            default (Optional[str]): New default version to set.

        Raises:
            ValueError: If the prompt does not exist.

        Returns:
            bool: True if the update was successful.
        """
        if name not in self.prompts:
            raise ValueError(f"Prompt '{name}' not found.")
        else:
            prompt = self.prompts[name]
            if versions:
                for k, v in versions.items():
                    prompt["versions"][k] = {"prompt": v}
            if parameters is not None:
                prompt["parameters"] = parameters
            if default is not None:
                prompt["default"] = default
            self._save_prompts()
        return True

    def rename_prompt(self, old_name: str, new_name: str):
        """
        Renames an existing prompt by changing its identifier key.

        Args:
            old_name (str): The current name of the prompt to rename.
            new_name (str): The new name to assign to the prompt.

        Raises:
            ValueError: If the original prompt does not exist, or if a prompt with the new name already exists.

        Returns:
            bool: True if the rename operation was successful.
        """
        if old_name not in self.prompts:
            raise ValueError(f"Prompt '{old_name}' not found.")
        if new_name in self.prompts:
            raise ValueError(f"A prompt with the name '{new_name}' already exists.")

        prompt_data = self.prompts.pop(old_name)
        prompt_data["name"] = new_name  # actualiza el campo interno también
        self.prompts[new_name] = prompt_data
        self._save_prompts()
        return True

    def delete_prompt(self, name: str):
        """
        Deletes a prompt from the collection by its name.

        Args:
            name (str): The name of the prompt to delete.

        Raises:
            ValueError: If the prompt does not exist.

        Returns:
            bool: True if the prompt was successfully deleted.
        """
        if name in self.prompts:
            del self.prompts[name]
            self._save_prompts()
        else:
            raise ValueError(f"Prompt '{name}' not found.")
        return True

    def list_versions(self, name: str) -> List[str]:
        """
        Returns a list of available model versions for the specified prompt.

        Args:
            name (str): The name of the prompt.

        Returns:
            List[str]: A list of version identifiers (e.g., 'gpt-4o', 'gemini-pro').

        Raises:
            ValueError: If the prompt does not exist.
        """
        if name not in self.prompts:
            raise ValueError(f"Prompt '{name}' not found.")
        return list(self.prompts[name]["versions"].keys())

    def get_default_version(self, name: str) -> Optional[str]:
        """
        Returns the default model version for a given prompt.

        Args:
            name (str): The name of the prompt.

        Returns:
            Optional[str]: The default version name if set, otherwise None.

        Raises:
            ValueError: If the prompt does not exist.
        """
        if name not in self.prompts:
            raise ValueError(f"Prompt '{name}' not found.")
        return self.prompts[name].get("default")

    def list_prompts(self) -> List[str]:
        """
        Returns a list of all prompt names currently stored.

        Returns:
            List[str]: A list containing the names of all available prompts.
        """
        return list(self.prompts.keys())
