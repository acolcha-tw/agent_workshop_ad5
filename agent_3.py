import os
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.settings import ModelSettings

REPO_PATH = os.path.abspath("./my-git-repo")

# ── 1. BaseModel — structured output the agent must return ───────────────────
class ChangelogResult(BaseModel):
    version: str
    summary: str
    markdown_content: str

# ── 2. Dynamic Context: typed dependency container (deps_type) ────────────────
@dataclass
class RAGDeps:
    repo_path: str
    changelog_file: str
    style_guide_file: str
    author: str

gemini_brain = GoogleModel('gemini-2.5-flash')

my_agent = Agent(
    model=gemini_brain,
    deps_type=RAGDeps,
    output_type=ChangelogResult,
    model_settings={'temperature': 0.4},
    # TODO: 1. Define the deps_type to be AppDeps for RunContext injection
    #  2. Define the output_type to be ChangelogResult for structured output
    #  3. Define the model_settings to configure the temperature for deterministic output
    system_prompt=(
        "You are a strict release documentation compliance officer. "
        "To produce a changelog entry you MUST follow this sequence:\n"
        "1. Call retrieve_style_guide to fetch the corporate layout template.\n"
        "2. Format the user's raw commits against that template.\n"
        "3. Call save_changelog with the final markdown to persist it."
    ),
    instructions=(
       "You are an expert technical writer and release documentation compliance officer. "
        "When given developer notes, generate a polished changelog entry that adheres strictly "
        "to the style guide provided in your instructions, then save it using the save_changelog tool."
    ),
)

# ── Tool 1: RAG retrieve — uses RunContext to get style_guide_file path ───────
@my_agent.tool
def retrieve_style_guide(ctx: RunContext[RAGDeps]) -> str:
    """Fetches the corporate changelog style guide from the knowledge base."""
    if not os.path.exists(ctx.deps.style_guide_file):
        raise FileNotFoundError(f"Could not find the compliance file at {ctx.deps.style_guide_file}")
    
    content = ""  

    #TODO: 6. Return the content of the style guide file using the injected deps
    with open(ctx.deps.style_guide_file, "r", encoding="utf-8") as f:
        content= f.read()

    return content

# ── Tool 2: Persist — uses RunContext to get repo_path and author ─────────────
@my_agent.tool
def save_changelog(ctx: RunContext[RAGDeps], content: str) -> str:
    """Saves the formatted changelog content to disk."""
    os.makedirs(ctx.deps.repo_path, exist_ok=True)
    #TODO: 7. Use the injected deps to write the content to the changelog file
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    changelog_entry = (
        f" Update from {ctx.deps.author}- {timestamp}\n"
        f"- : {content} \n\n"
    )

    with open(ctx.deps.changelog_file, "a", encoding="utf-8") as f:
            f.write(changelog_entry)
            
    return f"Changelog saved successfully by {ctx.deps.author}."

def init_workspace():
    os.makedirs(REPO_PATH, exist_ok=True)

async def run_agent_workflow(user_raw_commits: str) -> str:
    init_workspace()

    changelog_file_path = os.path.join(REPO_PATH, "CHANGELOG.md")
    style_guide_file_path = os.path.abspath("./style_guide.txt")

    #TODO: 5. Create an instance of Deps with the appropriate values for repo_path, changelog_file, style_guide_file and author
    deps = RAGDeps(REPO_PATH, changelog_file_path, style_guide_file_path, "Ale+Mariama" )

    # result.output is a validated ChangelogResult instance
    result = await my_agent.run(
        f"Format these raw developer commits into a compliant changelog entry:\n"
        f"{user_raw_commits}",
        deps=deps,
    )

    print(f"Version : {result.output.version}")
    print(f"Summary : {result.output.summary}")

    #TODO: 6. Return the content to be saved to the changelog file using the save_changelog tool
    return result.output.summary

