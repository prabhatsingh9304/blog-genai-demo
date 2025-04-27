class BlogCharacter:
    def __init__(self, topic, blogs_urls, keywords, tone, target_audience, rag_content, memory_context=""):
        self.topic = topic
        self.blogs_urls = blogs_urls
        self.keywords = keywords
        self.tone = tone
        self.target_audience = target_audience
        self.rag_content = rag_content
        self.memory_context = memory_context
        
    def get_character(self):
        character = f"""
        Write an SEO-optimized blog post on topic: **{self.topic}**. 
        
        **Constraints**:
        - The blog content should have word count around 2000-2500 words
        - The content should be detailed, structured with headings (H2, H3), and optimized for search engines. 
        - Maintain a {self.tone} tone suitable for {self.target_audience}. 
        - Ensure that the following keywords are naturally incorporated: {self.keywords}. 
        - Reduce frequency of this keyword. Enrich your text with secondary or long-tail keywords, and synonyms.
        - Ensure proper formatting, readability, and keyword distribution without stuffing. 
        - Use engaging introductions, clear explanations, bullet points, and actionable takeaways. 
        - Conclude with a compelling Call to Action: '[CTA]'.
        - Add meta description (150-160 characters) summarizing the article.
        - Consider using active voice instead of passive voice.
        - Don't write hard to read content, write in a way that is easy to read and understand.
        - Add blog links: {self.blogs_urls} as reference to make it more authoritative and useful to readers.
        - Write blog first and add additional requirements later.
        - Use the following RAG content to improve the blog post: {self.rag_content}
        
        Additional requirements:
        - Provide a meta tags for SEO optimization in new line.
        - Provide a alt text for the banner image in new line, use the keyword in alt text.
        - Provide a name for the banner image in new line, use the keyword in name.
        - Provide a url alias for the blog in new line, use the keyword in url alias.
        

        {self.memory_context if self.memory_context else ""}
        """
        return character