import requests
from requests.auth import HTTPBasicAuth
import json

# --- CONFIGURATION ---
TEAMCITY_URL = "http://localhost/"
USERNAME = "admin"
PASSWORD = "admin"

# --- API HELPERS ---

def api_get(url):
    resp = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers={"Accept": "application/json"})
    resp.raise_for_status()
    return resp.json()

def get_projects():
    url = f"{TEAMCITY_URL}/app/rest/projects"
    return api_get(url)["project"]

def get_project_by_id(project_id):
    url = f"{TEAMCITY_URL}/app/rest/projects/id:{project_id}"
    return api_get(url)

def get_build_types(project_id):
    url = f"{TEAMCITY_URL}/app/rest/projects/id:{project_id}"
    return api_get(url).get("buildTypes", {}).get("buildType", [])

def get_build_steps(build_type_id):
    url = f"{TEAMCITY_URL}/app/rest/buildTypes/id:{build_type_id}/steps"
    steps = api_get(url).get("step", [])
    detailed_steps = []
    for step in steps:
        step_id = step.get("id")
        detail_url = f"{TEAMCITY_URL}/app/rest/buildTypes/id:{build_type_id}/steps/id:{step_id}"
        try:
            detail = api_get(detail_url)
            detailed_steps.append(detail)
        except Exception:
            detailed_steps.append(step)
    return detailed_steps

def get_vcs_roots(build_type_id):
    url = f"{TEAMCITY_URL}/app/rest/buildTypes/id:{build_type_id}/vcs-root-entries"
    vcs_entries = api_get(url).get("vcs-root-entry", [])
    vcs_roots = []
    for entry in vcs_entries:
        vcs_root_id = entry["vcs-root"]["id"]
        detail_url = f"{TEAMCITY_URL}/app/rest/vcs-roots/id:{vcs_root_id}"
        detail = api_get(detail_url)
        vcs_roots.append({
            "id": detail.get("id"),
            "name": detail.get("name"),
            "fetchUrl": next((p["value"] for p in detail.get("properties", {}).get("property", []) if p["name"] == "url"), None),
            "defaultBranch": next((p["value"] for p in detail.get("properties", {}).get("property", []) if p["name"] == "branch"), None)
        })
    return vcs_roots

def get_triggers(build_type_id):
    url = f"{TEAMCITY_URL}/app/rest/buildTypes/id:{build_type_id}/triggers"
    triggers = api_get(url).get("trigger", [])
    trigger_list = []
    for trig in triggers:
        trig_info = {
            "type": trig.get("type"),
            "properties": {prop['name']: prop['value'] for prop in trig.get("properties", {}).get("property", [])}
        }
        trigger_list.append(trig_info)
    return trigger_list

def get_parameters(build_type_id):
    url = f"{TEAMCITY_URL}/app/rest/buildTypes/id:{build_type_id}/parameters"
    params = api_get(url).get("property", [])
    config_params = {}
    system_props = {}
    env_vars = {}
    for param in params:
        name = param["name"]
        value = param.get("value", "")
        if name.startswith("system."):
            system_props[name] = value
        elif name.startswith("env."):
            env_vars[name] = value
        else:
            config_params[name] = value
    return {
        "configuration": config_params,
        "system": system_props,
        "environment": env_vars
    }

def get_agent_requirements(build_type_id):
    url = f"{TEAMCITY_URL}/app/rest/buildTypes/id:{build_type_id}/agent-requirements"
    requirements = api_get(url).get("agent-requirement", [])
    reqs = []
    for req in requirements:
        reqs.append({
            "parameter": req.get("property-name"),
            "condition": req.get("condition"),
            "value": req.get("value"),
            "type": req.get("type"),
            "buildStep": req.get("build-step", {}).get("name") if req.get("build-step") else None
        })
    return reqs

def get_artifact_rules(build_type_id):
    url = f"{TEAMCITY_URL}/app/rest/buildTypes/id:{build_type_id}"
    return api_get(url).get("artifactRules", "")

def get_build_template(build_type_id):
    url = f"{TEAMCITY_URL}/app/rest/buildTypes/id:{build_type_id}"
    data = api_get(url)
    template = data.get("template")
    if template:
        return {
            "id": template.get("id"),
            "name": template.get("name")
        }
    return None

def get_parameter_descriptions(project_id):
    url = f"{TEAMCITY_URL}/app/rest/projects/id:{project_id}/parameters"
    params = api_get(url).get("property", [])
    descs = {}
    for param in params:
        descs[param["name"]] = param.get("description", "")
    return descs

# --- DATA COLLECTORS ---

def collect_project_and_subprojects_flat(project_id, all_projects):
    project = get_project_by_id(project_id)
    project_data = {
        "name": project['name'],
        "id": project['id'],
        "parameter_descriptions": get_parameter_descriptions(project['id']),
        "build_types": [],
        "subprojects": []
    }
    build_types = get_build_types(project['id'])
    for bt in build_types:
        bt_data = {
            "name": bt['name'],
            "id": bt['id'],
            "template": get_build_template(bt['id']),
            "steps": [],
            "vcs_roots": get_vcs_roots(bt['id']),
            "triggers": get_triggers(bt['id']),
            "parameters": get_parameters(bt['id']),
            "agent_requirements": get_agent_requirements(bt['id']),
            "artifact_rules": get_artifact_rules(bt['id'])
        }
        steps = get_build_steps(bt['id'])
        for step in steps:
            step_name = step.get("name")
            step_type = step.get("type")
            if not step_name:
                step_name = f"{step_type} Step"
            step_info = {
                "name": step_name,
                "type": step_type,
                "properties": {prop['name']: prop['value'] for prop in step.get("properties", {}).get("property", [])}
            }
            bt_data["steps"].append(step_info)
        project_data["build_types"].append(bt_data)
    # Find subprojects by parentProjectId
    subprojects = [p for p in all_projects if p.get("parentProjectId") == project_id]
    for sub in subprojects:
        subproject_data = collect_project_and_subprojects_flat(sub["id"], all_projects)
        project_data["subprojects"].append(subproject_data)
    return project_data

def collect_data_for_project_and_subprojects(project_name):
    all_projects = get_projects()
    project = next((p for p in all_projects if p['name'].lower() == project_name.lower()), None)
    if not project:
        print(f"Project '{project_name}' not found.")
        return []
    return [collect_project_and_subprojects_flat(project["id"], all_projects)]

# --- FORMATTERS / EXPORTERS ---

def format_properties(props):
    if not props:
        return "_No properties found_\n"
    lines = ["| Property | Value |", "|---|---|"]
    for k, v in props.items():
        lines.append(f"| {k} | {v} |")
    return "\n".join(lines) + "\n"

def write_project_md(f, project, level=1):
    header = "#" * level
    f.write(f"{header} Project: {project['name']} (`{project['id']}`)\n\n")
    if project.get("parameter_descriptions"):
        f.write("### Parameter Descriptions\n\n")
        for k, v in project["parameter_descriptions"].items():
            if v:
                f.write(f"- **{k}**: {v}\n")
        f.write("\n")
    for bt in project["build_types"]:
        f.write(f"{'#'*(level+1)} Build Configuration: {bt['name']} (`{bt['id']}`)\n\n")
        if bt.get("template"):
            tpl = bt["template"]
            f.write(f"**Template:** {tpl.get('name','')} (`{tpl.get('id','')}`)\n\n")
        if bt.get("vcs_roots"):
            f.write("### VCS Roots\n\n")
            for vcs in bt["vcs_roots"]:
                f.write(f"- **Name:** {vcs.get('name','')}  \n")
                f.write(f"  - **Fetch URL:** `{vcs.get('fetchUrl','')}`  \n")
                f.write(f"  - **Default Branch:** `{vcs.get('defaultBranch','')}`\n")
            f.write("\n")
        params = bt.get("parameters", {})
        if params and any(params.values()):
            f.write("<details>\n<summary>Parameters</summary>\n\n")
            if params.get("configuration"):
                f.write("**Configuration Parameters:**\n\n")
                for k, v in params["configuration"].items():
                    f.write(f"- {k}: {v}\n")
                f.write("\n")
            if params.get("system"):
                f.write("**System Properties:**\n\n")
                for k, v in params["system"].items():
                    f.write(f"- {k}: {v}\n")
                f.write("\n")
            if params.get("environment"):
                f.write("**Environment Variables:**\n\n")
                for k, v in params["environment"].items():
                    f.write(f"- {k}: {v}\n")
                f.write("\n")
            f.write("</details>\n\n")
        if bt.get("triggers"):
            f.write("<details>\n<summary>Triggers</summary>\n\n")
            for trig in bt["triggers"]:
                f.write(f"- **Type:** {trig['type']}\n")
                for k, v in trig["properties"].items():
                    f.write(f"  - {k}: {v}\n")
            f.write("\n</details>\n\n")
        if bt.get("steps"):
            f.write("### Build Steps\n\n")
            for step in bt["steps"]:
                # Collapsible section for each step
                f.write(f"<details>\n<summary>Step: {step['name']} ({step['type']})</summary>\n\n")
                exec_info = ""
                for key in ["script.content", "jetbrains_powershell_script_code", "command.executable", "dockerfile.path"]:
                    if key in step["properties"]:
                        exec_info = step["properties"][key]
                        break
                if exec_info:
                    f.write(f"**Executes:**\n```\n{exec_info}\n```\n\n")
                f.write(format_properties(step["properties"]))
                f.write("\n</details>\n\n")
        if bt.get("agent_requirements"):
            f.write("### Agent Requirements\n\n")
            for req in bt["agent_requirements"]:
                step_info = f" (Step: {req['buildStep']})" if req["buildStep"] else ""
                f.write(f"- **{req['type'].capitalize()}**: `{req['parameter']}` {req['condition']} `{req['value']}`{step_info}\n")
            f.write("\n")
        if bt.get("artifact_rules"):
            f.write("### Artifact Rules\n\n")
            f.write(f"```\n{bt['artifact_rules']}\n```\n\n")
    for sub in project.get("subprojects", []):
        write_project_md(f, sub, level=level+1)

def save_json(data, filename="teamcity_export.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def save_markdown(data, filename="teamcity_summary.md"):
    with open(filename, "w", encoding="utf-8") as f:
        for project in data:
            write_project_md(f, project)

# --- MAIN ---

def main():
    project_name = "Juice Shop"
    print(f"Exporting TeamCity project: {project_name}")
    data = collect_data_for_project_and_subprojects(project_name)
    if not data:
        print("No data to export.")
        return
    save_json(data)
    save_markdown(data)
    print("Export complete: teamcity_export.json and teamcity_summary.md")

if __name__ == "__main__":
    main()