import requests
import json
import os
import csv
from datetime import datetime
import packaging.version

# --- Configuration ---
# Get your Snyk API token from an environment variable for security
SNYK_API_TOKEN = os.getenv("SNYK_API_TOKEN")
if not SNYK_API_TOKEN:
    raise ValueError("SNYK_API_TOKEN environment variable not set.")

# The Snyk API base URL
SNYK_API_URL = "https://api.snyk.io/rest"

# The group ID to search within. Find this in the Snyk UI or API.
SNYK_GROUP_ID = "YOUR_SNYK_GROUP_ID" 

# The name of the package to report on
TARGET_PACKAGE = "package-xyz"
# The maximum allowed version (exclusive)
TARGET_VERSION = "0.0.2"

def get_headers():
    """Returns the headers for API requests."""
    return {
        "Authorization": f"token {SNYK_API_TOKEN}",
        "Content-Type": "application/vnd.api+json"
    }

def get_organizations(group_id):
    """Fetches all organizations within a given group."""
    print("Fetching organizations...")
    url = f"{SNYK_API_URL}/groups/{group_id}/orgs?version=2023-08-31"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    orgs = response.json().get("data", [])
    print(f"Found {len(orgs)} organizations.")
    return orgs

def get_projects(org_id):
    """Fetches all projects for a given organization."""
    print(f"Fetching projects for organization: {org_id}...")
    url = f"{SNYK_API_URL}/orgs/{org_id}/projects?version=2023-08-31"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    projects = response.json().get("data", [])
    print(f"Found {len(projects)} projects.")
    return projects

def get_dependencies(org_id, project_id):
    """Fetches dependencies for a given project."""
    url = f"{SNYK_API_URL}/orgs/{org_id}/projects/{project_id}/dependencies?version=2023-08-31"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json().get("data", [])

def main():
    """Main function to run the reporting script."""
    print("Starting Snyk API report generation...")
    all_violations = []

    try:
        orgs = get_organizations(SNYK_GROUP_ID)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching organizations: {e}")
        return

    for org in orgs:
        org_id = org['id']
        org_name = org['attributes']['name']
        
        try:
            projects = get_projects(org_id)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching projects for org {org_name}: {e}")
            continue

        for project in projects:
            project_id = project['id']
            project_name = project['attributes']['name']
            
            try:
                dependencies = get_dependencies(org_id, project_id)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching dependencies for project {project_name}: {e}")
                continue

            for dep in dependencies:
                # The dependency name and version are structured within the JSON data
                dep_name = dep['attributes']['name']
                dep_version_str = dep['attributes']['version']

                if dep_name == TARGET_PACKAGE:
                    try:
                        dep_version = packaging.version.parse(dep_version_str)
                        target_version = packaging.version.parse(TARGET_VERSION)
                    except packaging.version.InvalidVersion:
                        print(f"Warning: Skipping unparsable version for '{dep_name}' in project '{project_name}'.")
                        continue

                    if dep_version > target_version:
                        all_violations.append({
                            "organization": org_name,
                            "project": project_name,
                            "package": dep_name,
                            "version": dep_version_str,
                            "snyk_url": f"https://snyk.io/org/{org_name}/project/{project_id}"
                        })

    # Generate a timestamped CSV report
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"snyk_report_violations_{timestamp}.csv"

    if all_violations:
        print(f"\n🚨 Found {len(all_violations)} violations. Generating report: {report_filename}")
        with open(report_filename, 'w', newline='') as csvfile:
            fieldnames = ['organization', 'project', 'package', 'version', 'snyk_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(all_violations)
        print("✅ Report successfully created.")
    else:
        print("\n✅ No violations found across all projects.")

if __name__ == "__main__":
    main()
