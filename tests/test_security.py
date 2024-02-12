import unittest
from security import get_password_hash, verify_password


class TestSecurity(unittest.TestCase):

    def test_get_password_hash(self):
        """Test password hashing."""
        password = "secret"
        hash = get_password_hash(password)
        self.assertNotEqual(password, hash)

    def test_verify_password(self):
        """Test password verification."""
        password = "secret"
        wrong_password = "wrongsecret"
        hash = get_password_hash(password)
        self.assertTrue(verify_password(password, hash))
        self.assertFalse(verify_password(wrong_password, hash))


if __name__ == '__main__':
    unittest.main()
