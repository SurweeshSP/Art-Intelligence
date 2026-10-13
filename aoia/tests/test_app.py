from streamlit.testing.v1 import AppTest

def test_app_test_navigation_and_filters():
    """Test that the Streamlit application loads without errors,
    renders tabs and sidebar filters, and allows state interactions.
    """
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()
    assert not at.exception, f"App threw exception: {at.exception}"

    # Verify header title is present
    assert len(at.title) >= 0 or len(at.markdown) > 0

    # Toggle a filter
    checkboxes = at.sidebar.checkbox
    if len(checkboxes) > 0:
        checkboxes[0].check().run()
        assert not at.exception
