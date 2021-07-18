# PVSS - FS
Secret file sharing application based on Pedersen's Verified Sercet Sharing algorithm

# Requirements

- Python 3.7 (it is recommended to use virtualenv or conda to install environment)

- C++ Compiler (g++)

# Setup

- Step 0: Clone this repository

- Step 1: Compile C++ files into .so objects. We use ctypes to improve performance of these algorithms

- Step 2: Install requirements.txt

- Step 3: Export $PYTHONPATH to src folder destination on your machine

# Usage

- If you are a server: run services.py

- If you are a client: run client_app.py
