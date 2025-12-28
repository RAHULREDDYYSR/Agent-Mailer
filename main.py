import subprocess
import time
import os
import sys

def main():
    """
    Starts both the backend (Uvicorn) and frontend (Streamlit) services.
    """
    print("Starting Agent Mailer Services...")
    
    backend_process = None
    frontend_process = None

    try:
        # Start Backend
        print("Launching Backend...")
        backend_process = subprocess.Popen(
            ["uv", "run", "uvicorn", "backend.main:app", "--reload", "--port", "8000"],
            env=os.environ.copy()
        )
        
        # Wait a moment for backend to initialize
        time.sleep(2)

        # Start Frontend
        print("Launching Frontend...")
        frontend_process = subprocess.Popen(
            ["uv", "run", "streamlit", "run", "frontend/app.py", "--server.port", "8501"],
            env=os.environ.copy()
        )

        print("\nServices are running!")
        print("Backend: http://localhost:8000")
        print("Frontend: http://localhost:8501")
        print("Press Ctrl+C to stop.\n")

        # Wait for both processes to complete (or be interrupted)
        backend_process.wait()
        frontend_process.wait()

    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        # Ensure processes are terminated
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate() 
        sys.exit(0)

if __name__ == "__main__":
    main()
