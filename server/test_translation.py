import unittest
import json
from app import app

class TranslationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_vi_en_translation(self):
        # Vietnamese text for testing
        vietnamese_text = "Xin chào, tôi là một sinh viên. Hôm nay trời đẹp."

        # Send POST request to /translate endpoint
        response = self.app.post(
            '/translate',
            data=json.dumps({"text": vietnamese_text}),
            content_type='application/json'
        )

        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, 200)

        # Parse the JSON response
        data = json.loads(response.data)

        # Ensure that a translated text key exists in the response
        self.assertIn("translated_text", data)
        translated_text = data["translated_text"]

        # As we cannot predict the exact translation, we check for English keywords.
        # This is a heuristic to see if the output is in English.
        self.assertTrue(
            any(word in translated_text for word in ["Hello", "student", "beautiful"]),
            "The translated text does not seem to be in English."
        )

if __name__ == '__main__':
    unittest.main()
