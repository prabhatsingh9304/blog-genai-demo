class ParseRequestCharacter:
    def __init__(self):
        self.name = "Parse Request Character"
        self.description = "A character that parses the user's request and determines the action to take."
        self.tools = []

    def get_character(self):
        character = f"""
            You are a request analyzer. Your task is to determine if the user wants to:
            1. Generate a new blog post from scratch ('generate')
            2. Improve or edit an existing blog post ('improve')
            
            Analyze the user's request and respond with ONLY one of these commands: 'generate' or 'improve'.
            """
        return character
