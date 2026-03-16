"""
AgroAid – Forward-Chaining Inference Engine
Given a set of selected symptom IDs for a specific crop,
return ranked disease diagnoses with confidence scores.
"""
from database import get_rules_for_crop, get_disease, get_treatments_for_disease


def diagnose(crop_id: int, selected_symptom_ids: list[int]) -> list[dict]:
    """
    Run forward-chaining inference.

    For every rule associated with the given crop:
      - Count how many of the rule's required symptoms appear in selected_symptom_ids
      - Compute: match_ratio  = matched / total_required
      - Compute: raw_confidence = match_ratio * rule.confidence_score
      - Only return results where at least 1 symptom matches

    Returns a list of dicts sorted by raw_confidence (descending):
        {
            'disease_id':     int,
            'disease_name':   str,
            'description':    str,
            'severity':       str,
            'confidence':     float (0-100),
            'matched':        int,
            'total_required': int,
            'treatments':     list[dict]
        }
    """
    selected_set = set(selected_symptom_ids)
    rules = get_rules_for_crop(crop_id)

    seen_diseases = {}  # disease_id -> best result dict

    for rule in rules:
        required = set(rule['symptom_ids'])
        if not required:
            continue

        matched = len(selected_set & required)
        if matched == 0:
            continue

        match_ratio = matched / len(required)
        # Bonus: if ALL symptoms matched  
        completeness_bonus = 0.1 if matched == len(required) else 0.0
        raw_confidence = min((match_ratio + completeness_bonus) * rule['confidence_score'], 1.0)

        disease_id = rule['disease_id']

        if disease_id not in seen_diseases or raw_confidence > seen_diseases[disease_id]['_raw']:
            disease = get_disease(disease_id)
            treatments = get_treatments_for_disease(disease_id)

            seen_diseases[disease_id] = {
                'disease_id':     disease_id,
                'disease_name':   disease['name'],
                'description':    disease['description'],
                'severity':       disease['severity'],
                'confidence':     round(raw_confidence * 100, 1),
                'matched':        matched,
                'total_required': len(required),
                'treatments':     [dict(t) for t in treatments],
                '_raw':           raw_confidence
            }

    results = sorted(seen_diseases.values(), key=lambda x: x['_raw'], reverse=True)
    for r in results:
        del r['_raw']
    return results
