import pytest
from municipal_performance_scraping.extractors import extract_performance_data
from municipal_performance_scraping.transformers import (
    all_numeric_keys,
    indent_keys,
    format_json,
)


@pytest.fixture()
def valid_performance():
    return extract_performance_data(1313, 2018)


@pytest.fixture()
def erroneous_performance():
    return extract_performance_data(13131313, 2018)


def test_all_numeric_keys_valid_performance(valid_performance):
    assert all_numeric_keys(valid_performance)
    assert not all_numeric_keys(valid_performance["10"])


def test_all_numeric_keys_erroneous_performance(erroneous_performance):
    assert all_numeric_keys(erroneous_performance)
    assert not all_numeric_keys(erroneous_performance["10"])


def test_indent_keys(valid_performance):
    assert isinstance(indent_keys(valid_performance), list)


def test_indent_keys_err_performance(erroneous_performance):
    assert isinstance(indent_keys(erroneous_performance), list)


def test_format_json(valid_performance):
    assert format_json(valid_performance)
