from app.adapters.ashby_adapter import AshbyAdapter

def test_ashby_adapter_has_search_contract():
    adapter = AshbyAdapter()
    assert adapter.name == "Ashby"
    assert callable(adapter.search)
