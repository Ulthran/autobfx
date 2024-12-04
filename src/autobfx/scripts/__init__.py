from pathlib import Path


# The dot directory under the project root holds all the info related to Prefect services
# Dot directories in each project dir are used to store Autobfx progress tracking info
DOT_FP = Path(__file__).parent.parent.parent.parent / ".autobfx"
DOT_FP.mkdir(exist_ok=True)
