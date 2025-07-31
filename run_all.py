import subprocess

# Start backend (FastAPI)
backend = subprocess.Popen(["uvicorn", "app:app", "--reload", "--port", "8000"], cwd="backend")

# Start frontend (Streamlit)
frontend = subprocess.Popen(["streamlit", "run", "dashboard.py"], cwd="frontend")

# Wait for both to finish
backend.wait()
frontend.wait()
