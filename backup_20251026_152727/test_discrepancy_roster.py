"""
Test suite for discrepancy roster functionality.

Tests that the discrepancy roster correctly identifies and tracks members who are
technically eligible for promotion but have flags that require command review:
- UIF (Unfavorable Information File) codes
- RE (Reenlistment Eligibility) codes
- PAFSC (Skill Level) issues
"""

import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from board_filter import board_filter


def test_uif_discrepancy():
    """Test that UIF code triggers discrepancy status."""
    print("\n" + "="*70)
    print("TEST 1: UIF Discrepancy")
    print("="*70)

    # Member with UIF code 3 and disposition date before SCOD
    grade = 'SSG'
    year = 2025
    date_of_rank = '01-Jan-2022'  # Well before TIG requirement
    uif_code = 3  # UIF code > 1
    uif_disposition_date = '01-Dec-2025'  # Before SCOD (31-Jan-2026)
    tafmsd = '01-Jan-2018'  # Sufficient TIS
    re_status = '1A'  # Good RE code
    pafsc = '3D137'  # Sufficient skill level (7-level for SSG)
    two_afsc = None
    three_afsc = None
    four_afsc = None

    result = board_filter(
        grade=grade,
        year=year,
        date_of_rank=date_of_rank,
        uif_code=uif_code,
        uif_disposition_date=uif_disposition_date,
        tafmsd=tafmsd,
        re_status=re_status,
        pafsc=pafsc,
        two_afsc=two_afsc,
        three_afsc=three_afsc,
        four_afsc=four_afsc,
        member_name="TEST_MEMBER_UIF",
        ssan="TEST123"
    )

    print(f"\nResult: {result}")

    # Assert it returns discrepancy tuple
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert result[0] == 'discrepancy', f"Expected 'discrepancy', got {result[0]}"
    assert 'UIF' in result[1], f"Expected UIF in reason, got {result[1]}"

    print("✅ TEST PASSED: UIF correctly triggers discrepancy")
    return True


def test_re_code_discrepancy():
    """Test that problematic RE code triggers discrepancy status."""
    print("\n" + "="*70)
    print("TEST 2: RE Code Discrepancy")
    print("="*70)

    # Member with problematic RE code
    grade = 'TSG'
    year = 2025
    date_of_rank = '01-Jan-2020'  # Well before TIG requirement
    uif_code = 0  # No UIF
    uif_disposition_date = None
    tafmsd = '01-Jan-2014'  # Sufficient TIS
    re_status = '4H'  # Article 15 (problematic RE code)
    pafsc = '3D1X7'  # Sufficient skill level
    two_afsc = None
    three_afsc = None
    four_afsc = None

    result = board_filter(
        grade=grade,
        year=year,
        date_of_rank=date_of_rank,
        uif_code=uif_code,
        uif_disposition_date=uif_disposition_date,
        tafmsd=tafmsd,
        re_status=re_status,
        pafsc=pafsc,
        two_afsc=two_afsc,
        three_afsc=three_afsc,
        four_afsc=four_afsc,
        member_name="TEST_MEMBER_RE",
        ssan="TEST456"
    )

    print(f"\nResult: {result}")

    # Assert it returns discrepancy tuple
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert result[0] == 'discrepancy', f"Expected 'discrepancy', got {result[0]}"
    assert '4H' in result[1], f"Expected 4H in reason, got {result[1]}"

    print("✅ TEST PASSED: RE code correctly triggers discrepancy")
    return True


def test_pafsc_discrepancy():
    """Test that insufficient PAFSC skill level triggers discrepancy status."""
    print("\n" + "="*70)
    print("TEST 3: PAFSC Skill Level Discrepancy")
    print("="*70)

    # Member with insufficient PAFSC skill level
    grade = 'SSG'  # Requires 7-level
    year = 2025
    date_of_rank = '01-Jan-2022'  # Well before TIG requirement
    uif_code = 0  # No UIF
    uif_disposition_date = None
    tafmsd = '01-Jan-2018'  # Sufficient TIS
    re_status = '1A'  # Good RE code
    pafsc = '3D135'  # Only 5-level (insufficient for SSG which requires 7)
    two_afsc = None
    three_afsc = None
    four_afsc = None

    result = board_filter(
        grade=grade,
        year=year,
        date_of_rank=date_of_rank,
        uif_code=uif_code,
        uif_disposition_date=uif_disposition_date,
        tafmsd=tafmsd,
        re_status=re_status,
        pafsc=pafsc,
        two_afsc=two_afsc,
        three_afsc=three_afsc,
        four_afsc=four_afsc,
        member_name="TEST_MEMBER_PAFSC",
        ssan="TEST789"
    )

    print(f"\nResult: {result}")

    # Assert it returns discrepancy tuple
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert result[0] == 'discrepancy', f"Expected 'discrepancy', got {result[0]}"
    assert 'PAFSC' in result[1] or 'skill level' in result[1].lower(), f"Expected PAFSC in reason, got {result[1]}"

    print("✅ TEST PASSED: PAFSC skill level correctly triggers discrepancy")
    return True


def test_eligible_no_discrepancy():
    """Test that a clean member does NOT trigger discrepancy status."""
    print("\n" + "="*70)
    print("TEST 4: Clean Member (No Discrepancy)")
    print("="*70)

    # Completely clean member
    grade = 'SSG'
    year = 2025
    date_of_rank = '01-Jan-2022'  # Well before TIG requirement
    uif_code = 0  # No UIF
    uif_disposition_date = None
    tafmsd = '01-Jan-2018'  # Sufficient TIS
    re_status = '1A'  # Good RE code
    pafsc = '3D137'  # Sufficient skill level (7-level for SSG)
    two_afsc = None
    three_afsc = None
    four_afsc = None

    result = board_filter(
        grade=grade,
        year=year,
        date_of_rank=date_of_rank,
        uif_code=uif_code,
        uif_disposition_date=uif_disposition_date,
        tafmsd=tafmsd,
        re_status=re_status,
        pafsc=pafsc,
        two_afsc=two_afsc,
        three_afsc=three_afsc,
        four_afsc=four_afsc,
        member_name="TEST_MEMBER_CLEAN",
        ssan="TEST000"
    )

    print(f"\nResult: {result}")

    # Assert it returns True (eligible, no discrepancy)
    assert result is True or (isinstance(result, tuple) and result[0] is True), \
        f"Expected True or (True, ...), got {result}"

    print("✅ TEST PASSED: Clean member does not trigger discrepancy")
    return True


def test_multiple_discrepancies():
    """Test member with multiple discrepancy flags (UIF + RE code)."""
    print("\n" + "="*70)
    print("TEST 5: Multiple Discrepancies")
    print("="*70)

    # Member with both UIF and problematic RE code
    grade = 'SSG'
    year = 2025
    date_of_rank = '01-Jan-2022'
    uif_code = 2  # UIF present
    uif_disposition_date = '01-Dec-2025'  # Before SCOD
    tafmsd = '01-Jan-2018'
    re_status = '2J'  # Under investigation (problematic)
    pafsc = '3D137'  # Sufficient skill level (7-level)
    two_afsc = None
    three_afsc = None
    four_afsc = None

    result = board_filter(
        grade=grade,
        year=year,
        date_of_rank=date_of_rank,
        uif_code=uif_code,
        uif_disposition_date=uif_disposition_date,
        tafmsd=tafmsd,
        re_status=re_status,
        pafsc=pafsc,
        two_afsc=two_afsc,
        three_afsc=three_afsc,
        four_afsc=four_afsc,
        member_name="TEST_MEMBER_MULTI",
        ssan="TEST999"
    )

    print(f"\nResult: {result}")

    # Should catch first discrepancy (UIF is checked before RE code)
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert result[0] == 'discrepancy', f"Expected 'discrepancy', got {result[0]}"
    assert 'UIF' in result[1] or '2J' in result[1], \
        f"Expected UIF or 2J in reason, got {result[1]}"

    print("✅ TEST PASSED: Multiple discrepancies correctly detected")
    return True


def run_all_tests():
    """Run all discrepancy roster tests."""
    print("\n" + "#"*70)
    print("# DISCREPANCY ROSTER TEST SUITE")
    print("#"*70)

    tests = [
        test_uif_discrepancy,
        test_re_code_discrepancy,
        test_pafsc_discrepancy,
        test_eligible_no_discrepancy,
        test_multiple_discrepancies
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"\n❌ TEST FAILED: {test.__name__}")
            print(f"   Error: {e}")
        except Exception as e:
            failed += 1
            print(f"\n❌ TEST ERROR: {test.__name__}")
            print(f"   Exception: {e}")

    print("\n" + "#"*70)
    print(f"# TEST RESULTS")
    print("#"*70)
    print(f"Total Tests: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Discrepancy roster is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
