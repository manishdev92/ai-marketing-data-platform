def detect_intent(text: str) -> str:
    t = text.lower()

    if any(k in t for k in ["buy", "purchase", "order"]):
        return "purchase_intent"

    if any(k in t for k in ["recommend", "suggest"]):
        return "recommendation_intent"

    if any(k in t for k in ["refund", "return"]):
        return "support_intent"

    return "general_intent"
