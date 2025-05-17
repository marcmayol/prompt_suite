from prompt_suite import PromptSuite   # Make sure your class is in prompt_suite.py or adjust the import accordingly

# Path to the YAML prompt file
example_path = "example_prompts.yaml"

# Initialize PromptSuite using YAML format
suite = PromptSuite(file_path=example_path, file_format="")

# 1. List all available prompts
print("📌 Available prompts:")
print(suite.list_prompts())

# 2. Get a prompt with parameter substitution
print("\n🧠 Get 'instagram-editor' prompt:")
print(suite.get_prompt(
    name="instagram-editor",
    params={"post": "Launching our new AI tool!", "hashtags": "#AI #Launch"}
))

# 3. Create a new prompt
print("\n✨ Creating new prompt 'product-review-generator'")
suite.create_prompt(
    name="product-review-generator",
    parameters=["product_name", "rating"],
    versions={
        "gpt-4o": "Generate a review for {product_name} with a rating of {rating} stars.",
        "gemini-pro": "You are a review expert. Write a {rating}-star review of {product_name}."
    },
    default="gpt-4o"
)

# 4. Add a new version to the prompt
print("\n➕ Adding version 'claude-opus' to 'product-review-generator'")
suite.add_version(
    name="product-review-generator",
    version="claude-opus",
    content="Review the product {product_name}. Rating: {rating} stars.",
    set_as_default=True
)

# 5. Update the entire prompt
print("\n🔧 Updating 'product-review-generator' with new parameters, a new version, and changing the default")
suite.update_prompt(
    name="product-review-generator",
    parameters=["product_name", "rating", "features"],
    versions={
        "mistral": "Write a {rating}-star review of {product_name}. Focus on: {features}."
    },
    default="mistral"
)

# 6. Rename the prompt
print("\n✏️ Renaming 'product-review-generator' to 'review-writer'")
suite.rename_prompt("product-review-generator", "review-writer")

# 7. Delete a prompt
print("\n❌ Deleting 'bug-report-generator'")
suite.delete_prompt("bug-report-generator")

# 8. List available versions of a prompt
print("\n📚 Listing versions for 'instagram-editor'")
versions = suite.list_versions("instagram-editor")
print(f"Available versions: {versions}")

# 9. Get default version for a prompt
print("\n⭐ Default version for 'instagram-editor'")
default_version = suite.get_default_version("instagram-editor")
print(f"Default version: {default_version}")

# 10. List final prompts
print("\n📦 Final prompt list:")
print(suite.list_prompts())
