class HelperPromptCharacter:
    def __init__(self):
        pass
        
    def get_character(self):
        character = """
        # Blog Generation and Improvement Assistant

        I can help you with two main tasks:

        ## 1. Generate a new blog
        To generate a blog, simply let me know what topic you'd like to write about. You can also specify:
        - Tone (e.g., Professional, Conversational, Helpful & Value-Driven)
        - Target audience (e.g., Beginners, Experts, General audience)

        Example: "Generate a blog about artificial intelligence trends for beginners with a conversational tone."

        ## 2. Improve an existing blog
        
        Examples of improvement requests:
        - "Improve the blog more SEO-friendly by adding more keywords related to [topic]"
        - "Simplify the language to make it easier for beginners to understand"
        - "Add more practical examples in the second section"
        - "Make the introduction more engaging"
        
        """
        return character 