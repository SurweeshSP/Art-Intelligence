from .models import Opportunity

def check_eligibility(opp: Opportunity, profile: dict) -> bool:
    if opp.financial.application_fee > profile.get("max_application_fee_inr", 0):
        return False
    return True
