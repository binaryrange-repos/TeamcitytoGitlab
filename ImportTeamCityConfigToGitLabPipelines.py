import json
import os
import re

GITLAB_SECURITY_TEMPLATES = [
    "Security/SAST.gitlab-ci.yml",
    "Security/Secret-Detection.gitlab-ci.yml",
    "Security/Dependency-Scanning.gitlab-ci.yml"
]

def safe_filename(name):
    return re.sub(r'[^A-Za-z0-9_\-]', '_', name)

def generate_gitlab_pipeline(project, output_dir="."):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    project_name = safe_filename(project["name"])
    filename = os.path.join(output_dir, f"{project_name}.gitlab-ci.yml")
    with open(filename, "w", encoding="utf-8") as f:
        # Include GitLab security templates
        f.write("include:\n")
        for tpl in GITLAB_SECURITY_TEMPLATES:
            f.write(f"  - template: {tpl}\n")
        f.write("\n")
        # Generate jobs for each build configuration
        for bt in project.get("build_types", []):
            job_name = safe_filename(bt["name"])
            f.write(f"{job_name}:\n")
            f.write("  stage: build\n")
            # Parameters as variables
            params = bt.get("parameters", {})
            if any(params.values()):
                f.write("  variables:\n")
                for section in params.values():
                    for k, v in section.items():
                        f.write(f"    {k}: \"{v}\"\n")
            # Script from build steps
            f.write("  script:\n")
            for step in bt.get("steps", []):
                script = ""
                for key in ["script.content", "jetbrains_powershell_script_code", "command.executable", "dockerfile.path"]:
                    if key in step["properties"]:
                        script = step["properties"][key]
                        break
                if script:
                    for line in script.splitlines():
                        f.write(f"    - {line}\n")
            # Artifacts
            if bt.get("artifact_rules"):
                f.write("  artifacts:\n")
                f.write("    paths:\n")
                for rule in bt["artifact_rules"].splitlines():
                    rule = rule.strip()
                    if rule:
                        f.write(f"      - {rule}\n")
            f.write("\n")
    print(f"Generated: {filename}")
    # Recurse into subprojects
    for sub in project.get("subprojects", []):
        generate_gitlab_pipeline(sub, output_dir)

def main():
    output_dir = "Gitlab_Pipelines"
    with open("teamcity_export.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    for project in data:
        generate_gitlab_pipeline(project, output_dir)

if __name__ == "__main__":
    main()