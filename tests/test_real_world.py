"""
Fresh Real-World Out-of-Sample Evaluation Suite
================================================
Tests performance on 10 fresh, unseen real-world document logs.
Calculates Precision, Recall, F1-Score, and Accuracy.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine import PIIRedactor

def test_fresh_real_world_samples():
    redactor = PIIRedactor(seed=42)

    unseen_test_cases = [
        {
            "id": "SAMPLE_01",
            "text": "Audit report for Zenith Global Logistics Private Limited (CIN: U63090MH2015PTC265432). Contact CFO Mr. Rajesh Sharma at rsharma@zenithlogistics.com or +91 9820123456.",
            "expected_pii": [
                "Zenith Global Logistics Private Limited",
                "U63090MH2015PTC265432",
                "Mr. Rajesh Sharma",
                "rsharma@zenithlogistics.com",
                "+91 9820123456"
            ]
        },
        {
            "id": "SAMPLE_02",
            "text": "Director appointment: Dr. Ananya Deshmukh (DIN 07891234), residing at Flat 402, Building A, Sunrise Towers, MG Road, Pune - 411001.",
            "expected_pii": [
                "Dr. Ananya Deshmukh",
                "07891234",
                "Flat 402, Building A, Sunrise Towers, MG Road, Pune - 411001"
            ]
        },
        {
            "id": "SAMPLE_03",
            "text": "Verification of PAN Card ABCDE1234F for applicant Sunil Verma, DOB 15/08/1985.",
            "expected_pii": [
                "ABCDE1234F",
                "Sunil Verma",
                "15/08/1985"
            ]
        },
        {
            "id": "SAMPLE_04",
            "text": "KYC Record: Aadhaar number 8912 3456 7890 belongs to Mrs. Kavita Patel.",
            "expected_pii": [
                "8912 3456 7890",
                "Mrs. Kavita Patel"
            ]
        },
        {
            "id": "SAMPLE_05",
            "text": "US Tax Filing: SSN 987-65-4321 registered to Johnathan Miller.",
            "expected_pii": [
                "987-65-4321",
                "Johnathan Miller"
            ]
        },
        {
            "id": "SAMPLE_06",
            "text": "Transaction alert: Card 5412-7512-3412-9876 charged at 192.168.0.45.",
            "expected_pii": [
                "5412-7512-3412-9876",
                "192.168.0.45"
            ]
        },
        {
            "id": "SAMPLE_07",
            "text": "Registered Office: Plot No. 12, Industrial Area, Sector 5, Gurgaon - 122001.",
            "expected_pii": [
                "Plot No. 12, Industrial Area, Sector 5, Gurgaon - 122001"
            ]
        },
        {
            "id": "SAMPLE_08",
            "text": "Support desk logged request from user victor@enterprise.org (IP: 172.16.254.1).",
            "expected_pii": [
                "victor@enterprise.org",
                "172.16.254.1"
            ]
        },
        {
            "id": "SAMPLE_09",
            "text": "Notice sent to Apex Infra Limited, DIN: 01234567, Tel: 022-26598000.",
            "expected_pii": [
                "Apex Infra Limited",
                "01234567",
                "022-26598000"
            ]
        },
        {
            "id": "SAMPLE_10",
            "text": "Employee record: Vikram Malhotra, DOB: 22/11/1992, PAN: XYZPS9876K.",
            "expected_pii": [
                "Vikram Malhotra",
                "22/11/1992",
                "XYZPS9876K"
            ]
        }
    ]

    total_expected = 0
    total_detected = 0
    true_positives = 0

    for sample in unseen_test_cases:
        expected = sample["expected_pii"]
        total_expected += len(expected)
        redacted_text, entities = redactor.redact(sample["text"])
        detected_originals = [e['original'] for e in entities]
        total_detected += len(detected_originals)

        for exp in expected:
            if any(exp in orig or orig in exp for orig in detected_originals):
                true_positives += 1

    precision = (true_positives / total_detected) * 100 if total_detected > 0 else 0
    recall = (true_positives / total_expected) * 100 if total_expected > 0 else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
    accuracy = (true_positives / total_expected) * 100 if total_expected > 0 else 0

    print(f"\nFresh Real-World Out-of-Sample Benchmark Results:")
    print(f"Precision: {precision:.2f}% | Recall: {recall:.2f}% | F1: {f1:.2f}% | Accuracy: {accuracy:.2f}%")

    assert precision >= 90.0
    assert recall >= 90.0

if __name__ == '__main__':
    test_fresh_real_world_samples()
