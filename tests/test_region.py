import pytest

from src.region import Region


class TestRegion:
    def test_invalid_region_code_raises_error(self):
        with pytest.raises(Exception):
            Region(code="not a valid aws region code")

    def test_invalid_region_name_raises_error(self):
        with pytest.raises(Exception):
            Region(name="not a valid aws region name")

    def test_providing_code_and_name_raises_error(self):
        with pytest.raises(Exception):
            Region(name="foo", code="bar")

    def test_providing_neither_code_nor_name_raises_error(self):
        with pytest.raises(Exception):
            Region()

    def test_us_east_1_name_happy_path(self):
        reg = Region(name="us-east-1")
        assert reg.full_name == "US East (N. Virginia)"
        assert reg.code == "use1"
