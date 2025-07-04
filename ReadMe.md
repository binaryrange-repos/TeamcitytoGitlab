# TeamCity Project Exporter

This Python script exports TeamCity project and subproject configuration details (including build steps, triggers, parameters, and VCS roots) to both **JSON** and **Markdown** files.  
It is designed to help you analyze and migrate TeamCity build pipelines, for example, to GitLab.

---

## Prerequisites

- Python 3.x installed
- `requests` library (`pip install requests`)
- Access to your TeamCity server (tested with TeamCity 2019.1+)
- TeamCity user credentials with permission to view project settings

---

## Usage

1. **Clone or download this repository.**
2. **Edit the script** (`FetchTeamCityProject.py`) to set your TeamCity server URL, username, and password at the top of the file:
    ```python
    TEAMCITY_URL = "http://localhost:8111"
    USERNAME = "admin"
    PASSWORD = "admin"
    ```
3. **Open a terminal in the script folder.**
4. **Run the script:**
    ```
    python FetchTeamCityProject.py
    ```
5. **When prompted, enter the TeamCity project name** (as shown in the TeamCity UI).

---

## Output

After running, you will get:

- `teamcity_export.json`  
  A structured JSON file containing all project, subproject, and build configuration details.

- `teamcity_summary.md`  
  A Markdown file with a human-readable summary of all build configurations, steps, triggers, parameters, and VCS roots for the selected project and all its subprojects.

---

## Example

```
Enter the TeamCity project name: Juice Shop
Export complete: teamcity_export.json and teamcity_summary.md
```

---

## What is Exported?

- **Project and Subproject hierarchy**
- **Build Configurations** (for each project/subproject)
- **VCS Roots** (Git URLs, branches)
- **Parameters** (configuration, system, environment)
- **Triggers** (type and properties)
- **Build Steps** (type, script/command, all step properties)
- **Agent Requirements**

---

## Notes

- The script recursively finds all subprojects using the `parentProjectId` field.
- Connections are not exported (not supported by TeamCity 2019.1 REST API).
- If you need to export from a newer TeamCity version, you may need to adjust the script for new REST endpoints.

---

## Troubleshooting

- If you get authentication or connection errors, check your TeamCity URL, username, and password.
- If you get empty subprojects, ensure your TeamCity user has permission to view all projects.

---

## License Information

This project is the property of [https://www.secopsify.com/](https://www.secopsify.com/), Binaryrange Limited.

It is released under the MIT License:

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
```