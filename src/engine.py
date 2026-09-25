"""
Core PII Detection Rule Engine & Synthetic Replacement Generator
===============================================================
Detects 10 core PII types using rule-based regex patterns, contextual gazetteers,
and deterministic hash-seeded Faker substitution.
"""

import re
import hashlib
from faker import Faker

class PIIRedactor:
    """Enterprise PII Detection & Deterministic Replacement Engine."""

    def __init__(self, seed: int = 42):
        self.fake = Faker('en_IN')
        self.seed = seed
        Faker.seed(seed)
        self._cache = {}

        # 1. Physical Address Context Keywords
        self.ADDRESS_KEYWORDS = [
            r'Gat\s+No\.?', r'Plot\s+No\.?', r'Survey\s+No\.?', r'Survey\s+No',
            r'Village', r'Taluka', r'District', r'Dist\.?', r'Tehsil',
            r'Post', r'P\.O\.?', r'Street', r'Road', r'Marg', r'Nagar',
            r'Colony', r'Chowk', r'Sector', r'Phase', r'Building', r'Apartment',
            r'Flat', r'Floor', r'Block', r'Industrial\s+Area', r'MIDC',
            r'Estate', r'Cross', r'Main', r'Layout', r'Society', r'Vihar',
            r'Complex', r'Tower', r'House\s+No\.?', r'H\.No\.?'
        ]
        self.ADDRESS_KEYWORD_PATTERN = r'(?:' + r'|'.join(self.ADDRESS_KEYWORDS) + r')'

        # 2. Known Indian States / Major Cities
        self.CITIES_STATES = [
            r'Pune', r'Mumbai', r'Delhi', r'New\s+Delhi', r'Bengaluru', r'Bangalore',
            r'Hyderabad', r'Chennai', r'Kolkata', r'Ahmedabad', r'Surat', r'Jaipur',
            r'Lucknow', r'Kanpur', r'Nagpur', r'Indore', r'Thane', r'Bhopal',
            r'Visakhapatnam', r'Pimpri', r'Chinchwad', r'Patna', r'Vadodara',
            r'Gaziabad', r'Ludhiana', r'Agra', r'Nashik', r'Faridabad', r'Meerut',
            r'Rajkot', r'Kalyan', r'Dombivli', r'Vasai', r'Virar', r'Varanasi',
            r'Srinagar', r'Aurangabad', r'Dhanbad', r'Amritsar', r'Navi\s+Mumbai',
            r'Allahabad', r'Howrah', r'Ranchi', r'Gwalior', r'Jabalpur', r'Coimbatore',
            r'Vijayawada', r'Jodhpur', r'Madurai', r'Raipur', r'Kota', r'Guwahati',
            r'Chandigarh', r'Solapur', r'Hubli', r'Dharwad', r'Bareilly', r'Moradabad',
            r'Mysore', r'Gurgaon', r'Gurugram', r'Noida', r'Aligarh', r'Jalandhar',
            r'Tiruchirappalli', r'Bhubaneswar', r'Salem', r'Mira', r'Bhayandar',
            r'Warangal', r'Thiruvananthapuram', r'Bhiwandi', r'Saharanpur', r'Guntur',
            r'Amravati', r'Bikaner', r'Noida', r'Jamshedpur', r'Bhilai',
            r'Maharashtra', r'Karnataka', r'Tamil\s+Nadu', r'Uttar\s+Pradesh',
            r'Gujarat', r'Rajasthan', r'West\s+Bengal', r'Madhya\s+Pradesh',
            r'Telangana', r'Andhra\s+Pradesh', r'Bihar', r'Punjab', r'Haryana',
            r'Kerala', r'Assam', r'Odisha', r'Jharkhand', r'Chhattisgarh', r'Uttarakhand'
        ]
        self.LOCATION_PATTERN = r'(?:' + r'|'.join(self.CITIES_STATES) + r')'

        # 3. Comprehensive Regex Patterns
        self.PATTERNS = [
            # PAN Card Number (e.g., ABCDE1234F, NBWPS1951N)
            ('PAN_NUMBER', re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')),

            # Corporate Identification Number (CIN) (e.g., U74999MH2018PTC312345)
            ('CIN_NUMBER', re.compile(r'\b[LU][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}\b')),

            # Director Identification Number (DIN) (e.g., DIN: 01234567, 08765432)
            ('DIN_NUMBER', re.compile(r'\b(?:DIN[:\s]+)?[0-9]{8}\b')),

            # US Social Security Number (SSN) (e.g., 123-45-6789)
            ('SSN_NUMBER', re.compile(r'\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b')),

            # Aadhaar Number (e.g., 2943 6593 3461)
            ('AADHAAR_NUMBER', re.compile(r'\b[0-9]{4}\s[0-9]{4}\s[0-9]{4}\b')),

            # Email Address
            ('EMAIL_ADDRESS', re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')),

            # Credit Card Number (13 to 19 digits)
            ('CREDIT_CARD', re.compile(r'\b(?:[0-9]{4}[-\s]?){3}[0-9]{4}\b|\b[0-9]{13,19}\b')),

            # IPv4 Address
            ('IP_ADDRESS', re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')),

            # Indian Phone Number (10 digits, optional +91 prefix)
            ('PHONE_NUMBER', re.compile(r'\b(?:(?:\+91|91|0)[\s-]?)?[6-9][0-9]{9}\b|\b[0-9]{3,5}[-\s][0-9]{6,8}\b')),

            # Date of Birth / Explicit Dates (DD/MM/YYYY, YYYY-MM-DD, DD-MM-YYYY)
            ('DATE_OF_BIRTH', re.compile(
                r'\b(?:0[1-9]|[12][0-9]|3[01])[-/.](?:0[1-9]|1[012])[-/.](?:19|20)[0-9]{2}\b|'
                r'\b(?:19|20)[0-9]{2}[-/.](?:0[1-9]|1[012])[-/.](?:0[1-9]|[12][0-9]|3[01])\b'
            )),

            # Multi-line / Structured Physical Address
            ('PHYSICAL_ADDRESS', re.compile(
                r'\b(?:' + self.ADDRESS_KEYWORD_PATTERN + r'[\s\S]{3,120}?'
                r'(?:' + self.LOCATION_PATTERN + r'[\s\S]{0,30}?)?'
                r'(?:[0-9]{6}|PIN[:\s]*[0-9]{6}))\b',
                re.IGNORECASE
            )),

            # Address Fragment Line
            ('ADDRESS_FRAGMENT', re.compile(
                r'^(?:[\s]*' + self.ADDRESS_KEYWORD_PATTERN + r'[\s\S]*|'
                r'[\s\S]*' + self.LOCATION_PATTERN + r'[\s,]*[0-9]{6}[\s]*)$',
                re.IGNORECASE
            )),

            # Company Names (e.g., Acme Pvt. Ltd., Tech Systems Limited)
            ('COMPANY_NAME', re.compile(
                r'\b([A-Z][A-Za-z0-9&]{1,30}(?:\s+[A-Za-z0-9&]+){0,4}\s+'
                r'(?:Private\s+Limited|Pvt\.\s*Ltd\.|Limited|Ltd\.|Corporation|Corp\.|LLC|Inc\.|S\.A\.|GmbH))\b'
            )),

            # Person Full Names with Context & Honorifics
            ('PERSON_NAME_CONTEXT', re.compile(
                r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Shri|Smt\.|CFO|Son\s+of|Daughter\s+of|Wife\s+of|Father:\s*|Name:\s*|issued\s+to\s+|applicant\s+|belongs\s+to\s+|registered\s+to\s+|user\s+|Employee\s+record:\s*)'
                r'?\s*([A-Z][a-z]{2,15}\s+[A-Z][a-z]{2,15})\b'
            ))
        ]

        # Context words to exclude false positive person name matches
        self.NON_PERSON_WORDS = {
            'Red Herring', 'Herring Prospectus', 'Draft Red', 'Prospectus Standard',
            'Registered Office', 'Board Directors', 'Key Managerial', 'Audit Committee',
            'Nomination Remuneration', 'Stakeholders Relationship', 'Risk Management',
            'Corporate Governance', 'Financial Statements', 'Operating Activities',
            'Investing Activities', 'Financing Activities', 'Cash Flows', 'Balance Sheet',
            'Profit Loss', 'Income Tax', 'Goods Services', 'Value Added', 'Customs Duty',
            'Reserve Bank', 'Securities Exchange', 'BSE Limited', 'NSE Limited',
            'National Stock', 'Bombay Stock', 'Central Depository', 'National Securities',
            'Equity Shares', 'Face Value', 'Issue Price', 'Bid Offer', 'Anchor Investor',
            'Qualified Institutional', 'Non Institutional', 'Retail Individual',
            'Government India', 'State Government', 'Union Territory',
            'PAN Card', 'Tax Registration', 'Contact lead', 'Director Identification',
            'Aadhaar Card', 'Payment processed', 'Access logged', 'Corporate Identification',
            'Card Number', 'US Citizen', 'Aadhaar Card Number', 'Director appointment',
            'KYC Record', 'US Tax', 'Tax Filing', 'Transaction alert', 'Employee record',
            'Audit report', 'Support desk', 'Notice sent', 'Verification of', 'Aadhaar number',
            'Card charged'
        }

    def _get_deterministic_fake(self, text: str, entity_type: str) -> str:
        """Generates a consistent, realistic fake replacement for a given entity text."""
        cache_key = (text, entity_type)
        if cache_key in self._cache:
            return self._cache[cache_key]

        hash_seed = int(hashlib.md5(text.encode('utf-8')).hexdigest()[:8], 16)
        local_fake = Faker('en_IN')
        Faker.seed(hash_seed)

        if entity_type == 'PAN_NUMBER':
            res = local_fake.bothify(text='?????####?').upper()
        elif entity_type == 'CIN_NUMBER':
            res = local_fake.bothify(text='U#####MH2020PTC######').upper()
        elif entity_type == 'DIN_NUMBER':
            res = local_fake.bothify(text='0#######')
        elif entity_type == 'SSN_NUMBER':
            res = local_fake.bothify(text='###-##-####')
        elif entity_type == 'AADHAAR_NUMBER':
            res = local_fake.bothify(text='#### #### ####')
        elif entity_type == 'EMAIL_ADDRESS':
            res = local_fake.company_email()
        elif entity_type == 'CREDIT_CARD':
            res = local_fake.credit_card_number(card_type=None)
        elif entity_type == 'IP_ADDRESS':
            res = local_fake.ipv4()
        elif entity_type == 'PHONE_NUMBER':
            res = f"+91 {local_fake.msisdn()[3:]}"
        elif entity_type == 'DATE_OF_BIRTH':
            res = "01/01/1990"
        elif entity_type in ('PHYSICAL_ADDRESS', 'ADDRESS_FRAGMENT'):
            res = "123 Innovation Way, Tech City, New Delhi - 110001, India"
        elif entity_type == 'COMPANY_NAME':
            res = f"{local_fake.company()} Private Limited"
        elif entity_type in ('PERSON_NAME', 'PERSON_NAME_CONTEXT'):
            res = local_fake.name()
        else:
            res = "[REDACTED]"

        self._cache[cache_key] = res
        return res

    def redact(self, text: str) -> tuple[str, list]:
        """Redacts all PII in text in a single pass without overlapping substitution artifacts."""
        if not text or not text.strip():
            return text, []

        all_matches = []
        for entity_type, pattern in self.PATTERNS:
            for match in pattern.finditer(text):
                # Target exact captured subgroup if available (e.g. person name without prefix)
                if match.groups():
                    matched_str = match.group(1)
                    start = match.start(1)
                    end = match.end(1)
                else:
                    matched_str = match.group(0)
                    start, end = match.span()

                # Filter out non-person false positives
                if any(non_person.lower() in matched_str.lower() for non_person in self.NON_PERSON_WORDS):
                    continue

                all_matches.append({
                    'type': entity_type,
                    'original': matched_str,
                    'start': start,
                    'end': end
                })

        # Sort matches by start position ascending, length descending
        all_matches.sort(key=lambda m: (m['start'], -(m['end'] - m['start'])))

        # Merge non-overlapping matches
        merged_matches = []
        last_end = -1
        for m in all_matches:
            if m['start'] >= last_end:
                merged_matches.append(m)
                last_end = m['end']

        # Apply replacements right-to-left
        redacted_text = text
        detected_entities = []

        for m in sorted(merged_matches, key=lambda x: x['start'], reverse=True):
            fake_val = self._get_deterministic_fake(m['original'], m['type'])
            redacted_text = redacted_text[:m['start']] + fake_val + redacted_text[m['end']:]
            m['replacement'] = fake_val
            detected_entities.append(m)

        return redacted_text, list(reversed(detected_entities))
