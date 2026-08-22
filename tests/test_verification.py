from vtms_v1.verification import run_verification_suite


def test_verification_suite_passes_and_includes_exact_benchmark() -> None:
    report = run_verification_suite()
    checks = {check["check_id"]: check for check in report["checks"]}

    assert report["verification_status"] == "PASS"
    assert "V-ANALYTIC-01" in checks
    assert checks["V-ANALYTIC-01"]["passed"] is True
    assert len(report["checks"]) >= 22
