def test_deliberate_failure_for_ci_gatekeeping():
    """Deliberate failure to demonstrate CI blocks merge on failing tests."""
    assert False, "Deliberate test failure for CPE434 CI gatekeeping demonstration"
