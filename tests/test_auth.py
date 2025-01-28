import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))         # PYTHON IMPORT FIX
sys.path.append(parent_dir)                                                         #

import unittest
from unittest.mock import MagicMock, patch
from fastapi import Response, Request
from jwt import InvalidTokenError
from auth import *
from db.models import User

class TestJWTencoder(unittest.TestCase):

    def test_form_JWT_payload(self):
        body = {"userId": 1}
        payload = JWTencoder.form_JWT_payload(body, 5)
        self.assertIn("iss", payload)
        self.assertIn("exp", payload)
        self.assertIn("iat", payload)
        self.assertIn("userId", payload)
        self.assertEqual(payload["userId"], 1)

    def test_form_JWT_header(self):
        header = JWTencoder.form_JWT_header("HS256")
        self.assertEqual(header["alg"], "HS256")
        self.assertEqual(header["typ"], "JWT")

    def test_encode(self):
        body = {"userId": 1}
        token = JWTencoder.encode(body, 10, "HS256")
        self.assertIsInstance(token, str)

class TestJWTgenerator(unittest.TestCase):

    def test_generate_access_token(self):
        mock_settings = MagicMock()
        mock_settings.ACCS_TOK_LIFETIME_MIN = 15
        body = {"userId": 1}
        token = JWTgenerator.generate_access_token(body, mock_settings.ACCS_TOK_LIFETIME_MIN)
        self.assertIsInstance(token, str)

    def test_generate_tokens(self):
        mock_settings = MagicMock()
        mock_settings.ACCS_TOK_LIFETIME_MIN = 15
        mock_settings.REF_TOK_LIFETIME_DAYS = 1
        body = {"userId": 1}
        access_token, refresh_token = JWTgenerator.generate_tokens(body)
        self.assertIsInstance(access_token, str)
        self.assertIsInstance(refresh_token, str)

class TestJWTvalidator(unittest.TestCase):

    def test_check_valid_token(self):
        body = {"userId": 1}
        token = JWTencoder.encode(body, 10, "HS256")
        self.assertTrue(JWTvalidator.check(token))

    def test_check_invalid_token(self):
        self.assertFalse(JWTvalidator.check("invalid_token"))

class TestJWTdecoder(unittest.TestCase):

    def test_decode_valid_token(self):
        body = {"userId": 1}
        token = JWTencoder.encode(body, 10, "HS256")
        decoded = JWTdecoder.decode(token)
        self.assertEqual(decoded["userId"], 1)

    def test_decode_invalid_token(self):
        with self.assertRaises(InvalidTokenError):
            JWTdecoder.decode("invalid_token")

class TestTokenHandler(unittest.TestCase):

    def test_remove_tokens(self):
        response = Response()
        TokenHandler.remove_tokens(response)
        self.assertEqual(response.headers.get("access_token"), None)
        self.assertEqual(response.headers.get("refresh_token"), None)

    def test_get_user_bytoken(self):
        encoding_user = session.query(User).first()
        token = JWTencoder.encode({"userId": encoding_user.id}, 10)
        user = TokenHandler.get_user_bytoken(token)
        self.assertEqual(user.id, encoding_user.id)

class TestUserValidation(unittest.TestCase):

    @patch("auth.JWTvalidator")
    @patch("auth.TokenHandler.get_user_bytoken")
    def test_user_validation_valid(self, mock_get_user_bytoken, mock_validator):
        mock_validator.check.return_value = True
        mock_get_user_bytoken.return_value = MagicMock(id=1, is_admin=False)
        request = MagicMock(cookies={"access_token": "valid_token"})
        validation = UserValidation(request)
        self.assertTrue(validation.is_token_valid)
        self.assertEqual(validation.user.id, 1)

    def test_user_validation_no_token(self):
        request = MagicMock(cookies={})
        with self.assertRaises(UserValidation.NotAuthorized):
            UserValidation(request)

class TestAdminValidation(unittest.TestCase):

    @patch("auth.UserValidation")
    def test_admin_validation_valid(self, mock_user_validation):
        mock_user_validation.return_value.is_admin = True
        request = MagicMock()
        admin_validation = AdminValidation(request)
        self.assertTrue(mock_user_validation.called)



if __name__ == "__main__":
    unittest.main()
