
import requests
import os
import base64

PLATFORM_URL = "http://localhost:12345"

# API url templates
CONTEST_SUBMISSIONS_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/CONTEST_ID/submissions?strict=false"
CONTEST_PROBLEMS_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/CONTEST_ID/problems?strict=false"
CONTEST_TEAMS_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/CONTEST_ID/teams?public=true&strict=false"
SUBMISSION_JUDGEMENT_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/judgements?submission_id=SUBMISSION_ID&strict=false"
SUBMISSION_SOURCE_CODE_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/CONTEST_ID/submissions/SUBMISSION_ID/source-code?strict=false"

EXTENSIONS = {
    "cpp": "cpp",
    "c": "c",
    "python": "py",
    "java": "java",
    "python3": "py"
}

# Authentication credentials
USERNAME = "admin"
PASSWORD = "JfYI-hnvj24NVauo"

# Create a session object
session = requests.Session()

# Perform authentication
session.auth = (USERNAME, PASSWORD)



def decode(base64_string):
    """
    Decode a Base64 encoded string.
    """
    try:
        decoded_bytes = base64.b64decode(base64_string)
        decoded_string = decoded_bytes.decode('utf-8')
        return decoded_string
    except Exception as e:
        print("Error decoding Base64 string:", str(e))


def get_json_response(request_url):
    """
    Send a GET request to the specified URL and return the response data as JSON.
    """
    response = session.get(request_url)

    data = None

    # Check the response status code
    if response.status_code == 200:
        # Request was successful
        data = response.json()  # Get the response data in JSON format
    else:
        # Request failed
        print("Request failed with status code:", response.status_code)

    return data


def get_contest_teams(contest_id):
    """
    Get the teams for a contest.
    """
    url = CONTEST_TEAMS_URL_TEMPLATE.replace("CONTEST_ID", str(contest_id))

    return get_json_response(url)


def get_contest_problems(contest_id):
    """
    Get the problems for a contest.
    """
    url = CONTEST_PROBLEMS_URL_TEMPLATE.replace("CONTEST_ID", str(contest_id))

    return get_json_response(url)


def get_contest_submissions(contest_id):
    """
    Get the submissions for a contest.
    """
    url = CONTEST_SUBMISSIONS_URL_TEMPLATE.replace("CONTEST_ID", str(contest_id))

    return get_json_response(url)


def get_submission_source_code(contest_id, submission_id):
    """
    Get the source code for a submission.
    """
    url = SUBMISSION_SOURCE_CODE_URL_TEMPLATE.replace("CONTEST_ID", str(contest_id)) \
        .replace("SUBMISSION_ID", str(submission_id))

    data = get_json_response(url)

    if data is not None:
        return decode(data[0]["source"])
    else:
        return None


def get_submission_judgement(submission_id):
    """
    Get the judgement for a submission.
    """
    url = SUBMISSION_JUDGEMENT_URL_TEMPLATE.replace("SUBMISSION_ID", str(submission_id))

    return get_json_response(url)


def get_submission_verdict(submission_id):
    """
    Get the verdict for a submission.
    """
    for judgement in get_submission_judgement(submission_id):
        print(judgement)
        if judgement["valid"] is True:
            return judgement["judgement_type_id"]

    return None


contest_id = 2

# Process each submission and store the relevant information
for submission in get_contest_submissions(contest_id):
    if submission["id"] == "40":
        team_id = submission["team_id"]
        problem_id = submission["problem_id"]
        submission_id = submission["id"]

        submission_verdict = get_submission_verdict(submission_id)

        language = submission["language_id"]
        code_source = get_submission_source_code(contest_id, submission_id)


        print(team_id)
        print(problem_id)
        print(submission_id)
        print(submission_verdict)
        print(language)
        print(code_source)
        print()



    