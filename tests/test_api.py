import tests.utils as utils
from libcoveoc4ids.api import APIException


def test_valid_data():
    """" Test valid data should have no errors """
    errors, ctx = utils.test_fixture("example-data.json")

    assert len(errors.keys()) == 0, "Validation errors found"


def test_invalid_data():
    """ Test valid data but with no useful fields """
    errors, ctx = utils.test_fixture("rubbish.json")

    assert len(errors.keys()) == 5, "Expecting 5 validation errors"


def test_validation_errors():
    """ Check that the validation errors are the ones we are expecting """
    errors, ctx = utils.test_fixture("validation-errors-package.json")

    invalid_code = []
    invalid_uri = []
    invalid_number = []
    invalid_date = []
    invalid_string = []
    invalid_array = []
    invalid_object = []
    invalid_int = []

    missing_value = []
    invalid_length = []

    for err in errors:
        if "Invalid code found in" in err:
            invalid_code.append(err)

        elif "Invalid 'uri' found" in err:
            invalid_uri.append(err)

        elif "Date is not in the correct format" in err:
            invalid_date.append(err)

        elif "is not a string" in err:
            invalid_string.append(err)

        elif "is not a integer" in err:
            invalid_int.append(err)

        elif "is not a JSON object" in err:
            invalid_object.append(err)

        elif "is not a JSON array" in err:
            invalid_array.append(err)

        elif "is not a number" in err:
            invalid_number.append(err)

        elif "is too short" in err:
            invalid_length.append(err)

        elif "is missing but required" in err:
            missing_value.append(err)

        else:
            # We shouldn't reach here if we have sorted all the validation
            # errors
            assert False, "Validation error '%s' not captured" % err

    assert len(invalid_code) == 5, "Expecting 5 invalid codes"
    assert len(invalid_uri) == 2, "Expecting 2 invalid uris"
    assert len(invalid_date) == 1, "Expecting 1 invalid dates"
    assert len(invalid_string) == 18, "Expecting 18 invalid strings"
    assert len(invalid_int) == 1, "Expecting 1 invalid integers"
    assert len(invalid_object) == 3, "Expecting 3 invalid objects"
    assert len(invalid_array) == 8, "Expecting 8 invalid arrays"
    assert len(invalid_number) == 4, "Expecting 4 invalid numbers"
    assert len(invalid_length) == 2, "Expecting 2 invalid value lengths"
    assert len(missing_value) == 8, "Expecting 8 missing values"

    assert len(errors.keys()) == 52, "Expecting total of 52 validation errors!"


def test_additional_fields():
    """ Test that the additional fields have been parsed """
    errors, ctx = utils.test_fixture("rubbish.json")

    assert ctx['additional_fields_count'] == 2, "Expecting two additional fields"
    print(ctx)


def test_invalid_json():
    """ Should cause an exception on broken json file """
    try:
        errors, ctx = utils.test_fixture("invalid-json.json")
    except APIException:
        return

    assert False, "We should have had an exception generated by invalid json file"


def test_additional_checks():
    """ Test the additional checks to make sure each expected one is present in test data"""
    errors, ctx = utils.test_fixture("example-additional-checks.json")
    checked = 0
    expected_checks = 4

    assert len(ctx["additional_checks"]) == expected_checks, "Additional checks are incomplete"

    for check_result in ctx["additional_checks"]:
        # Tests to make sure we have the right dictionary created
        assert "check_id" in check_result, "Check result has no check_id field"
        assert "message" in check_result, "Check result has no message field"
        assert "paths" in check_result, "Check result has no paths"

        assert len(check_result["paths"]) > 0, "Check result has no paths"

        assert type(check_result["check_id"] is str), "Type additional check check_id is not a string"
        assert type(check_result["message"] is str), "Type additional check message is not a string"
        assert type(check_result["paths"] is list), "Type additional check paths is not a list"

        if check_result["check_id"] in [
            "missing-currency",
            "missing-values",
            "invalid-project-ids",
            "missing-org-refs"
        ]:
            checked += 1

    assert(expected_checks == checked), \
        "Checks tested not expected total for this test data %s" % ctx["additional_checks"]


def test_additional_checks_no_parties():
    """ Extra check on missing-org-refs by removing all the parties definitions and thus"""
    """ triggering for every possible path"""

    errors, ctx = utils.test_fixture("example-additional-checks-no-parties.json")

    assert len(ctx["additional_checks"][0]["paths"]) == 15, "The number of paths where organisation refs"\
        " are missing is not correct"
