class KeywordsCharacter:
    def __init__(self, topic, top_related_topics):
        self.topic = topic
        self.top_related_topics = top_related_topics
    
    def get_character(self):
        character = f"""            
            From these trending topics: {', '.join(self.top_related_topics)},  
            Select the **most relevant and engaging** one for a blog on "{self.topic}".  
            Return only the topic name—no explanations.  
        """
        return character
