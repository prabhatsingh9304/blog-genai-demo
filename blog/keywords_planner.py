from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


class GoogleAdsKeywordGenerator:
    DEFAULT_LOCATION_IDS = ["1023191"]  # New York, NY
    DEFAULT_LANGUAGE_ID = "1000"  # English

    def __init__(self, config_path: str):
        self.client = GoogleAdsClient.load_from_storage(config_path)
        self.service = self.client.get_service("KeywordPlanIdeaService")
        self.keyword_plan_network = self.client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS

    def _map_location_ids_to_resource_names(self, location_ids):
        return [
            self.client.get_service("GeoTargetConstantService").geo_target_constant_path(location_id)
            for location_id in location_ids
        ]

    def _get_language_resource_name(self, language_id):
        return self.client.get_service("GoogleAdsService").language_constant_path(language_id)

    def generate_keywords(self, customer_id, keyword_texts=None, page_url=None,
                          location_ids=None, language_id=None):
        if not (keyword_texts or page_url):
            raise ValueError("You must provide at least one of keyword_texts or page_url.")

        location_ids = location_ids or self.DEFAULT_LOCATION_IDS
        language_id = language_id or self.DEFAULT_LANGUAGE_ID

        location_rns = self._map_location_ids_to_resource_names(location_ids)
        language_rn = self._get_language_resource_name(language_id)

        request = self.client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = customer_id
        request.language = language_rn
        request.geo_target_constants = location_rns
        request.include_adult_keywords = False
        request.keyword_plan_network = self.keyword_plan_network

        if keyword_texts and page_url:
            request.keyword_and_url_seed.url = page_url
            request.keyword_and_url_seed.keywords.extend(keyword_texts)
        elif keyword_texts:
            request.keyword_seed.keywords.extend(keyword_texts)
        elif page_url:
            request.url_seed.url = page_url

        results = []
        response = self.service.generate_keyword_ideas(request=request)
        for idea in response:
            results.append({
                "text": idea.text,
                "avg_monthly_searches": idea.keyword_idea_metrics.avg_monthly_searches,
                "competition": idea.keyword_idea_metrics.competition.name,
            })
        return results


# Example usage
if __name__ == "__main__":
    client_path = "/home/hash/google-ads.yaml"
    customer_id = "4077356448"
    keywords = ["coffee", "best coffee beans"]
    page_url = "https://example.com"

    generator = GoogleAdsKeywordGenerator(client_path)
    try:
        keyword_ideas = generator.generate_keywords(
            customer_id=customer_id,
            keyword_texts=keywords,
            # page_url=page_url
        )
        for idea in keyword_ideas:
            print(f'Keyword: "{idea["text"]}", Monthly Searches: {idea["avg_monthly_searches"]}, Competition: {idea["competition"]}')
    except GoogleAdsException as ex:
        print(f"Request failed with error: {ex}")
