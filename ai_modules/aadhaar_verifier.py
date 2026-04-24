from .groq_client import GroqClient

class AadhaarVerifier:
    """AI Module to verify Aadhaar names using Vision LLM."""
    
    def __init__(self):
        self.client = GroqClient()

    def verify(self, image_path, expected_name):
        """
        Extracts name from Aadhaar image and compares it with expected name.
        """
        prompt = (
            f"This is an Aadhaar card image. Please identify the full name of the person on the card. "
            f"Return ONLY the full name in English. Do not include any other text. "
            f"If you cannot find a name, return 'Unknown'."
        )
        
        result = self.client.generate_content(prompt, image_path=image_path)
        extracted_name = result.strip()
        
        if not extracted_name or extracted_name.lower() == 'unknown':
            return {
                'success': False,
                'extracted_name': 'Unknown',
                'expected_name': expected_name,
                'message': "Could not read a name from the card."
            }

        # Clean up expected and extracted names for better matching
        clean_extracted = "".join(e for e in extracted_name if e.isalnum()).lower()
        clean_expected = "".join(e for e in expected_name if e.isalnum()).lower()
        
        # Simple matching: check if expected name is contained in the extracted name
        is_match = clean_expected in clean_extracted or clean_extracted in clean_expected
        
        # Guard against hallucination (names aren't usually 100+ chars)
        if len(extracted_name) > 60:
            is_match = False

        return {
            'success': is_match,
            'extracted_name': extracted_name,
            'expected_name': expected_name
        }
