import json
import os

def load_api_data(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            extracted_data = json.load(file)
        return extracted_data
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        return None


def prepare_readme_prompt(api_data, project_folder):
    prompt = "# Project Setup and Structure\n\n"
    prompt += "This README outlines the project setup, structure, and relevant details to get started with the FastAPI project.\n\n"


    prompt += "## Project Folder Structure\n"
    for root, dirs, files in os.walk(project_folder):
        for file in files:
            if file.endswith(".py"):
                prompt += f"- **{os.path.relpath(os.path.join(root, file), project_folder)}**: Python source code file\n"
        for dir in dirs:
            prompt += f"- **{os.path.relpath(os.path.join(root, dir), project_folder)}**: Folder\n"
    prompt += "\n"


    prompt += "## Backend Logic\n"
    backend_logic = api_data[0].get("backend_logic", [])
    if backend_logic:
        for logic in backend_logic:
            prompt += f"- {logic}\n"
    else:
        prompt += "No specific backend logic described.\n"
   
    prompt += "\n"


    prompt += "## Database Schema\n"
    db_schema = api_data[0].get("database_schema", {})
    if db_schema:
        prompt += "### Tables and Columns\n"
        for table_name, table_info in db_schema.get("tables", {}).items():
            prompt += f"#### {table_name} Table\n"
            prompt += "Columns:\n"
            for column_name, column_type in table_info.get("columns", {}).items():
                prompt += f"- `{column_name}`: `{column_type}`\n"
            if table_info.get("primary_key"):
                prompt += f"Primary Key: `{table_info['primary_key']}`\n"
            if table_info.get("foreign_keys"):
                prompt += "Foreign Keys:\n"
                for fk in table_info.get("foreign_keys", []):
                    if isinstance(fk, dict):
                        table = fk.get('table', 'Unknown table')
                        column = fk.get('column', 'Unknown column')
                        prompt += f"- References `{table}` (`{column}`)\n"
                    elif isinstance(fk, str):
                        prompt += f"- Foreign Key (String): {fk}\n"
                    elif isinstance(fk, list):
                        prompt += f"- Foreign Key (List): {', '.join(fk)}\n"
                    else:
                        prompt += f"- Invalid foreign key format: {fk}\n"
    else:
        prompt += "No database schema available.\n"
    prompt += "\n"


    prompt += "## Authentication\n"
    auth_info = api_data[0].get("authentication", {})
    if auth_info:
        prompt += f"**Authentication Type**: `{auth_info.get('type', 'Unknown')}`\n"
        if "roles" in auth_info:
            prompt += "Roles:\n"
            for role in auth_info.get("roles", []):
                prompt += f"- `{role}`\n"
        if "rules" in auth_info:
            prompt += "Rules:\n"
            for rule in auth_info.get("rules", []):
                prompt += f"- {rule}\n"
    else:
        prompt += "No authentication information available.\n"


    prompt += "\n## Key API Endpoints\n"
    for entry in api_data:
        for endpoint in entry.get("api_endpoints", []):
            method = endpoint.get("method", "UNKNOWN")
            path = endpoint.get("path", "UNKNOWN")
            description = endpoint.get("description", "No description available.")
            prompt += f"- `{method}` {path}: {description}\n"
    prompt += "\n"

    return prompt


def generate_readme_with_ai(prompt):

    generated_readme = f"# Auto-generated README\n\n{prompt}"
    return generated_readme


def save_readme_to_file(readme_content, project_folder):
    output_file_path = os.path.join(project_folder, "README.md")
    with open(output_file_path, "w", encoding="utf-8") as md_file:
        md_file.write(readme_content)
    print(f"✅ README saved to {output_file_path}")


def generate_readme(json_path, base_dir):
    api_data = load_api_data(json_path)
    if api_data is None:
        return


    dirs = [d for d in os.listdir(base_dir) if d.startswith("fastapi_project_") and os.path.isdir(os.path.join(base_dir, d))]
    if not dirs:
        print("❌ No project folder found.")
        return
    dirs.sort(reverse=True)
    project_folder = os.path.join(base_dir, dirs[0])


    prompt = prepare_readme_prompt(api_data, project_folder)

    readme_content = generate_readme_with_ai(prompt)

    save_readme_to_file(readme_content, project_folder)


base_dir = os.getcwd()  
json_file_path = os.path.join(base_dir, "extracted_data.json")


generate_readme(json_file_path, base_dir)


