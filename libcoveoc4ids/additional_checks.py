import gettext
import re

from libcoveoc4ids.additional_check import AdditionalCheck

_ = gettext.gettext


class CurrencyCheck(AdditionalCheck):
    def process(self, data, flat_data):
        amount_path = re.compile(".*amount$")

        expected_currency_paths = []
        missing = []

        for path in flat_data.keys():
            if amount_path.match(path):
                expected_currency_paths.append(path[: -len("amount")] + "currency")

        for expected in expected_currency_paths:
            if expected not in flat_data:
                missing.append(expected[: -len("currency")])

        if len(missing) == 0:
            return True

        return self.result(
            "missing-currency",
            _(
                "There are %(count)d values without a currency. Currencies should be published for all values."
            )
            % {"count": len(missing)},
            missing,
        )


class EmptyValueCheck(AdditionalCheck):
    def process(self, data, flat_data):
        missing = []

        # Similar check to libcoveocds EmptyFieldCheck
        for path, value in flat_data.items():
            if isinstance(value, str) and len(value.strip()) == 0:
                missing.append(path)
            elif isinstance(value, dict) and len(value) == 0:
                missing.append(path)
            elif isinstance(value, list) and len(value) == 0:
                missing.append(path)

        if len(missing) == 0:
            return True

        return self.result(
            "missing-values",
            _("The data includes fields that are empty or contain only whitespaces. "
                "Fields that are not being used, or that have no value, "
                "should be excluded in their entirety (key and value) from the data"),
            missing,
        )


class ProjectPrefixCheck(AdditionalCheck):
    def process(self, data, flat_data):

        # matches /projects/10/id
        project_path = re.compile(r".*\/projects\/[0-9]+\/id$")
        # matches oc4ids-abc123-anything
        valid_project_id = re.compile(r"oc4ids\-[a-z0-9]{6}.+$")

        invalid_project_id_paths = []

        for path, value in flat_data.items():
            if project_path.match(path):
                # Note if there is no value the regex can't match we leave it to
                # the other checks to expose this error.
                if value and valid_project_id.match(value) is None:
                    invalid_project_id_paths.append(path)

        if len(invalid_project_id_paths) == 0:
            return True

        return self.result(
            "invalid-project-ids",
            _(
                "%(count)d of your project id fields has a problem: "
                "There is no prefix or the prefix format is not recognised."
            )
            % {"count": len(invalid_project_id_paths)},
            invalid_project_id_paths,
        )


class OrgReferencesExistCheck(AdditionalCheck):
    project_id_match = re.compile(r"^/projects/\d+")

    def __init__(self, *args, **kwargs):
        # Cache of project party ids
        self.project_parties_ids = {}

    def extract_project_from_path(self, path):
        """ Matches /projects/<int> and returns the int portion """

        return int(self.project_id_match.match(path).group()[len("/projects/"):])

    def projects_parties_ids(self, data, project):
        try:
            return self.project_parties_ids[project]
        except KeyError:
            try:
                self.project_parties_ids[project] = [
                    party["id"] for party in data["projects"][project]["parties"]
                ]
                return self.project_parties_ids[project]
            except KeyError:
                # This happens if the project has no parties defined
                return []

    def process(self, data, flat_data):
        org_paths = re.compile(
            r"(.*)(publicAuthority|budget\/budgetBreakdown\/\d+\/sourceParty|"
            r"contractingProcesses\/\d+\/summary\/(tender|suppliers\/\d+)(\/)"
            r"*(tenderers\/\d+|procuringEntity|administrativeEntity)*)\/id$"
        )

        missing_references_paths = []

        for path, value in flat_data.items():
            if org_paths.match(path):
                project = self.extract_project_from_path(path)
                if value not in self.projects_parties_ids(data, project):
                    missing_references_paths.append(path)

        if len(missing_references_paths) == 0:
            return True

        return self.result(
            "missing-org-refs",
            _(
                "There are %(count)d organization references with an id that does not match the id of any parties. "
                "All organization references should have an associated entry in the parties array with a matching id."
            )
            % {"count": len(missing_references_paths)},
            missing_references_paths,
        )


def additional_checks():
    return [
        EmptyValueCheck(),
        CurrencyCheck(),
        ProjectPrefixCheck(),
        OrgReferencesExistCheck(),
    ]
