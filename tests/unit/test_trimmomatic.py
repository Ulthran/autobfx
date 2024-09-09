from tasks.trimmomatic import trimmomatic


def test_trimmomatic():
    assert trimmomatic.fn() == "trimmomatic"
