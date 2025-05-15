import py_compile
import sys
import os

def check_python_file(filepath):
    try:
        py_compile.compile(filepath, doraise=True)
        print(f"✅ File {filepath} compiles successfully.")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Compilation error in {filepath}:")
        print(f"   {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking {filepath}: {e}")
        return False

if __name__ == "__main__":
    # Check specific file
    plugin_path = r"c:\Users\David\Documents\GitHub\test1234"
    init_path = os.path.join(plugin_path, "__init__.py")
    
    check_python_file(init_path)
    
    # Optional: Check all Python files in plugin directory
    print("\nChecking all Python files in directory:")
    for filename in os.listdir(plugin_path):
        if filename.endswith(".py"):
            filepath = os.path.join(plugin_path, filename)
            check_python_file(filepath)
