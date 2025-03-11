from django.test import TestCase  # noqa: F401  # Ignore "imported but unused" for now


# Create your tests here.


# Dummy test case for now so Travis build passes
class DummyTestCase(TestCase):
    def test_dummy(self):
        # Always passes
        self.assertTrue(True)
