import requests
from requests.auth import HTTPBasicAuth
import json

TEAMCITY_URL = "http://localhost/"
USERNAME = "admin"
PASSWORD = "admin"

def get_projects():
    url = f"{TEAMCITY_URL}/app/rest/projects"
    resp = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers={"Accept": "application/json"})
    return resp.json()["project"]

def get_build_types(project_id):
    url = f"{TEAMCITY_URL}/app/rest/projects/id:{project_id}"
    resp = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers={"Accept": "application/json"})
    return resp.json().get("buildTypes", {}).get("buildType", [])

def get_build_steps(build_type_id):
    url = f"{TEAMCITY_URL}/app/rest/buildTypes/id:{build_type_id}/steps"
    resp = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers={"Accept": "application/json"})
    steps = resp.json().get("step", [])
    detailed_steps = []
    for step in steps:
        step_id = step.get("id")
        detail_url = f"{TEAMCITY_URL}/app/rest/buildTypes/id:{build_type_id}/steps/id:{step_id}"
        detail_resp = requests.get(detail_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers={"Accept": "application/json"})
        if detail_resp.status_code == 200:
            detailed_steps.append(detail_resp.json())
        else:
            detailed_steps.append(step)
    return detailed_steps

def get_vcs_roots(build_type_id):
    url = f"{TEAMCITY_URL}/app/rest/buildTypes/id:{build_type_id}/vcs-root-entries"
    resp = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers={"Accept": "application/json"})
    vcs_entries = resp.json().get("vcs-root-entry", [])
    vcs_roots = []
    for entry in vcs_entries:
        vcs_root_id = entry["vcs-root"]["id"]
        detail_url = f"{TEAMCITY_URL}/app/rest/vcs-roots/id:{vcs_root_id}"
        detail_resp = requests.get(detail_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers={"Accept": "application/json"})
        if detail_resp.status_code == 200:
            detail = detail_resp.json()
            vcs_roots.append({
                "id": detail.get("id"),
                "name": detail.get("name"),
                "fetchUrl": next((p["value"] for p in detail.get("properties", {}).get("property", []) if p["name"] == "url"), None),
                "defaultBranch": next((p["value"] for p in detail.get("properties", {}).get("property", []) if p["name"] == "branch"), None)
            })
    return vcs_roots

def get_triggers(build_type_id):
    url = f"{TEAMCITY_URL}/app/rest/buildTypes/id:{build_type_id}/triggers"
    resp = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers={"Accept": "application/json"})
    triggers = resp.json().get("trigger", [])
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
    resp = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers={"Accept": "application/json"})
    params = resp.json().get("property", [])
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
    resp = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers={"Accept": "application/json"})
    requirements = resp.json().get("agent-requirement", [])
    reqs = []
    for req in requirements:
        reqs.append({
            "parameter": req.get("property-name"),
            "condition": req.get("condition"),
            "value": req.get("value"),
            "type": req.get("type"),  # "explicit" or "buildStep"
            "buildStep": req.get("build-step", {}).get("name") if req.get("build-step") else None
        })
    return reqs

def get_compatible_agents(build_type_id):
    url = f"{TEAMCITY_URL}/app/rest/buildTypes/id:{build_type_id}/compatibleAgents"
    resp = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers={"Accept": "application/json"})
    if resp.status_code != 200:
        print(f"Failed to fetch compatible agents for {build_type_id}: {resp.status_code} {resp.text}")
        return []
    try:
        agents = resp.json().get("agent", [])
    except Exception as e:
        print(f"JSON decode error for compatible agents: {e}\nResponse text: {resp.text}")
        return []
    return [agent.get("name") for agent in agents]

def collect_data():
    all_data = []
    projects = get_projects()
    for project in projects:
        project_data = {
            "name": project['name'],
            "id": project['id'],
            "build_types": []
        }
        build_types = get_build_types(project['id'])
        for bt in build_types:
            bt_data = {
                "name": bt['name'],
                "id": bt['id'],
                "steps": [],
                "vcs_roots": get_vcs_roots(bt['id']),
                "triggers": get_triggers(bt['id']),
                "parameters": get_parameters(bt['id']),
                "agent_requirements": get_agent_requirements(bt['id']),
                # "compatible_agents": get_compatible_agents(bt['id'])  # Commented out
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
        all_data.append(project_data)
    return all_data

def collect_data_for_project(project_name):
    projects = get_projects()
    # Find the project by name (case-insensitive)
    project = next((p for p in projects if p['name'].lower() == project_name.lower()), None)
    if not project:
        print(f"Project '{project_name}' not found.")
        return []
    project_data = {
        "name": project['name'],
        "id": project['id'],
        "build_types": []
    }
    build_types = get_build_types(project['id'])
    for bt in build_types:
        bt_data = {
            "name": bt['name'],
            "id": bt['id'],
            "steps": [],
            "vcs_roots": get_vcs_roots(bt['id']),
            "triggers": get_triggers(bt['id']),
            "parameters": get_parameters(bt['id']),
            "agent_requirements": get_agent_requirements(bt['id']),
            # "compatible_agents": get_compatible_agents(bt['id'])  # If you want to re-enable later
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
    return [project_data]

def save_json(data, filename="teamcity_export.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def save_markdown(data, filename="teamcity_summary.md"):
    def format_properties(props):
        if not props:
            return "_No properties found_\n"
        lines = ["| Property | Value |", "|---|---|"]
        for k, v in props.items():
            lines.append(f"| {k} | {v} |")
        return "\n".join(lines) + "\n"

    with open(filename, "w", encoding="utf-8") as f:
        for project in data:
            f.write(f"# Project: {project['name']} (`{project['id']}`)\n\n")
            for bt in project["build_types"]:
                f.write(f"## Build Configuration: {bt['name']} (`{bt['id']}`)\n\n")

                # VCS Roots
                if bt.get("vcs_roots"):
                    f.write("### VCS Roots\n\n")
                    for vcs in bt["vcs_roots"]:
                        f.write(f"- **Name:** {vcs.get('name','')}  \n")
                        f.write(f"  - **Fetch URL:** `{vcs.get('fetchUrl','')}`  \n")
                        f.write(f"  - **Default Branch:** `{vcs.get('defaultBranch','')}`\n")
                    f.write("\n")

                # Parameters
                params = bt.get("parameters", {})
                if params:
                    f.write("### Parameters\n\n")
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

                # Triggers
                if bt.get("triggers"):
                    f.write("### Triggers\n\n")
                    for trig in bt["triggers"]:
                        f.write(f"- **Type:** {trig['type']}\n")
                        for k, v in trig["properties"].items():
                            f.write(f"  - {k}: {v}\n")
                    f.write("\n")

                # Steps
                if bt.get("steps"):
                    f.write("### Build Steps\n\n")
                    for step in bt["steps"]:
                        f.write(f"#### Step: {step['name']} ({step['type']})\n\n")
                        # Try to show what is executed
                        exec_info = ""
                        # Common script keys for different runners
                        for key in ["script.content", "jetbrains_powershell_script_code", "command.executable", "dockerfile.path"]:
                            if key in step["properties"]:
                                exec_info = step["properties"][key]
                                break
                        if exec_info:
                            f.write(f"**Executes:**\n```\n{exec_info}\n```\n\n")
                        # Show all properties
                        f.write(format_properties(step["properties"]))
                        f.write("\n")

                # Agent Requirements
                if bt.get("agent_requirements"):
                    f.write("### Agent Requirements\n\n")
                    for req in bt["agent_requirements"]:
                        step_info = f" (Step: {req['buildStep']})" if req["buildStep"] else ""
                        f.write(f"- **{req['type'].capitalize()}**: `{req['parameter']}` {req['condition']} `{req['value']}`{step_info}\n")
                    f.write("\n")

            f.write("\n")

def main():
    project_name = input("Enter the TeamCity project name: ").strip()
    data = collect_data_for_project(project_name)
    if not data:
        print("No data to export.")
        return
    save_json(data)
    save_markdown(data)
    print("Export complete: teamcity_export.json and teamcity_summary.md")

if __name__ == "__main__":
    main()