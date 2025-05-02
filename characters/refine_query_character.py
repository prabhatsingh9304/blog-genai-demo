class RefineQueryCharacter:
    def __init__(self, topic):
        self.topic = topic
    
    def get_character(self):
        character = f"""
        Given the blog topic '{self.topic}', 
        generate a comprehensive similarity search query that would help find relevant content for writing a blog post from a rag system.
        Focus on finding authoritative sources, expert opinions, and practical examples that would be valuable for blog readers.
        Consider aspects like best practices, case studies, and current trends in the field.
        Return only the refined query, no explanations.
        """
        return character
