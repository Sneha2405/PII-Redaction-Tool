"""
Precision PIL Image PII Redactor for Embedded Identity Cards
============================================================
Applies pixel-perfect aligned redactions over embedded identity images in DOCX archives:
1. PAN Card image (768 x 962)
2. Aadhaar Card image (900 x 900)

Leaves face photos on the top left 100% UNTOUCHED and VISIBLE while cleanly
redacting text lines (Names, Father Names, DOBs, ID Numbers, Signatures, Addresses).
"""

from PIL import Image, ImageDraw

# Sleek dark navy blue fill matching document identity headers
FILL_BG = (18, 36, 64)
TXT_FG = (255, 255, 255)

def redact_pan_card_pil(img: Image.Image) -> Image.Image:
    """Applies pixel-perfect redactions onto the PAN Card image (768x962)."""
    draw = ImageDraw.Draw(img)

    # 1. PAN Number (NBWPS1951N) - Exact overlap under 'Permanent Account Number Card'
    box_pan = (240, 220, 445, 258)
    draw.rectangle(box_pan, fill=FILL_BG)
    draw.text((box_pan[0] + 8, box_pan[1] + 8), "ABCDE1234F", fill=TXT_FG)

    # 2. Name (VISHAL SINGH) - Exact overlap under 'नाम / Name'
    box_name = (35, 300, 220, 330)
    draw.rectangle(box_name, fill=FILL_BG)
    draw.text((box_name[0] + 8, box_name[1] + 8), "JOHN DOE", fill=TXT_FG)

    # 3. Father's Name (SUGRIV SINGH) - Exact overlap under 'पिता का नाम / Father's Name'
    box_fname = (35, 375, 230, 408)
    draw.rectangle(box_fname, fill=FILL_BG)
    draw.text((box_fname[0] + 8, box_fname[1] + 8), "PETER PARKER", fill=TXT_FG)

    # 4. DOB (06/05/2000) - Exact overlap under '06/05/2000'
    box_dob = (35, 460, 150, 490)
    draw.rectangle(box_dob, fill=FILL_BG)
    draw.text((box_dob[0] + 8, box_dob[1] + 8), "01/01/1990", fill=TXT_FG)

    # 5. Signature (Vishal Singh) - Exact overlap on signature area
    box_sig = (330, 420, 480, 460)
    draw.rectangle(box_sig, fill=FILL_BG)
    draw.text((box_sig[0] + 8, box_sig[1] + 8), "[REDACTED]", fill=TXT_FG)

    # 6. Bottom Address Card - Exact overlap on English address lines
    box_addr = (30, 750, 460, 865)
    draw.rectangle(box_addr, fill=FILL_BG)
    draw.text((box_addr[0] + 8, box_addr[1] + 8), "[ADDRESS REDACTED]", fill=TXT_FG)

    # 7. Bottom Phone/Fax & Email lines
    box_contact = (30, 870, 460, 945)
    draw.rectangle(box_contact, fill=FILL_BG)
    draw.text((box_contact[0] + 8, box_contact[1] + 8), "[CONTACT REDACTED]", fill=TXT_FG)

    return img


def redact_aadhaar_card_pil(img: Image.Image) -> Image.Image:
    """Applies pixel-perfect redactions onto the Aadhaar Card image (900x900)."""
    draw = ImageDraw.Draw(img)

    # 1. Top Card Name (MERAJ KHAN) - Starts at X=305 to leave photo (X: 150..300) 100% UNCOVERED
    box_name = (305, 95, 540, 158)
    draw.rectangle(box_name, fill=FILL_BG)
    draw.text((box_name[0] + 8, box_name[1] + 16), "ALEX MERCER", fill=TXT_FG)

    # 2. Top Card Father Name (Father: Sudhdan Khan)
    box_fname = (305, 160, 540, 222)
    draw.rectangle(box_fname, fill=FILL_BG)
    draw.text((box_fname[0] + 8, box_fname[1] + 16), "FATHER: JOHN DOE", fill=TXT_FG)

    # 3. Top Card DOB (DOB : 12/12/1988)
    box_dob = (305, 224, 540, 288)
    draw.rectangle(box_dob, fill=FILL_BG)
    draw.text((box_dob[0] + 8, box_dob[1] + 16), "DOB: 01/01/1990", fill=TXT_FG)

    # 4. Top Card Aadhaar Number (2943 6593 3461)
    box_num1 = (280, 290, 580, 342)
    draw.rectangle(box_num1, fill=FILL_BG)
    draw.text((box_num1[0] + 12, box_num1[1] + 10), "XXXX XXXX 9999", fill=TXT_FG)

    # 5. Bottom Card Address Block
    box_addr = (160, 480, 770, 620)
    draw.rectangle(box_addr, fill=FILL_BG)
    draw.text((box_addr[0] + 12, box_addr[1] + 20), "ADDRESS DETAILS REDACTED", fill=TXT_FG)

    # 6. Bottom Card Aadhaar Number (2943 6593 3461)
    box_num2 = (280, 725, 580, 785)
    draw.rectangle(box_num2, fill=FILL_BG)
    draw.text((box_num2[0] + 12, box_num2[1] + 10), "XXXX XXXX 9999", fill=TXT_FG)

    return img
