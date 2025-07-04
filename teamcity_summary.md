# Project: Juice Shop (`JuiceShop`)

## Build Configuration: Build (`JuiceShop_Build`)

### VCS Roots

- **Name:** https://github.com/juice-shop/juice-shop.git#refs/heads/master  
  - **Fetch URL:** `https://github.com/juice-shop/juice-shop.git`  
  - **Default Branch:** `refs/heads/master`

### Parameters

**Configuration Parameters:**

- para1: test

**System Properties:**

- system.para2: test

**Environment Variables:**

- env.para3: test

### Triggers

- **Type:** vcsTrigger
  - branchFilter: +:*
  - enableQueueOptimization: true
  - quietPeriodMode: DO_NOT_USE

### Build Steps

<details>
<summary>Step: DockerCommand Step (DockerCommand)</summary>

**Executes:**
```
Dockerfile
```

| Property | Value |
|---|---|
| docker.command.type | build |
| docker.push.remove.image | true |
| dockerfile.path | Dockerfile |
| dockerfile.source | PATH |
| teamcity.step.mode | default |

</details>

<details>
<summary>Step: simpleRunner Step (simpleRunner)</summary>

**Executes:**
```
./vagrant/bootstrap.sh
```

| Property | Value |
|---|---|
| script.content | ./vagrant/bootstrap.sh |
| teamcity.step.mode | default |
| use.custom.script | true |

</details>

<details>
<summary>Step: echo step (jetbrains_powershell)</summary>

**Executes:**
```
echo "Powershell commands1"
echo "Powershell commands2"
```

| Property | Value |
|---|---|
| jetbrains_powershell_execution | PS1 |
| jetbrains_powershell_noprofile | true |
| jetbrains_powershell_script_code | echo "Powershell commands1"
echo "Powershell commands2" |
| jetbrains_powershell_script_mode | CODE |
| teamcity.step.mode | default |

</details>

## Project: Sub-Juice Shop (`JuiceShop_SubJuiceShop`)

### Build Configuration: Sub-Build (`JuiceShop_SubJuiceShop_SubBuild`)

### VCS Roots

- **Name:** https://github.com/juice-shop/juice-shop.git#refs/heads/master  
  - **Fetch URL:** `https://github.com/juice-shop/juice-shop.git`  
  - **Default Branch:** `refs/heads/master`

### Parameters

### Triggers

- **Type:** vcsTrigger
  - branchFilter: +:*
  - enableQueueOptimization: true
  - quietPeriodMode: DO_NOT_USE

### Build Steps

<details>
<summary>Step: Step 1 (jetbrains_powershell)</summary>

**Executes:**
```
echo "step 1"
```

| Property | Value |
|---|---|
| jetbrains_powershell_execution | PS1 |
| jetbrains_powershell_noprofile | true |
| jetbrains_powershell_script_code | echo "step 1" |
| jetbrains_powershell_script_mode | CODE |
| teamcity.step.mode | default |

</details>

## Project: Sub-Juice Shop2 (`JuiceShop_SubJuiceShop2`)

### Build Configuration: Sub-Build (`JuiceShop_SubJuiceShop2_SubBuild`)

### VCS Roots

- **Name:** https://github.com/juice-shop/juice-shop.git#refs/heads/master  
  - **Fetch URL:** `https://github.com/juice-shop/juice-shop.git`  
  - **Default Branch:** `refs/heads/master`

### Parameters

### Triggers

- **Type:** vcsTrigger
  - branchFilter: +:*
  - enableQueueOptimization: true
  - quietPeriodMode: DO_NOT_USE

### Build Steps

<details>
<summary>Step: Step 1 (jetbrains_powershell)</summary>

**Executes:**
```
echo "step 1"
```

| Property | Value |
|---|---|
| jetbrains_powershell_execution | PS1 |
| jetbrains_powershell_noprofile | true |
| jetbrains_powershell_script_code | echo "step 1" |
| jetbrains_powershell_script_mode | CODE |
| teamcity.step.mode | default |

</details>

