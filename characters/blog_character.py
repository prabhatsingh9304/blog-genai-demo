class BlogCharacter:
    def __init__(self, topic, keywords, tone, target_audience, rag_content):
        self.topic = topic
        self.keywords = keywords
        self.tone = tone
        self.target_audience = target_audience
        self.rag_content = rag_content
        
    def get_character(self):
        character = f"""
        Write an SEO-optimized blog post on topic: **{self.topic}**. 
        
        Constraints:
        - Ensure that the following keywords are naturally incorporated: {self.keywords}. 
        - Maintain a {self.tone} tone suitable for {self.target_audience}. 
        - The content should be detailed, structured with headings (H2, H3), and optimized for search engines. 
        - Use engaging introductions, clear explanations, bullet points, and actionable takeaways. 
        - The word count should be around 1500-2000 words. Conclude with a compelling Call to Action: '[CTA]'.
        - Ensure proper formatting, readability, and keyword distribution without stuffing. 
        - Add meta description (150-160 characters) summarizing the article.
        - Don't use complex words, use simple words and easy to understand.
        - Consider using active voice instead of passive voice.
        - Don't write hard to read content, write in a way that is easy to read and understand.
        - Write blog first and add additional requirements later.
        
        Additional requirements:
        - Provide a meta tags for SEO optimization in new line.
        - Provide a alt text for the banner image in new line, use the keyword in alt text.
        - Provide a name for the banner image in new line, use the keyword in name.
        - Provide a url alias for the blog in new line, use the keyword in url alias.
        
        Use the following RAG content to improve the blog post: {self.rag_content}

        """
        return character