import argparse


def main(argv):
    """CLI for autobfx's AI helper"""
    parser = argparse.ArgumentParser(description="AI helper")
    parser.add_argument("--project_fp", type=str, help="Filepath to the project")
    parser.add_argument("prompt", type=str, help="Question you want to ask autobfx")
    args = parser.parse_args(argv)

    return args
