from ingestion.parse import parse_pdf

res = parse_pdf("../resumes/Shruti_Panda_Resume.pdf")

print(f"\nTotal sections detected: {len(res)}\n")

EXPECTED_SECTIONS_CONTAIN = [
    "summary", "education", "skills", "experience",
    "project", "certification"
]

keys_lower = [k.lower() for k in res.keys()]

print("=== SECTION VALIDATION ===")
for expected in EXPECTED_SECTIONS_CONTAIN:
    found = any(expected in k for k in keys_lower)
    status = "PASS" if found else "FAIL"
    print(f"[{status}] Section containing '{expected}'")

print("\n=== SECTION QUALITY CHECK ===")
for k, v in res.items():
    lines = [l for l in v.splitlines() if l.strip()]
    has_run_on = any(len(l) > 300 for l in lines)

    print(f"\n--- {k} ---")
    print(f"Lines     : {len(lines)}")
    print(f"Chars     : {len(v)}")
    print(f"Run-on?   : {'YES' if has_run_on else 'No'}")
    print(f"Preview   : {v[:150]}")