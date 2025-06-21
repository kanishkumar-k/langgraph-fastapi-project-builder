import os
import subprocess
import sys
import random
import string
import time
from datetime import datetime


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def generate_password(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def setup_postgresql():
    try:
        db_user = "postgres"
        db_password = generate_password()
        db_name = "mydb"
        container_name = "devin_pg"

        running = subprocess.check_output(["podman", "ps", "--format", "{{.Names}}"]).decode().splitlines()
        if container_name not in running:
            print("🛠️ Starting new PostgreSQL container...")
            subprocess.run([
                "podman", "run", "--name", container_name,
                "-e", f"POSTGRES_USER={db_user}",
                "-e", f"POSTGRES_PASSWORD={db_password}",
                "-e", f"POSTGRES_DB={db_name}",
                "-p", "5432:5432",
                "-d", "postgres"
            ], check=True)
            print("⏳ Waiting for PostgreSQL to start...")
            time.sleep(10)
        else:
            print("✅ PostgreSQL container already running.")
        return db_user, db_password, db_name
    except Exception as e:
        print(f"PostgreSQL setup error: {e}")
        return None, None, None


def setup_venv(project):
    try:
        venv_path = os.path.join(project, "venv")
        print("🐍 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)

        pip = os.path.join(venv_path, "Scripts", "pip.exe") if os.name == "nt" else os.path.join(venv_path, "bin", "pip")
        subprocess.run([pip, "install", "-r", os.path.join(project, "requirements.txt")], check=True)
    except Exception as e:
        print(f"Virtualenv setup error: {e}")


def create_folders(project):
    paths = ["app/api/routes", "app/models", "app/services", "tests"]
    for path in paths:
        os.makedirs(os.path.join(project, path), exist_ok=True)


def create_static_files(project, db_user, db_password, db_name):
    try:
        write_file(os.path.join(project, ".env"), f"DATABASE_URL=postgresql://{db_user}:{db_password}@localhost:5432/{db_name}")
        write_file(os.path.join(project, "requirements.txt"), "\n".join([
            "fastapi", "uvicorn", "psycopg2-binary", "alembic", "sqlalchemy", "python-dotenv"
        ]))
        write_file(os.path.join(project, "README.md"), f"# {project}\n\n")

        write_file(os.path.join(project, "app", "main.py"), """from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to your FastAPI app!"}
""")

        write_file(os.path.join(project, "app", "database.py"), """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
""")

        for path in ["app/api/routes", "app/models"]:
            write_file(os.path.join(project, path, "__init__.py"), "")
    except Exception as e:
        print(f"Static file creation error: {e}")


def setup_alembic(project, db_user, db_password, db_name):
    try:
        os.chdir(project)
        subprocess.run(["alembic", "init", "migrations"], check=True)

        with open("alembic.ini", "r", encoding="utf-8") as f:
            cfg = f.read()
        cfg = cfg.replace(
            "sqlalchemy.url = driver://user:pass@localhost/dbname",
            f"sqlalchemy.url = postgresql://{db_user}:{db_password}@localhost:5432/{db_name}"
        )
        with open("alembic.ini", "w", encoding="utf-8") as f:
            f.write(cfg)

        env_path = os.path.join("migrations", "env.py")
        with open(env_path, "r", encoding="utf-8") as f:
            env = f.read()
        env = env.replace(
            "target_metadata = None",
            "from app.database import Base\n"
            "target_metadata = Base.metadata"
        ).replace(
            "# add your model's MetaData object here",
            "from app.models import user, item  # Ensure models are imported"
        )
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env)

        os.chdir("..")
    except Exception as e:
        print(f"Alembic setup error: {e}")


# 🌟 LangGraph Node 2 Function
def node2_generate_setup():
    try:
        project =  f"fastapi_project_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        print(f"🚀 Creating: {project}")
        os.makedirs(project, exist_ok=True)
        create_folders(project)

        db_user, db_password, db_name = setup_postgresql()
        create_static_files(project, db_user, db_password, db_name)
        setup_venv(project)

        if db_user and db_password and db_name:
            setup_alembic(project, db_user, db_password, db_name)

        print("FastAPI project setup completed!")
        # print("Running FastAPI app...")

        # uvicorn_exec = os.path.join(project, "venv", "Scripts", "uvicorn.exe") if os.name == "nt" else os.path.join(project, "venv", "bin", "uvicorn")
        # subprocess.Popen([uvicorn_exec, "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"], cwd=project)

        # print("🎉 Your FastAPI project is live at http://localhost:8000")

        return {
            "project_name": project,
            "db_user": db_user,
            "db_password": db_password,
            "db_name": db_name
        }
    



    except Exception as e:
        print(f"Agent setup error: {e}")
        return {"error": str(e)}


if __name__ == "__main__":

    result = node2_generate_setup()
    print("\n📦 Final Result State:\n", result)


