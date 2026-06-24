class RiskScoringEngine:

    def calculate_score(self, hash_valid, signature_valid, watermark_valid,
                         ai_probability):

        score = 100

        if not hash_valid:
            score -= 40
        if not signature_valid:
            score -= 35
        if not watermark_valid:
            score -= 10

        score -= int(ai_probability * 0.15)

        return max(score, 0)

    def classify_risk(self, score):
        if score >= 90:
            return "TRUSTED"
        elif score >= 70:
            return "LOW RISK"
        elif score >= 50:
            return "MEDIUM RISK"
        elif score >= 30:
            return "HIGH RISK"
        else:
            return "CRITICAL RISK"
