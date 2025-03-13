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

def update_all_agent_files():
    """Update imports in all agent files"""
    agents_dir = os.path.join('src', 'agents')
    
    if not os.path.exists(agents_dir):
        print(f"Directory {agents_dir} does not exist")
        return
    
    for filename in os.listdir(agents_dir):
        if filename.endswith('.py'):
            file_path = os.path.join(agents_dir, filename)
            update_imports_in_file(file_path)

if __name__ == "__main__":
    update_all_agent_files()
    print("All agent files updated successfully") 