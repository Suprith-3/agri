import json
from ai_modules.groq_client import GroqClient

class SchemeFinder:
    """Specialized AI for finding real-world agricultural schemes."""
    
    def __init__(self):
        self.client = GroqClient()

    def get_recommendations(self, user_state="Karnataka", user_district="Unknown"):
        prompt = f"""
        Act as a highly accurate government agricultural consultant in India. 
        Identify the latest 5 active government schemes (Centrally sponsored or State-specific for {user_state}) 
        that would benefit a farmer in {user_district}.
        
        CRITICAL: Provide ONLY real, working, official government website links for the application process. 
        Avoid generic homepage links if a direct registration link is available.
        
        Examples of correct links:
        - PM-KISAN: https://pmkisan.gov.in/RegistrationFormnew.aspx
        - PMFBY: https://pmfby.gov.in/farmer/registration
        - KCC: https://eseva.csccloud.in/KCC/default.aspx
        
        For each scheme, provide:
        1. Name (Official Name)
        2. Brief description (2 sentences)
        3. Key benefit (e.g., ₹20,000 subsidy)
        4. The real official website link for application (verified .gov.in or .nic.in domains preferred)
        
        Return the result as a JSON array of objects with keys: name, description, benefit, link.
        Do not include any other text before or after the JSON.
        """
        
        system_msg = "You are a helpful assistant that provides agricultural scheme data in pure JSON format."
        
        try:
            response = self.client.generate_content(prompt, system_instruction=system_msg)
            # Find JSON block if AI adds extra text
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                return json.loads(json_str)
            return []
        except Exception as e:
            print(f"[SchemeFinder Error] {e}")
            return []
