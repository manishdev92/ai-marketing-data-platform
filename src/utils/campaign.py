def assign_campaign(intent: str) -> str:
    mapping = {
        "recommendation_intent": "campaign_reco_1",
        "purchase_intent": "campaign_buy_1",
        "support_intent": "campaign_support_1",
        "general_intent": "campaign_general_1",
    }
    return mapping.get(intent, "campaign_general_1")
