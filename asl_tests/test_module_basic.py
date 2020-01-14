import unittest


class TestModuleBasic(unittest.TestCase):
    def test_import(self):
        import asl  # noqa: F401


if __name__ == "__main__":
    unittest.main()
