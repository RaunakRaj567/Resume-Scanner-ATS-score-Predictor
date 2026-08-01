import subprocess
import sys
import time
import os

def main():
    print("🚀 Starting Resume Scanner & ATS Predictor...")
    print("--------------------------------------------------")
    print("1. Launching FastAPI Backend on http://localhost:8000 ...")
    
    python_exe = sys.executable
    
    backend_process = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"]
    )
    
    # Give backend a moment to initialize
    time.sleep(2)
    
    print("2. Launching Streamlit Frontend Dashboard ...")
    frontend_process = subprocess.Popen(
        [python_exe, "-m", "streamlit", "run", "web/streamlit_app.py"]
    )
    
    print("--------------------------------------------------")
    print("App is running! Press Ctrl+C in this terminal to stop both servers.")
    print("--------------------------------------------------")

    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n Shutting down services...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("Done.")

if __name__ == "__main__":
    main()
