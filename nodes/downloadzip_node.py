import zipfile
import shutil
import os

BASE_DIR = os.getcwd()  

def get_latest_project_folder():
    dirs = [d for d in os.listdir(BASE_DIR) if d.startswith("fastapi_project_") and os.path.isdir(os.path.join(BASE_DIR, d))]
    if not dirs:
        raise FileNotFoundError("❌ No project folder found.")
    dirs.sort(reverse=True)  
    return os.path.join(BASE_DIR, dirs[0])

def zip_project_folder(project_dir):
    zip_filename = f"{os.path.basename(project_dir)}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder_name, subfolders, filenames in os.walk(project_dir):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                arcname = os.path.relpath(file_path, project_dir)
                zipf.write(file_path, arcname)
    return zip_filename

def download_project_zip():
    project_dir = get_latest_project_folder()

    zip_filename = zip_project_folder(project_dir)

    print(f"✅ Project zip file created: {zip_filename}")

if __name__ == "__main__":
    download_project_zip()


