import asyncio
import os
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.settings import ModelSettings

REPO_PATH = os.path.abspath("./my-git-repo")
CHANGELOG_FILE = os.path.join(REPO_PATH, "CHANGELOG.md")

# ── 1. BaseModel — structured output the agent must return ───────────────────
class ChangelogResult(BaseModel):
    version: str
    summary: str
    markdown_content: str

# ── 2. RunContext — typed dependency container ────────────────────────────────
@dataclass
class AppDeps:
    repo_path: str
    changelog_file: str
    author: str

# Instantiate the Gemini Brain
gemini_brain = GoogleModel('gemini-2.5-flash')

my_agent = Agent(
    model=gemini_brain,
    deps_type=AppDeps,
    output_type=ChangelogResult,
    model_settings={'temperature': 0.0},
    # TODO: 1. Define the deps_type to be AppDeps for RunContext injection
    #  2. Define the output_type to be ChangelogResult for structured output
    #  3. Define the model_settings to configure the temperature for deterministic output
    system_prompt=(
        "You are an expert technical writer. "
        "When given developer notes, generate a polished changelog entry "
        "and use the save_changelog tool to persist it to disk."
    )
)


# ── Tool: uses RunContext to access injected deps ─────────────────────────────
@my_agent.tool
def save_changelog(ctx: RunContext[AppDeps], content: str) -> str:
    """Saves the formatted changelog content to disk using injected deps."""
    os.makedirs(ctx.deps.repo_path, exist_ok=True)

    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    changelog_entry = (
        f" Update from {ctx.deps.author}- {timestamp}\n"
        f"- : {content} \n\n"
    )

   #TODO: 4. Use the injected deps to write the content to the changelog file
    with open(ctx.deps.changelog_file, "a", encoding="utf-8") as f:
        f.write(changelog_entry)

    return f"Saved successfully to {ctx.deps.changelog_file} by {ctx.deps.author}"

def init_workspace():
    os.makedirs(REPO_PATH, exist_ok=True)

async def run_agent_workflow(user_instruction: str) -> ChangelogResult:
    init_workspace()

    #TODO: 5. Create an instance of AppDeps with the appropriate values for repo_path, changelog_file, and author
    deps = AppDeps(repo_path=REPO_PATH, changelog_file=CHANGELOG_FILE, author="Alejandra+Mariama")

    # result.output is a validated ChangelogResult instance
    result = await my_agent.run(user_instruction, deps=deps)

    print(f"Version : {result.output.version}")
    print(f"Summary : {result.output.summary}")

    #TODO: 6. Return the content to be saved to the changelog file using the save_changelog tool
    return result.output.summary
