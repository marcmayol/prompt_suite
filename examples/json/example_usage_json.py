from prompt_suite import PromptSuite  # Make sure your class is in prompt_suite.py or adjust the import accordingly

# Path to the example prompt JSON file
example_path = "example_prompts.json"

# Initialize the PromptSuite with the JSON file
suite = PromptSuite(file_path=example_path, file_format="")

# 1. List available prompts
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
print(suite.create_prompt(
    name="product-review-generator",
    parameters=["product_name", "rating"],
    versions={
        "gpt-4o": "Generate a review for {product_name} with a rating of {rating} stars.",
        "gemini-pro": "You are a review expert. Write a {rating}-star review of {product_name}."
    },
    default="gemini-pro"
))
print(suite.get_prompt(name="product-review-generator",
                       params={"product_name": "ps5", "rating": "5"}))

# 4. Add a new version to an existing prompt
print("\n➕ Adding new version 'claude-opus' to 'product-review-generator'")
print(suite.add_version(
    name="product-review-generator",
    version="claude-opus",
    content="Review the product {product_name}. Rating: {rating} stars.",
    set_as_default=True
))
# 5. List available versions for a specific prompt
print("\n📚 Listing versions for 'product-review-generator'")
versions = suite.list_versions("product-review-generator")
print(versions)

# 6. Update the entire prompt: parameters, versions, and default version
print("\n🔧 Updating 'product-review-generator' with new parameters, a new version, and changing the default")
print(suite.update_prompt(
    name="product-review-generator",
    parameters=["product_name", "rating", "features"],
    versions={
        "mistral": "Write a {rating}-star review of {product_name}. Focus on: {features}."
    },
    default="mistral"
))
print(suite.get_prompt(name="product-review-generator",
                       params={"product_name": "ps5", "rating": "5", "features": "graphics,speed"}))

# 7. Get the default version of a specific prompt
print("\n⭐ Default version for 'instagram-editor'")
default_version = suite.get_default_version("instagram-editor")
print(f"Default version: {default_version}")

# 8. Rename a prompt
print("\n✏️ Renaming 'product-review-generator' to 'review-writer'")
print(suite.rename_prompt("product-review-generator", "review-writer"))
print(suite.get_prompt(name="review-writer",
                       params={"product_name": "ps5", "rating": "5", "features": "graphics,speed"}))

# 9. Delete a prompt
print("\n❌ Deleting 'email-summarizer'")
print(suite.delete_prompt("email-summarizer"))

# 10. List prompts again to see final state
print("\n📦 Final prompt list:")
print(suite.list_prompts())
