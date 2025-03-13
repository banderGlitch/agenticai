import os
import re

def update_imports_in_file(file_path):
    """Update imports in a file from langchain to langchain_core and langchain_community"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Update imports
    content = content.replace('from langchain.chains import', 'from langchain_core.chains import')
    content = content.replace('from langchain.prompts import', 'from langchain_core.prompts import')
    content = content.replace('from langchain.llms import', 'from langchain_community.llms import')
    content = content.replace('from langchain.chat_models import', 'from langchain_community.chat_models import')
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Updated imports in {file_path}")

def update_all_files():
    """Update imports in all Python files"""
    # Update agent files
    agents_dir = os.path.join('src', 'agents')
    if os.path.exists(agents_dir):
        for filename in os.listdir(agents_dir):
            if filename.endswith('.py'):
                file_path = os.path.join(agents_dir, filename)
                update_imports_in_file(file_path)
    
    # Update main.py
    if os.path.exists('main.py'):
        update_imports_in_file('main.py')
    
    # Update other Python files in src directory
    src_dir = 'src'
    if os.path.exists(src_dir):
        for root, dirs, files in os.walk(src_dir):
            for filename in files:
                if filename.endswith('.py'):
                    file_path = os.path.join(root, filename)
                    update_imports_in_file(file_path)

if __name__ == "__main__":
    update_all_files()
    print("All files updated successfully") 