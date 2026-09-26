import sys
sys.path.insert(0, '.')
from proofpatch.runner import run_verification

tests = [
    ("baseline",  3, "Reproduced"),
    ("candidate", 3, "Verified against this test suite"),
    # bad_patch tests are EXPECTED to fail (negative control proves the suite catches bad fixes)
    # status is STATUS_REPRODUCED because the test suite successfully caught the defect
    ("bad_patch", 3, "Reproduced"),
]
all_ok = True
for v, ps, exp in tests:
    r = run_verification(v, "main", ps)
    ok = r["status"] == exp
    all_ok = all_ok and ok
    print(f"{'PASS' if ok else 'FAIL'} | {v:10s} | status={r['status']!r} | actual={r['actual_ids']} | missing={r['missing_ids']}")
print("RESULT:", "ALL PASS" if all_ok else "FAILURES DETECTED")
