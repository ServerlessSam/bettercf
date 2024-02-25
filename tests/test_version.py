import pytest

from bettercf.version import Version


class TestVersion:
    """
    Version Class Initialisation Tests
    """

    def test_init_with_bad_version(self):
        with pytest.raises(Exception):
            Version(version_string="not a valid version string")

    def test_init_with_micro_happy_path(self):
        ver = Version(version_string="1.2.3")
        assert (ver.major, ver.minor, ver.micro) == (1, 2, 3)

    def test_init_without_micro_happy_path(self):
        ver = Version(version_string="1.2")
        assert (ver.major, ver.minor) == (1, 2)
        with pytest.raises(AttributeError):
            ver.micro

    """
    major_minor(_micro)() Class Function Tests
    """

    def test_major_minor_micro_happy_path(self):
        assert Version.major_minor_micro("1.2.3") == (1, 2, 3)
        assert Version.major_minor_micro("0.0.0") == (0, 0, 0)

    def test_major_minor_micro_bad_verion_errors(self):
        for bad_version in [[1, 2, 3], "1.2", "1.2.3.4", "", None, "foo"]:
            with pytest.raises(Exception):
                Version.major_minor_micro(bad_version)

    def test_major_minor_bad_version_errors(self):
        for bad_version in [[1, 2], "1.2.3", "", None, "foo"]:
            with pytest.raises(Exception):
                Version.major_minor(bad_version)

    def test_major_minor_happy_path(self):
        assert Version.major_minor("1.2") == (1, 2)
        assert Version.major_minor("0.0") == (0, 0)

    """
    get_version_string() Class Function Tests
    """

    def test_get_version_string_no_micro_happy_path(self):
        ver = Version("1.2")
        assert ver.get_version_string() == "1.2"
        ver0 = Version("0.0")
        assert ver0.get_version_string() == "0.0"

    def test_get_version_string_with_micro_happy_path(self):
        ver = Version("1.2.3")
        assert ver.get_version_string() == "1.2.3"
        ver0 = Version("0.0.0")
        assert ver0.get_version_string() == "0.0.0"

    """
    major_version_increment() Class Function Tests
    """

    def test_major_version_increment_no_micro_happy_path(self):
        ver = Version("1.2")
        ver.major_version_increment()
        assert (ver.major, ver.minor) == (2, 0)

    def test_major_version_increment_with_micro_happy_path(self):
        ver = Version("1.2.3")
        ver.major_version_increment()
        assert (ver.major, ver.minor, ver.micro) == (2, 0, 0)

    """
    minor_version_increment() Class Function Tests
    """

    def test_minor_version_increment_no_micro_happy_path(self):
        ver = Version("1.2")
        ver.minor_version_increment()
        assert (ver.major, ver.minor) == (1, 3)

    def test_minor_version_increment_with_micro_happy_path(self):
        ver = Version("1.2.3")
        ver.minor_version_increment()
        assert (ver.major, ver.minor, ver.micro) == (1, 3, 0)

    """
    micro_version_increment() Class Function Tests
    """

    def test_micro_version_increment_with_micro_happy_path(self):
        ver = Version("1.2.3")
        ver.micro_version_increment()
        assert (ver.major, ver.minor, ver.micro) == (1, 2, 4)

    def test_micro_version_increment_no_micro_errors(self):
        ver = Version("1.2")
        with pytest.raises(Exception):
            ver.micro_version_increment()

    """
    auto_increment_version() Class Function Tests
    """

    def test_auto_increment_version_with_micro_happy_path(self):
        ver = Version("1.2.3")
        ver.auto_increment_version()
        assert (ver.major, ver.minor, ver.micro) == (1, 3, 0)
        ver.auto_increment_version(major_increment=True)
        assert (ver.major, ver.minor, ver.micro) == (2, 0, 0)
        ver.auto_increment_version(micro_increment=True)
        assert (ver.major, ver.minor, ver.micro) == (2, 0, 1)

    def test_auto_increment_version_no_micro_happy_path(self):
        ver = Version("1.2")
        ver.auto_increment_version()
        assert (ver.major, ver.minor) == (1, 3)
        ver.auto_increment_version(major_increment=True)
        assert (ver.major, ver.minor) == (2, 0)

    def test_auto_increment_version_no_micro_errors_when_micro_increment_is_true(self):
        ver = Version("1.2")
        with pytest.raises(Exception):
            ver.auto_increment_version(micro_increment=True)

    def test_auto_increment_version_errors_when_providing_both_increment_types(self):
        ver = Version("1.2")
        with pytest.raises(Exception):
            ver.auto_increment_version(True, True)
