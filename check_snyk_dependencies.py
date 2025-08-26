import json
import sys
import packaging.version

# --- Configuration ---
# The name of the package you want to check
TARGET_PACKAGE = "package-xyz"
# The maximum allowed version (exclusive)
TARGET_VERSION = "0.0.2"
# The path to the Snyk JSON output file
SNYK_JSON_FILE = "snyk-results.json"

def check_dependencies(file_path):
    """
    Parses a Snyk JSON output file and checks for a specific package version.
    
    Args:
        file_path (str): The path to the Snyk JSON file.
    
    Returns:
        bool: True if a violation is found, False otherwise.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Snyk results file not found at '{file_path}'")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{file_path}'")
        sys.exit(1)

    print(f"Checking Snyk dependencies for '{TARGET_PACKAGE}' version > '{TARGET_VERSION}'...")

    if "vulnerabilities" not in data:
        print("No vulnerabilities section found in the JSON. Exiting.")
        return False
    
    # Iterate through all dependencies and check for the target package
    for vuln in data["vulnerabilities"]:
        if "from" in vuln and len(vuln["from"]) > 0:
            # The 'from' array represents the dependency path. The last item is the package itself.
            package_name = vuln["from"][-1].split('@')[0]
            
            # Check if the package name matches
            if package_name == TARGET_PACKAGE:
                # Extract the version from the package string (e.g., package-xyz@1.2.3)
                try:
                    package_version_str = vuln["from"][-1].split('@')[1]
                    # Use a robust version parser to handle different version formats
                    package_version = packaging.version.parse(package_version_str)
                    target_version = packaging.version.parse(TARGET_VERSION)
                except (IndexError, packaging.version.InvalidVersion) as e:
                    print(f"Warning: Could not parse version for package '{package_name}'. Skipping.")
                    continue

                # Enforce the gating rule
                if package_version > target_version:
                    print(f"🚨 Gating violation found!")
                    print(f"Package: {package_name}@{package_version}")
                    print(f"Dependency path: {' -> '.join(vuln['from'])}")
                    print(f"Rule: Version must be less than or equal to {TARGET_VERSION}")
                    return True

    print("✅ No violations found. All clear!")
    return False

if __name__ == "__main__":
    if check_dependencies(SNYK_JSON_FILE):
        # Exit with a non-zero status code to fail the CI/CD job
        sys.exit(1)
    else:
        # Exit with a zero status code to pass the CI/CD job
        sys.exit(0)
