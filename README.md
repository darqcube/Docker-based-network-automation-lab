
# Docker-based Network Automation Lab — Infrahub + Nornir + PyATS + TextFSM

## Overview
This project provides a Docker-based lab for automated network configuration and verification. It integrates seven main components:

- **Infrahub (OpsMills):** Stores network inventory (IP addresses, device parameters).
- **Nornir + Netmiko + Jinja2 + TextFSM:** Automated configuration generation and Deploys configs, parses output for instant checks.
- **PyATS + TextFSM:** Post-deployment verification and instant checks using TextFSM parsing.

**One-command pipeline in VS Code with Dev Containers support.**

## Architecture
The solution uses three containers:

| Service   | Port  | Role                                      |
|-----------|-------|-------------------------------------------|
| Infrahub  | 8000  | Inventory API                             |
| PyATS     | 5000  | Trigger server for post-deploy verification|
| Nornir    | —     | Deployment engine                         |

All containers share the `shared_data` volume for configs, logs, and results.

## Workflow
1. **Start Infrahub** (port 8000)
2. **Start PyATS trigger server** (port 5000)
3. **Run Nornir deployment**:
    - Pulls device data from Infrahub
    - Generates configs using Jinja2 templates
    - Deploys configs to devices via Netmiko
    - Runs instant Huawei check (TextFSM parsing)
    - Triggers PyATS full verification

### Sequence
```
docker-compose up --build
```
This will build and start all services. Nornir will automatically run the deployment workflow.

## Results

- **Instant check:** `shared_data/configs/<device>_instant_check.json`
- **PyATS raw output:** `shared_data/results/pyats_raw.json`
- **PyATS parsed output:** `shared_data/results/pyats_parsed.json`

## Requirements

Python dependencies are managed per container:

- `requirements.nornir.txt` — Nornir, Netmiko, Jinja2, TextFSM, etc.
- `requirements.pyats.txt` — PyATS, Genie, Flask, TextFSM, etc.

## Usage

1. **Build and start all containers:**
    ```bash
    docker-compose up --build
    ```
2. **Infrahub** exposes inventory API at `http://localhost:8000/api/devices`
3. **Nornir** pulls inventory, generates configs, deploys, and triggers checks
4. **PyATS** server listens for triggers and runs verification

## Customization

- **Templates:** Edit Jinja2 templates in `workflow/templates/` for custom configs
- **TextFSM:** Add/modify parsing templates in `workflow/textfsm_templates/`
- **Inventory:** Infrahub API can be extended for more device parameters

## Troubleshooting

- Check logs in `shared_data/logs/`
- Inspect results in `shared_data/configs/` and `shared_data/results/`
- For issues, rebuild containers: `docker-compose build --no-cache`

## References

- [Infrahub OpsMills](https://opsmills.com/infrahub)
- [Nornir](https://nornir.readthedocs.io/en/latest/)
- [PyATS](https://developer.cisco.com/pyats/)

---
**Author:** Salman Khan