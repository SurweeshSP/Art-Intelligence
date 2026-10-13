from .models import Opportunity

def validate_opportunity(opp: Opportunity) -> Opportunity:
    if opp.deadline_date:
        opp.verification = "LIKELY"
    return opp
