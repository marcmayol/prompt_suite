from typing import Dict, List, Optional, Any
import json


class PromptSuiteSQL:
    def __init__(self, connection, auto_setup: bool = True,
                 custom_queries: Optional[Dict[str, str]] = None,
                 table_suffix: str = ""):
        """
        Initializes the SQL-based PromptSuite.

        Args:
            connection: Active DB connection (must support .cursor()).
            auto_setup (bool): If True, creates necessary tables with default queries.
            custom_queries (Optional[Dict[str, str]]): Required if auto_setup is False.
            table_suffix (str): Optional suffix added to table names for isolation (e.g. "_dev", "_test").

        Raises:
            RuntimeError: If initialization fails or required custom queries are missing.
        """
        try:
            self.conn = connection
            self.cursor = self.conn.cursor()
            self.auto_setup = auto_setup
            self.table_suffix = table_suffix

            self.prompts_table = f"prompts{self.table_suffix}"
            self.versions_table = f"prompt_versions{self.table_suffix}"

            self.required_query_keys = [
                "get_prompt_by_name",
                "get_versions_by_prompt",
                "get_version_content",
                "create_prompt",
                "create_version",
                "update_prompt",
                "delete_prompt",
                "rename_prompt"
            ]

            if auto_setup:
                self._create_default_tables()
                self.queries = self._default_queries()
            else:
                if not custom_queries:
                    raise RuntimeError("custom_queries must be provided when auto_setup=False.")
                missing = set(self.required_query_keys) - set(custom_queries.keys())
                if missing:
                    raise RuntimeError(f"Missing required queries: {', '.join(missing)}")
                self.queries = custom_queries

        except Exception as e:
            raise RuntimeError(f"Error initializing PromptSuiteSQL: {e}")

    def _create_default_tables(self):
        prompts_table = f"prompts_{self.table_suffix}"
        versions_table = f"prompt_versions_{self.table_suffix}"

        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prompts_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_name TEXT UNIQUE NOT NULL,
                parameters TEXT,  -- comma-separated list of parameter names
                default_version TEXT
            );
        """)
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {versions_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id INTEGER,
                version TEXT NOT NULL,
                prompt_text TEXT NOT NULL,
                FOREIGN KEY(prompt_id) REFERENCES {prompts_table}(id) ON DELETE CASCADE
            );
        """)
        self.conn.commit()

    def _default_queries(self) -> Dict[str, Dict[str, Any]]:
        return {
            "get_prompt_by_name": {
                "query": (
                    "SELECT id, prompt_name, parameters, default_version "
                    "FROM {prompts_table} WHERE prompt_name = :prompt_name;"
                ),
                "params": ["prompt_name"]
            },
            "get_versions_by_prompt": {
                "query": (
                    "SELECT version FROM {versions_table} "
                    "WHERE prompt_id = :prompt_id;"
                ),
                "params": ["prompt_id"]
            },
            "get_version_content": {
                "query": (
                    "SELECT prompt_text FROM {versions_table} "
                    "WHERE prompt_id = :prompt_id AND version = :version;"
                ),
                "params": ["prompt_id", "version"]
            },
            "get_all_prompts": {
                "query": (
                    "SELECT prompt_name FROM {prompts_table};"
                ),
                "params": []
            },
            "get_prompt_id_by_name": {
                "query": (
                    "SELECT id FROM {prompts_table} WHERE prompt_name = :prompt_name;"
                ),
                "params": ["prompt_name"]
            },
            "create_prompt": {
                "query": (
                    "INSERT INTO {prompts_table} (prompt_name, parameters, default_version) "
                    "VALUES (:prompt_name, :parameters, :default_version);"
                ),
                "params": ["prompt_name", "parameters", "default_version"]
            },
            "create_version": {
                "query": (
                    "INSERT INTO {versions_table} (prompt_id, version, prompt_text) "
                    "VALUES (:prompt_id, :version, :prompt_text);"
                ),
                "params": ["prompt_id", "version", "prompt_text"]
            },
            "update_prompt": {
                "query": (
                    "UPDATE {prompts_table} SET parameters = :parameters, default_version = :default_version "
                    "WHERE id = :id;"
                ),
                "params": ["parameters", "default_version", "id"]
            },
            "delete_prompt": {
                "query": (
                    "DELETE FROM {prompts_table} WHERE prompt_name = :prompt_name;"
                ),
                "params": ["prompt_name"]
            },
            "rename_prompt": {
                "query": (
                    "UPDATE {prompts_table} SET prompt_name = :new_name WHERE prompt_name = :old_name;"
                ),
                "params": ["new_name", "old_name"]
            }
        }

    def _run_query(self, key: str, params: Dict[str, Any], fetch: str = "none"):
        """
        Executes a query by key using its param list and returns optional results.

        Args:
            key (str): The query name in self.queries.
            params (Dict[str, Any]): The values for the query.
            fetch (str): Can be 'one', 'all' or 'none'.

        Returns:
            Any: Fetched results if fetch is 'one' or 'all', otherwise None.

        Raises:
            RuntimeError: If the query execution fails or parameters are missing.
        """
        try:
            if key not in self.queries:
                raise KeyError(f"Query '{key}' not defined.")

            query_obj = self.queries[key]
            raw_query = query_obj["query"]
            expected_params = query_obj["params"]

            # Validate required parameters
            missing = [k for k in expected_params if k not in params]
            if missing:
                raise ValueError(f"Missing parameters for query '{key}': {', '.join(missing)}")

            # Format table names if used in the query
            placeholders = {
                "prompts_table": self.prompts_table,
                "versions_table": self.versions_table,
            }
            try:
                query = raw_query.format(**{
                    k: v for k, v in placeholders.items() if f"{{{k}}}" in raw_query
                })
            except KeyError as e:
                raise RuntimeError(f"Missing table placeholder in query '{key}': {e}")
            except (ValueError, IndexError) as e:
                raise RuntimeError(f"Invalid placeholder syntax in query '{key}': {e}")
            except Exception as e:
                raise RuntimeError(f"Unexpected error formatting query '{key}': {e}")

            # Order parameter values
            values = tuple(params[k] for k in expected_params)

            # Execute query
            self.cursor.execute(query, values)

            if fetch == "one":
                return self.cursor.fetchone()
            elif fetch == "all":
                return self.cursor.fetchall()
            return None

        except Exception as e:
            raise RuntimeError(f"Error running query '{key}': {e}")

    def create_prompt(self, prompt_name: str, versions: Dict[str, str],
                      parameters: Optional[List[str]] = None,
                      default: Optional[str] = None) -> bool:
        """
        Creates a new prompt with the given name, parameters, versions, and optional default version.

        Args:
            prompt_name (str): The unique name of the prompt.
            versions (Dict[str, str]): A dictionary of version_name → prompt_text.
            parameters (Optional[List[str]]): A list of parameter names used in the prompt.
            default (Optional[str]): The default version to use (must match a key in `versions`).

        Returns:
            bool: True if the prompt and versions were successfully created.

        Raises:
            RuntimeError: If the prompt already exists or any step fails.
        """
        try:
            # Check if the prompt already exists
            existing = self._run_query("get_prompt_by_name", {"prompt_name": prompt_name}, fetch="one")
            if existing:
                raise RuntimeError(f"Prompt '{prompt_name}' already exists.")

            # Serialize parameters
            param_str = json.dumps(parameters or [])

            # Insert prompt into DB
            self._run_query("create_prompt", {
                "prompt_name": prompt_name,
                "parameters": param_str,
                "default_version": default
            })

            # Retrieve the prompt ID
            result = self._run_query("get_prompt_id_by_name", {"prompt_name": prompt_name}, fetch="one")
            if not result:
                raise RuntimeError(f"Failed to retrieve ID for prompt '{prompt_name}'.")
            prompt_id = result[0]

            # Insert each version
            for version, text in versions.items():
                self._run_query("create_version", {
                    "prompt_id": prompt_id,
                    "version": version,
                    "prompt_text": text
                })

            self.conn.commit()
            return True

        except Exception as e:
            raise RuntimeError(f"Error creating prompt '{prompt_name}': {e}")

    import json

    def get_prompt(self, prompt_name: str, version: Optional[str] = None,
                   params: Optional[Dict[str, str]] = None) -> str:
        """
        Retrieves and renders the prompt content for a specific version, injecting parameters.

        Args:
            prompt_name (str): The name of the prompt.
            version (Optional[str]): The specific version to use. If not provided, uses the default version.
            params (Optional[Dict[str, str]]): A dictionary of parameters to replace in the prompt content.

        Returns:
            str: The final prompt string with parameters applied.

        Raises:
            RuntimeError: If the prompt or version is not found or required parameters are missing.
        """
        try:
            # Get the full prompt record
            prompt = self._run_query("get_prompt_by_name", {"prompt_name": prompt_name}, fetch="one")
            if not prompt:
                raise RuntimeError(f"Prompt '{prompt_name}' not found.")

            prompt_id, prompt_name_db, parameters_json, default_version = prompt

            # Select the version to use
            selected_version = version or default_version
            if not selected_version:
                raise RuntimeError(f"No version specified and no default set for prompt '{prompt_name}'.")

            # Get the prompt content for the selected version
            result = self._run_query("get_version_content", {
                "prompt_id": prompt_id,
                "version": selected_version
            }, fetch="one")

            if not result:
                raise RuntimeError(f"Version '{selected_version}' not found for prompt '{prompt_name}'.")

            prompt_text = result[0]

            # Load expected parameters from stored JSON
            expected_params = json.loads(parameters_json or "[]")

            # Validate and replace parameters
            if expected_params:
                if not params:
                    raise ValueError(f"Missing required parameters: {', '.join(expected_params)}")

                missing = [p for p in expected_params if p not in params]
                if missing:
                    raise ValueError(f"Missing required parameters: {', '.join(missing)}")

                for key, value in params.items():
                    prompt_text = prompt_text.replace(f"{{{key}}}", str(value))

            return prompt_text

        except Exception as e:
            raise RuntimeError(f"Error retrieving prompt '{prompt_name}': {e}")

    def add_version(self, prompt_name: str, version: str, content: str) -> bool:
        """
        Adds a new version to an existing prompt.

        Args:
            prompt_name (str): Name of the prompt to add the version to.
            version (str): Version name to add (e.g., 'gpt-4o').
            content (str): Prompt content for this version.

        Returns:
            bool: True if the version was added successfully.

        Raises:
            RuntimeError: If the prompt does not exist or the version already exists.
        """
        try:
            # Get the prompt ID
            prompt = self._run_query("get_prompt_id_by_name", {"prompt_name": prompt_name}, fetch="one")
            if not prompt:
                raise RuntimeError(f"Prompt '{prompt_name}' not found.")
            prompt_id = prompt[0]

            # Check if the version already exists
            existing = self._run_query("get_version_content", {
                "prompt_id": prompt_id,
                "version": version
            }, fetch="one")
            if existing:
                raise RuntimeError(f"Version '{version}' already exists for prompt '{prompt_name}'.")

            # Insert the new version
            self._run_query("create_version", {
                "prompt_id": prompt_id,
                "version": version,
                "prompt_text": content
            })

            self.conn.commit()
            return True

        except Exception as e:
            raise RuntimeError(f"Error adding version '{version}' to prompt '{prompt_name}': {e}")

    def update_prompt(self, prompt_name: str,
                      versions: Optional[Dict[str, str]] = None,
                      parameters: Optional[List[str]] = None,
                      default: Optional[str] = None) -> bool:
        """
        Updates the parameters, default version, and/or adds new versions to an existing prompt.

        Args:
            prompt_name (str): Name of the prompt to update.
            versions (Optional[Dict[str, str]]): New versions to add (won't overwrite existing ones).
            parameters (Optional[List[str]]): New list of parameters.
            default (Optional[str]): New default version.

        Returns:
            bool: True if the update was successful.

        Raises:
            RuntimeError: If the prompt does not exist or an error occurs.
        """
        try:
            # Get the prompt info
            prompt = self._run_query("get_prompt_by_name", {"prompt_name": prompt_name}, fetch="one")
            if not prompt:
                raise RuntimeError(f"Prompt '{prompt_name}' not found.")

            prompt_id, _, parameters_json, current_default = prompt

            # Update parameters and/or default version
            if parameters is not None or default is not None:
                param_str = json.dumps(parameters) if parameters is not None else parameters_json
                default_version = default if default is not None else current_default

                self._run_query("update_prompt", {
                    "parameters": param_str,
                    "default_version": default_version,
                    "id": prompt_id
                })

            # Add new versions if provided
            if versions:
                for version, text in versions.items():
                    existing = self._run_query("get_version_content", {
                        "prompt_id": prompt_id,
                        "version": version
                    }, fetch="one")
                    if existing:
                        continue  # skip if version already exists

                    self._run_query("create_version", {
                        "prompt_id": prompt_id,
                        "version": version,
                        "prompt_text": text
                    })

            self.conn.commit()
            return True

        except Exception as e:
            raise RuntimeError(f"Error updating prompt '{prompt_name}': {e}")

    def rename_prompt(self, old_name: str, new_name: str) -> bool:
        """
        Renames an existing prompt.

        Args:
            old_name (str): Current name of the prompt.
            new_name (str): New name to assign.

        Returns:
            bool: True if the prompt was renamed successfully.

        Raises:
            RuntimeError: If the old prompt does not exist or the new name is already taken.
        """
        try:
            # Ensure the old prompt exists
            if not self._run_query("get_prompt_by_name", {"prompt_name": old_name}, fetch="one"):
                raise RuntimeError(f"Prompt '{old_name}' not found.")

            # Ensure the new name is not already used
            if self._run_query("get_prompt_by_name", {"prompt_name": new_name}, fetch="one"):
                raise RuntimeError(f"A prompt with the name '{new_name}' already exists.")

            # Rename the prompt
            self._run_query("rename_prompt", {
                "old_name": old_name,
                "new_name": new_name
            })

            self.conn.commit()
            return True

        except Exception as e:
            raise RuntimeError(f"Error renaming prompt '{old_name}' to '{new_name}': {e}")

    def delete_prompt(self, prompt_name: str) -> bool:
        """
        Deletes a prompt and all its associated versions from the database.

        Args:
            prompt_name (str): The name of the prompt to delete.

        Returns:
            bool: True if the deletion was successful.

        Raises:
            RuntimeError: If the prompt does not exist or deletion fails.
        """
        try:
            # Confirm the prompt exists
            if not self._run_query("get_prompt_by_name", {"prompt_name": prompt_name}, fetch="one"):
                raise RuntimeError(f"Prompt '{prompt_name}' not found.")

            # Delete the prompt
            self._run_query("delete_prompt", {"prompt_name": prompt_name})

            self.conn.commit()
            return True

        except Exception as e:
            raise RuntimeError(f"Error deleting prompt '{prompt_name}': {e}")

    def list_versions(self, prompt_name: str) -> List[str]:
        """
        Returns a list of version names for a given prompt.

        Args:
            prompt_name (str): The name of the prompt.

        Returns:
            List[str]: A list of version names.

        Raises:
            RuntimeError: If the prompt does not exist or the query fails.
        """
        try:
            # Get the prompt ID
            prompt = self._run_query("get_prompt_id_by_name", {"prompt_name": prompt_name}, fetch="one")
            if not prompt:
                raise RuntimeError(f"Prompt '{prompt_name}' not found.")
            prompt_id = prompt[0]

            # Fetch versions associated with the prompt
            results = self._run_query("get_versions_by_prompt", {"prompt_id": prompt_id}, fetch="all")
            return [row[0] for row in results] if results else []

        except Exception as e:
            raise RuntimeError(f"Error listing versions for prompt '{prompt_name}': {e}")

    def get_default_version(self, prompt_name: str) -> str:
        """
        Returns the default version name for a given prompt.

        Args:
            prompt_name (str): The name of the prompt.

        Returns:
            str: The default version name.

        Raises:
            RuntimeError: If the prompt does not exist or no default is set.
        """
        try:
            prompt = self._run_query("get_prompt_by_name", {"prompt_name": prompt_name}, fetch="one")
            if not prompt:
                raise RuntimeError(f"Prompt '{prompt_name}' not found.")

            default_version = prompt[3]  # [id, prompt_name, parameters, default_version]
            if not default_version:
                raise RuntimeError(f"No default version set for prompt '{prompt_name}'.")

            return default_version

        except Exception as e:
            raise RuntimeError(f"Error retrieving default version for prompt '{prompt_name}': {e}")

    def list_prompts(self) -> List[str]:
        """
        Returns a list of all prompt names stored in the database.

        Returns:
            List[str]: A list of prompt names.

        Raises:
            RuntimeError: If the query fails.
        """
        try:
            results = self._run_query("get_all_prompts", {}, fetch="all")
            return [row[0] for row in results] if results else []

        except Exception as e:
            raise RuntimeError(f"Error listing prompts: {e}")

