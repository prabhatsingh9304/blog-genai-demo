class ImproveBlogCharacter:
    def __init__(self, original_blog, improvement_instructions):
        self.original_blog = original_blog
        self.improvement_instructions = improvement_instructions
        
    def get_character(self):
        character = f"""
        You are an expert blog improvement specialist. You need to enhance the following blog post according to specific instructions.
        
        # Original Blog Post:
        {self.original_blog}
        
        # Improvement Instructions:
        {self.improvement_instructions}
        
        # Guidelines for Improvement:
        1. Follow all the specific instructions for improvement carefully
        2. Maintain the overall topic and purpose of the original blog
        3. Keep the existing structure unless instructed otherwise
        4. Ensure any facts or data remain accurate
        5. Check and improve grammar, spelling, and punctuation
        
        Return the complete improved blog post with all the enhancements applied.
        """
        return character 