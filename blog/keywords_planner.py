import sys
from typing import List, Optional
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

class KeywordPlanner:
    def __init__(self, customer_id: str, config_path: Optional[str] = None):
        self.customer_id = customer_id
        self.client = GoogleAdsClient.load_from_storage(config_path) if config_path else GoogleAdsClient.load_from_storage()
        self.keyword_plan_idea_service = self.client.get_service("KeywordPlanIdeaService")

    def _map_location_ids_to_resource_names(self, location_ids: List[str]) -> List[str]:
        geo_target_constant_service = self.client.get_service("GeoTargetConstantService")
        return [geo_target_constant_service.geo_target_constant_path(location_id) for location_id in location_ids]

    def generate_keyword_ideas(
        self,
        keyword_texts: Optional[List[str]] = None,
        page_url: Optional[str] = None,
        location_ids: Optional[List[str]] = None,
        language_id: str = "1000",  # Default to English
        include_adult_keywords: bool = False,
    ) -> List[dict]:
        try:
            if not keyword_texts and not page_url:
                raise ValueError("At least one of keyword_texts or page_url must be provided.")

            location_ids = location_ids or ["1023191"]  # Default to New York, NY
            location_rns = self._map_location_ids_to_resource_names(location_ids)
            language_rn = self.client.get_service("LanguageConstantService").language_constant_path(language_id)

            request = self.client.get_type("GenerateKeywordIdeasRequest")
            request.customer_id = self.customer_id
            request.language = language_rn
            request.geo_target_constants.extend(location_rns)
            request.include_adult_keywords = include_adult_keywords
            request.keyword_plan_network = self.client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS

            if keyword_texts and page_url:
                request.keyword_and_url_seed.url = page_url
                request.keyword_and_url_seed.keywords.extend(keyword_texts)
            elif keyword_texts:
                request.keyword_seed.keywords.extend(keyword_texts)
            elif page_url:
                request.url_seed.url = page_url

            response = self.keyword_plan_idea_service.generate_keyword_ideas(request=request)

            results = []
            for idea in response:
                metrics = idea.keyword_idea_metrics
                results.append({
                    "keyword": idea.text,
                    "avg_monthly_searches": metrics.avg_monthly_searches,
                    "competition": metrics.competition.name,
                    "low_top_of_page_bid_micros": metrics.low_top_of_page_bid_micros,
                    "high_top_of_page_bid_micros": metrics.high_top_of_page_bid_micros,
                })
            return results

        except GoogleAdsException as ex:
            print(f"Request failed with status '{ex.error.code().name}' and includes the following errors:")
            for error in ex.failure.errors:
                print(f"\tError with message '{error.message}'.")
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        print(f"\t\tOn field: {field_path_element.field_name}")
            sys.exit(1)

if __name__ == "__main__":
    planner = KeywordPlanner(customer_id="INSERT_CUSTOMER_ID_HERE")
    keyword_ideas = planner.generate_keyword_ideas(
        keyword_texts=["digital marketing", "seo"],
        location_ids=["1023191"],  # New York, NY
        language_id="1000",        # English
    )
    for idea in keyword_ideas:
        print(idea)
