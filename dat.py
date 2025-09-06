#!/usr/bin/env python3
import csv
import random
from datetime import date, timedelta

random.seed(42)
N = 1000
OUT_FILE = "augmented_claims_1000.csv"

# Code pools
# Code sets (curated for plausibility)
ICD10 = [
    # Endocrine & metabolic
    "E11.9","E11.65","E10.9","E78.5","E03.9","E66.9","E55.9","E53.8","E16.2","E04.2",
    # Circulatory
    "I10","I11.9","I25.10","I20.9","I21.9","I48.91","I50.9","I63.9","I65.29","I73.9",
    # Respiratory
    "J06.9","J18.9","J20.9","J30.9","J44.9","J45.909","J45.40","J96.00","J98.4","J22",
    # Digestive
    "K21.9","K29.70","K35.80","K40.20","K52.9","K57.30","K59.00","K70.30","K80.20","K92.2",
    # Musculoskeletal
    "M17.9","M19.90","M25.50","M25.561","M25.562","M54.2","M54.5","M81.0","M79.1","M51.26",
    # Nervous system
    "G40.909","G43.909","G47.00","G56.00","G89.29","G20","G35","G62.9","G81.90","G93.40",
    # Injury & poisoning
    "S72.001A","S72.002A","S52.501A","S52.502A","S82.001A","S82.002A","T81.4XXA","T14.90XA","T78.40XA","T50.905A",
    # Symptoms & signs
    "R07.9","R51.9","R42","R10.9","R11.0","R19.7","R50.9","R55","R60.9","R73.9",
    # Factors influencing health
    "Z00.00","Z00.01","Z01.10","Z12.11","Z12.31","Z23","Z51.11","Z79.01","Z79.899","Z98.890"
]

CPT = [
    # E/M
    "99212","99213","99214","99215","99203","99204","99205","99283","99284","99285",
    # Preventive
    "99395","99396","99397","99385","99386","99387","99406","99407","99408","99409",
    # Diagnostics
    "93000","93005","93010","71045","71046","71047","71048","74018","74019","74021",
    # Procedures
    "97110","97112","97530","97535","97542","20550","20551","20610","20611","36415",
    # Endoscopy
    "43235","43239","45378","45380","45385","31575","31576","31577","31578","31579",
    # Surgery
    "27130","27447","29880","29881","29882","29883","29888","29889","29891","29892",
    # Lab
    "80050","80053","80061","81001","81002","81003","81005","82043","82270","82272",
    # Imaging
    "70450","70460","70470","70551","70552","70553","72125","72126","72127","72128"
]

HCPCS = [
    # Your originals
    "J3420","G0008","L1830","A4550","S0028","E0114","Q3014","E0100","V2020","G0438",
    # Drugs & biologics
    "J1885","J1100","J1170","J1200","J1756","J1815","J2405","J2550","J2785","J3301",
    # DME
    "E0110","E0111","E0112","E0113","E0116","E0117","E0118","E0119","E0140","E0141",
    # Supplies
    "A4206","A4207","A4208","A4209","A4210","A4211","A4212","A4213","A4215","A4216",
    # Services
    "G0439","G0442","G0444","G0446","G0447","G0448","G0459","G0463","G0475","G0476",
    # Vision/hearing
    "V2100","V2101","V2102","V2103","V2104","V2105","V2106","V2107","V2108","V2109",
    # Misc
    "S0020","S0021","S0022","S0023","S0024","S0025","S0026","S0027","S0029","S0030"
]

MOD = [
    # CPT Level I
    "25","26","50","51","52","53","54","55","56","57",
    "58","59","62","63","66","76","77","78","79","80",
    "81","82","90","91","92","95","96","97","99",
    # HCPCS Level II
    "E1","E2","E3","E4","FA","F1","F2","F3","F4","F5",
    "F6","F7","F8","F9","LC","LD","LE","LT","RT","QK",
    "QX","QY","QZ","XE","XP","XS","XU","ZA","ZB","ZC",
    # Anesthesia physical status
    "P1","P2","P3","P4","P5","P6",
    # Informational
    "GA","GC","GE","GG","GH","GJ","GM","GN","GO","GP",
    "GQ","GR","GS","GT","GU","GV","GW","GX","GY","GZ"
]

DRG = [
    "064","065","066","067","068","069","070","071","072","073",
    "074","075","076","077","078","079","080","081","082","083",
    "084","085","086","087","088","089","090","091","092","093",
    "094","095","096","097","098","099","100","101","102","103",
    "121","122","123","124","125","146","147","148","149","150",
    "151","152","153","154","155","156","157","158","159","173",
    "175","176","177","178","179","180","181","182","183","184",
    "185","186","187","188","189","190","191","192","193","194",
    "195","196","197","198","199","200","201","202","203","204"
]


PLAN_TYPES = ["PPO","HMO","EPO","POS"]
BENEFITS = {"PPO":1_000_000,"HMO":750_000,"EPO":500_000,"POS":250_000}

# Allowed submission window per payer (days)
ALLOWED_DAYS = {f"PY{p:02d}": random.choice([30,45,60])
                for p in range(1,9)}

# Denial definitions
DENIALS = [
    ("CARC 16","Missing prior authorization","Eligibility","Y",30,"High"),
    ("CARC 197","Precertification absent","Eligibility","Y",30,"High"),
    ("CARC 18","Duplicate claim/service","Technical","Y",60,"Low"),
    ("CARC 96","Non-covered service","Clinical","N",0,"Medium"),
    ("CARC 29","Time limit for filing expired","Administrative","N",0,"Medium"),
    ("CARC 109","Benefit maximum reached","Eligibility","Y",45,"High"),
    ("CARC 204","Service not covered per plan","Eligibility","N",0,"High"),
    ("CARC 125","Submission/billing error","Technical","Y",45,"Medium"),
    ("CARC 23","Impact of prior payer adjudication","Administrative","Y",30,"Low"),
]

HEADERS = [
    "ClaimID","PatientID","PayerID","ProviderID","ClaimAmount","Reimbursement",
    "DenialStatus","ServiceDate","Contracted_Submission_Date","SubmissionDate",
    "ProcessedDate","ICD10_Code","CPT_Code","HCPCS_Code","Modifier","DRG_Code",
    "Coverage_Start_Date","Coverage_End_Date","Plan_Type","Benefit_Limit",
    "PriorAuth_Obtained","Referral_Required","Clearinghouse_Edit_Count",
    "Denial_Code","Denial_Reason","Denial_Category","Appeal_Allowed",
    "Days_To_Appeal","Denial_Severity"
]

def date_str(d):
    return d.isoformat()

def random_service_date(i):
    return date(2024, 1, 1) + timedelta(days=(i % 334))

def coverage_window(i, svc_date, denial_code):
    # base window choices
    if i % 5 == 0:
        start, end = date(2023, 6, 1), date(2024, 5, 31)
    elif i % 3 == 0:
        start, end = date(2024, 2, 1), date(2025, 1, 31)
    else:
        start, end = date(2024, 1, 1), date(2024, 12, 31)

    # CARC 204 → force lapse before service
    if denial_code == "CARC 204":
        end = svc_date - timedelta(days=random.randint(1, 30))

    return start, end

def gen_dates(payer_id, svc_date, denial_code):
    allowed = ALLOWED_DAYS[payer_id]
    contracted = svc_date + timedelta(days=allowed)

    if denial_code == "CARC 29":
        # Timely‐filing denial → after contracted
        sub = contracted + timedelta(days=random.randint(1, 15))
    else:
        # Normal submission between service and contracted
        delta = max((contracted - svc_date).days, 1)
        sub = svc_date + timedelta(days=random.randint(0, delta))

    proc = sub + timedelta(days=random.randint(1, 10))
    return contracted, sub, proc

def gen_amount(i, plan, denial_code):
    base = 150 + (i % 50) * 25 + [0.00,0.50,0.99][i % 3]
    if denial_code == "CARC 109":
        # Over‐limit amount
        return round(BENEFITS[plan] + random.uniform(10, 500), 2)
    return round(base, 2)

def gen_prior_auth(denial_code):
    if denial_code in ("CARC 16","CARC 197"):
        return "N"
    return random.choice(["Y","N"])

def gen_ch_edits(denial_code):
    if denial_code == "CARC 125":
        return random.randint(5, 12)
    return random.randint(0, 4)

with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(HEADERS)

    for i in range(1, N+1):
        claim_id    = f"C{i:04d}"
        patient_id  = f"P{(i % 200)+1:03d}"
        payer_id    = f"PY{(i % 8)+1:02d}"
        provider_id = f"PR{((i*3) % 12)+1:02d}"
        denied = (i % 4 == 0) or (i % 9 == 0)

        if denied:
            d_code, d_reason, d_cat, d_appeal, d_days, d_sev = DENIALS[i % len(DENIALS)]
            status = 1
        else:
            d_code, d_reason, d_cat, d_appeal, d_days, d_sev = (
                "None","Paid in full","None","N",0,"None"
            )
            status = 0

        svc_date = random_service_date(i)
        cov_start, cov_end = coverage_window(i, svc_date, d_code)
        plan = random.choice(PLAN_TYPES)
        benef = BENEFITS[plan]
        contracted, sub_date, proc_date = gen_dates(payer_id, svc_date, d_code)
        amt = gen_amount(i, plan, d_code)

        if status and d_cat == "Technical" and i % 2 == 0:
            reimb = round(amt * 0.5, 2)
        else:
            reimb = amt if not status else 0.00

        prior_auth = gen_prior_auth(d_code)
        referral   = random.choice(["Y","N"])
        ch_edits   = gen_ch_edits(d_code)

        row = [
            claim_id, patient_id, payer_id, provider_id,
            f"{amt:.2f}", f"{reimb:.2f}", status,
            date_str(svc_date), date_str(contracted),
            date_str(sub_date), date_str(proc_date),
            random.choice(ICD10), random.choice(CPT),
            random.choice(HCPCS), random.choice(MOD),
            random.choice(DRG), date_str(cov_start),
            date_str(cov_end), plan, benef,
            prior_auth, referral, ch_edits,
            d_code, d_reason, d_cat, d_appeal, d_days, d_sev
        ]
        writer.writerow(row)

print(f"Done. Wrote {N} records to {OUT_FILE}")