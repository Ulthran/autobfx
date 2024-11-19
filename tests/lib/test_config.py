from src.autobfx.lib.config import Config, FlowConfig


def test_config():
    config = Config(
        version="0.0.0",
        name="test",
        project_fp="test_project_fp",
    )


def test_flow_config():
    flow_config = FlowConfig(
        input="test_input",
        output="test_output",
    )
