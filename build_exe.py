import subprocess
import os

def build_exe():
    print("🔨 Building WebMiner.exe...")
    
    # Check if icon exists
    icon_flag = ""
    if os.path.exists("icon.ico"):
        icon_flag = "--icon=icon.ico"
        print("✅ Icon found: icon.ico")
    else:
        print("⚠️  No icon.ico found - building without icon")
    
    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=WebMiner",
        "--clean",
        "--noconfirm",
        "due_amount_scraper_gui.py"
    ]
    
    # Add icon if available
    if icon_flag:
        cmd.append(icon_flag)
    
    # Add hidden imports
    cmd.extend([
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=selenium",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=concurrent.futures"
    ])
    
    print(f"🚀 Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        print("📁 Executable location: dist/WebMiner.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

if __name__ == "__main__":
    build_exe()
