import os
import glob

def fix_imports_in_file(file_path):
    """Fix imports in a file by changing langchain_core.chains to langchain.chains."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix the incorrect imports
    content = content.replace('from langchain_core.chains import', 'from langchain.chains import')
    
    # Also fix any imports related to Groq
    content = content.replace('from langchain.llms import Groq', 'from langchain_groq import ChatGroq')
    content = content.replace('from langchain.llms.groq import Groq', 'from langchain_groq import ChatGroq')
    content = content.replace('from langchain_core.llms import Groq', 'from langchain_groq import ChatGroq')
    content = content.replace('from langchain_community.llms import Groq', 'from langchain_groq import ChatGroq')
    content = content.replace('from langchain_community.llms.groq import Groq', 'from langchain_groq import ChatGroq')
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Fixed imports in {file_path}")

def fix_all_files():
    """Fix imports in all Python files in the project."""
    # Fix files in src/agents directory if it exists
    agents_dir = os.path.join('src', 'agents')
    if os.path.exists(agents_dir):
        for py_file in glob.glob(os.path.join(agents_dir, '*.py')):
            fix_imports_in_file(py_file)
    
    # Fix main.py if it exists
    main_py = os.path.join('src', 'main.py')
    if os.path.exists(main_py):
        fix_imports_in_file(main_py)
    
    # Fix config.py if it exists
    config_py = os.path.join('src', 'config.py')
    if os.path.exists(config_py):
        fix_imports_in_file(config_py)
    
    # Fix any Python files in the src directory
    if os.path.exists('src'):
        for py_file in glob.glob(os.path.join('src', '*.py')):
            fix_imports_in_file(py_file)
    
    # Fix app.py if it exists
    app_py = 'app.py'
    if os.path.exists(app_py):
        fix_imports_in_file(app_py)
    
    # Fix main.py in the root directory if it exists
    root_main_py = 'main.py'
    if os.path.exists(root_main_py):
        fix_imports_in_file(root_main_py)
    
    print("All imports fixed successfully!")

if __name__ == "__main__":
    fix_all_files() 