from typing import Callable, List, Optional
import re
from agents import Runner, Agent, RunConfig

notify: Optional[Callable] = None

prompt = """
Using python schedule, write a block of code that calls notify(arg: str). Assume you have access to the function `notify`, and the arg should signify what to do.
"""

raw_str = None
schedule_blocks = None
async def make_schedule(input):
    print("Making scheduler...")
    scheduler = Agent(
        name="Scheduler",
        instructions="""
        You are a helpful assistant writing correct python with perfect syntax. Just write the lines of code, no main() function, etc. Given the assignment, right the correct python code.

        """,
        model="o4-mini",
        run_config=RunConfig(
            seed=42,
            temperature=0
        )
        
    )
    print("Scheduler making schedule")
    result = await Runner.run(scheduler, prompt + input, max_turns=2)

    global raw_str
    raw_str = result.final_output

    global schedule_blocks
    schedule_blocks = extract_python_or_fallback(result.final_output)

    

def run_schedule():
    global notify

    print(f"Running schedule with notify={notify}")
    exec_globals = {
        "notify": notify,
    }
    global schedule_blocks
    
    if schedule_blocks is None:
        print("No schedule to run...")
    try:
        for code in schedule_blocks:
            print("RUNNING CODE:\n")
            print(code)
            exec(code, exec_globals)
    except Exception as e:
        print(f"Exception in schedule: {e}")

def extract_python_or_fallback(text: str) -> list[str]:
    blocks = extract_python_blocks(text)
    if blocks:
        return blocks
    # fallback: treat entire text as code
    return [text.strip()]

def extract_python_blocks(text: str) -> List[str]:
    """
    Extracts fenced ```python code blocks from a markdown-like string.
    Returns a list of code strings.
    """
    pattern = re.compile(
        r"```(?:python)?\s*\n(.*?)```",
        re.DOTALL | re.IGNORECASE
    )
    return [block.strip() for block in pattern.findall(text)]