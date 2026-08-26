# agent_1.py
import os
from datetime import datetime

# Align this path with what the Streamlit File Inspector is searching for
REPO_PATH = os.path.abspath("./my-git-repo")
CHANGELOG_FILE = os.path.join(REPO_PATH, "CHANGELOG.md")

def init_workspace():
    """Initializes the exact repository path expected by the lab dashboard."""
    os.makedirs(REPO_PATH, exist_ok=True)

async def run_agent_workflow(user_instruction: str) -> str:
    """Rigidly writes the raw Streamlit text directly to disk without an AI."""
    init_workspace()

    return f"Status: {write_changelog(user_instruction)} " 

def write_changelog(user_instruction: str) -> str:

    if user_instruction.strip() is None or user_instruction.strip() == "":
        raise Exception("User instruction is empty")
        return

    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d")

    with open(CHANGELOG_FILE, 'a') as file:
        file.write( formatted_date + ' ' + user_instruction)
    
    return "Instruction added successfully!"