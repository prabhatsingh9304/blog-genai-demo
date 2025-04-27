class TopicCharacter:
    def __init__(self, user_input):
        self.user_input = user_input
    
    def get_character(self):
        character = f"""
            Extract the main blog topic from the following user input:  
            "{self.user_input}"  
            Ensure the extracted topic is concise, relevant, and properly formatted for a blog title.  
            Return only the topic name—no explanations.  
        """
        return character

