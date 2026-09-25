"""
Prospectus Document Evaluation Benchmark Test Suite
===================================================
Tests detection across all required PII entity types on prospectus document logs.
Calculates Precision, Recall, F1-Score, and Accuracy.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine import PIIRedactor

def test_pii_detection_accuracy():
    redactor = PIIRedactor(seed=42)

    test_cases = [
        # PAN Cards
        ("PAN Card: NBWPS1951N issued to Vishal Singh", ["NBWPS1951N", "Vishal Singh"]),
        ("Tax Registration PAN: ABCDE1234F", ["ABCDE1234F"]),

        # Email Addresses
        ("Contact lead manager at info@icicisecurities.com or support@axiscap.in", ["info@icicisecurities.com", "support@axiscap.in"]),

        # Phone Numbers
        ("Call company secretary at +91 9876543210 or 022-22882200", ["91 9876543210", "022-22882200"]),

        # CIN & DIN Numbers
        ("Corporate Identification Number: U74999MH2018PTC312345", ["U74999MH2018PTC312345"]),
        ("Director Identification Number DIN: 08765432", ["08765432"]),

        # SSN Numbers
        ("US Citizen SSN 123-45-6789 verified", ["123-45-6789"]),

        # Aadhaar Numbers
        ("Aadhaar Card Number 2943 6593 3461 verified", ["2943 6593 3461"]),

        # Credit Cards
        ("Payment processed via card 4532-7512-8943-1102", ["4532-7512-8943-1102"]),

        # IP Addresses
        ("Access logged from IP 192.168.1.105 and 10.0.4.12", ["192.168.1.105", "10.0.4.12"]),

        # Company Names
        ("Offered by Acme Technologies Private Limited", ["Acme Technologies Private Limited"]),

        # Dates of Birth
        ("Born on 06/05/2000 in Mumbai", ["06/05/2000"]),

        # Physical Addresses
        ("Plot No. 341, Survey No. 997/8, Pune - 411 016.", ["Plot No. 341, Survey No. 997/8, Pune - 411 016."])
    ]

    total_expected = 0
    total_detected = 0
    true_positives = 0

    for text, expected in test_cases:
        total_expected += len(expected)
        redacted_text, entities = redactor.redact(text)
        detected_originals = [e['original'] for e in entities]
        total_detected += len(detected_originals)

        for exp in expected:
            if any(exp in orig or orig in exp for orig in detected_originals):
                true_positives += 1

    precision = (true_positives / total_detected) * 100 if total_detected > 0 else 0
    recall = (true_positives / total_expected) * 100 if total_expected > 0 else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
    accuracy = (true_positives / total_expected) * 100 if total_expected > 0 else 0

    print(f"\nEvaluation Benchmark Results:")
    print(f"Precision: {precision:.2f}% | Recall: {recall:.2f}% | F1: {f1:.2f}% | Accuracy: {accuracy:.2f}%")

    assert precision >= 95.0, f"Precision {precision:.2f}% is below target threshold of 95%"
    assert recall >= 95.0, f"Recall {recall:.2f}% is below target threshold of 95%"

if __name__ == '__main__':
    test_pii_detection_accuracy()
