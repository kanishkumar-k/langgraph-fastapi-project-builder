import json
import os
import subprocess
import sys
from functools import lru_cache
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

REQUIRED_PACKAGES = ["groq"]

def install_missing_packages():
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

install_missing_packages()

from groq import Groq

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

def load_extracted_data():
    try:
        with open("extracted_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(1)
    except json.JSONDecodeError:
        sys.exit(1)

@lru_cache(maxsize=128)
def generate_code_from_groq(prompt: str):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return ""

def get_latest_project_dir():
    base_dir = os.getcwd()
    dirs = [d for d in os.listdir(base_dir) if d.startswith("fastapi_project_")]
    if not dirs:
        raise FileNotFoundError("No fastapi_project_ folder found.")
    dirs.sort(reverse=True)
    return os.path.join(base_dir, dirs[0])

def sanitize_filename(path: str):
    path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
    return path if path else "root"

def generate_code_from_requirements():
    extracted_data = load_extracted_data()
    project_dir = get_latest_project_dir()

    for data in extracted_data:
        api_endpoints = data.get("api_endpoints", [])
        database_schema = data.get("database_schema", {})
        authentication = data.get("authentication", {})

        for endpoint in api_endpoints:
            method = endpoint.get("method", "GET")
            path = endpoint.get("path", "/")
            description = endpoint.get("description", "")
            parameters = endpoint.get("parameters", [])

            route_file_name = f"{sanitize_filename(path)}.py"
            route_file_path = os.path.join(project_dir, "app/api/routes", route_file_name)

            prompt = f"""
            Write strict FastAPI code for a {method.upper()} API endpoint:
            - Path: {path}
            - Method: {method}
            - Parameters: {json.dumps(parameters)}
            """

            generated_code = generate_code_from_groq(prompt)

            with open(route_file_path, "w", encoding="utf-8") as f:
                f.write(generated_code.strip())

            service_file_name = f"{sanitize_filename(path)}_service.py"
            service_file_path = os.path.join(project_dir, "app/services", service_file_name)

            prompt_service = f"""
            Write a service layer for the {method.upper()} API endpoint:
            - Path: {path}
            - Method: {method}
            - Parameters: {json.dumps(parameters)}
            - Include necessary CRUD logic based on the json file provided and test cases.
            """

            generated_service_code = generate_code_from_groq(prompt_service)

            with open(service_file_path, "w", encoding="utf-8") as f:
                f.write(generated_service_code.strip())

        tables = database_schema.get("tables", {})
        for table_name, table_details in tables.items():
            columns = table_details.get("columns", {})
            primary_key = table_details.get("primary_key", "")
            foreign_keys = table_details.get("foreign_keys", [])

            model_file_name = f"{sanitize_filename(table_name)}.py"
            model_file_path = os.path.join(project_dir, "app/models", model_file_name)

            prompt = f"""
            Write strict FastAPI SQLAlchemy model code:
            - Table: {table_name}
            - Columns: {json.dumps(columns)}
            - Primary Key: {primary_key}
            - Foreign Keys: {json.dumps(foreign_keys)}
            """

            generated_code = generate_code_from_groq(prompt)

            with open(model_file_path, "w", encoding="utf-8") as f:
                f.write(generated_code.strip())

        if authentication:
            auth_type = authentication.get("type", "JWT")
            roles = authentication.get("roles", [])
            rules = authentication.get("rules", [])

            auth_file_path = os.path.join(project_dir, "app/auth.py")
            prompt = f"""
            Write strict FastAPI code for {auth_type} authentication handler:
            - Authentication Type: {auth_type}
            - Roles: {json.dumps(roles)}
            - Rules: {json.dumps(rules)}
            """

            generated_code = generate_code_from_groq(prompt)

            with open(auth_file_path, "w", encoding="utf-8") as f:
                f.write(generated_code.strip())

if __name__ == "__main__":
    generate_code_from_requirements()


