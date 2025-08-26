# Snyk Package Manager CICD Check & Reporting

This repository contains two Python scripts designed to automate and enhance Snyk's capabilities for enforcing custom policies and generating reports.

-----

### Scripts Explained 💻

#### `check_snyk_dependencies.py`

  * **Function**: This script acts as a **CI/CD pipeline gate**.
  * **Purpose**: It parses the JSON output from a `snyk test` command and fails the build if a specific package, configured as `package-xyz`, has a version greater than the allowed threshold (`v0.0.2`). This ensures that no new code is deployed with a forbidden dependency version.

#### `snyk_reporter.py`

  * **Function**: This script generates a **scheduled report**.
  * **Purpose**: Using the Snyk REST API, it scans all projects across your organizations to find and report every instance of `package-xyz` that violates your version rule. The output is a clear CSV file that provides a complete view of your environment's compliance, which is invaluable for security teams and stakeholders.

-----

### Setup and Configuration ⚙️

#### Prerequisites

  * Python 3.x
  * `snyk-cli`
  * A Snyk API Token

#### Installation

Install the necessary Python packages using the provided `requirements.txt` file.

```bash
pip install -r requirements.txt
```

#### Configuration

**For `check_snyk_dependencies.py`:**

Open the script and edit the following variables to match your requirements:

  * `TARGET_PACKAGE`: The name of the package you want to gate.
  * `TARGET_VERSION`: The maximum allowed version for that package.

**For `snyk_reporter.py`:**

You need to provide your Snyk API token to the script securely.

  * **Local Development**: Set the token as an environment variable in your terminal.
      * **macOS/Linux**: `export SNYK_API_TOKEN="your_snyk_api_token"`
      * **Windows**: `set SNYK_API_TOKEN="your_snyk_api_token"`
  * **CI/CD Pipelines**: Configure the API token as a **CI/CD variable** or **secret** within your pipeline's settings.
  * **Cron Jobs**: Ensure the environment variable is explicitly defined in your cron script to make it available to the Python script.

You'll also need to update the `SNYK_GROUP_ID` variable within the script itself with your specific Snyk group ID.

-----

### Usage Examples 🚀

#### CI/CD Gating (`check_snyk_dependencies.py`)

Run this as a step in your CI/CD pipeline.

```bash
# Step 1: Run Snyk test and save JSON output
snyk test --json-file-output=snyk-results.json

# Step 2: Execute the gating script
python check_snyk_dependencies.py
```

If a version violation is found, the script will exit with a non-zero code, failing your pipeline.

#### Scheduled Reporting (`snyk_reporter.py`)

Run this script as a scheduled job (e.g., using a cron job or a scheduled CI/CD pipeline).

```bash
# Ensure the API token environment variable is set
python snyk_reporter.py
```

The script will generate a timestamped CSV report named `snyk_report_violations_*.csv` in the same directory, listing all found violations.
