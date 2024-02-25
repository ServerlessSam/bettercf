from bettercf.account import Account


class TestAccount:
    def test_account_init_happy_path(self):
        acc = Account(1, "foo")
        assert (acc.id, acc.name) == (1, "foo")
