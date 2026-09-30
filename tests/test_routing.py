import unittest

from backend.engine.multimodal_network import create_multimodal_network
from backend.engine.route_recommender import RouteRecommender
from backend.engine.scenario_manager import ScenarioManager
from backend.engine.threat_intelligence import CARFFilter, ThreatIntelligencePredictor


class RoutingDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.router = RouteRecommender(
            create_multimodal_network(), ThreatIntelligencePredictor(), None,
            ScenarioManager(), demo_mode=True,
        )

    def test_carf_keeps_relevant_and_rejects_irrelevant_modal_news(self):
        carf = CARFFilter()
        self.assertEqual(carf.apply_filter(0.8, "Canal vessel delayed at port", "sea"), 0.8)
        self.assertEqual(carf.apply_filter(0.8, "Airport flight disruption", "sea"), 0.0)
        self.assertEqual(carf.apply_filter(0.8, "Truck traffic on highway", "road"), 0.8)

    def test_suez_scenario_changes_the_sea_route_decision(self):
        normal = self.router.recommend("Shanghai", "Rotterdam")
        disrupted = self.router.recommend("Shanghai", "Rotterdam", scenario="SUEZ_BLOCK")
        normal_balanced = next(item for item in normal["recommendations"] if item["persona"] == "BALANCED")
        disrupted_balanced = next(item for item in disrupted["recommendations"] if item["persona"] == "BALANCED")
        self.assertIn("CHOKE-SUEZ", [leg["to"] for leg in normal_balanced["legs"]])
        self.assertNotIn("CHOKE-SUEZ", [leg["to"] for leg in disrupted_balanced["legs"]])
        self.assertGreater(disrupted_balanced["adjusted_eta"], normal_balanced["adjusted_eta"])
        self.assertGreater(disrupted_balanced["confidence_band"]["p85_hours"], disrupted_balanced["adjusted_eta"])


if __name__ == "__main__":
    unittest.main()
