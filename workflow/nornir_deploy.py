import os
import json
import requests
import textfsm
from nornir import InitNornir
from nornir_jinja2.plugins.tasks import template_file
from nornir_netmiko.tasks import netmiko_send_config
from rich import print

INFRAHUB_API = "http://infrahub:8000/api/devices"
PYATS_TRIGGER = "http://pyats:5000/run-tests"

SHARED_CONFIG_DIR = "/workspace/shared_data/configs"
os.makedirs(SHARED_CONFIG_DIR, exist_ok=True)


def get_inventory():
    r = requests.get(INFRAHUB_API)
    r.raise_for_status()
    devices = r.json()
    with open("/workspace/inventory.json", "w") as f:
        json.dump(devices, f, indent=2)
    return devices


def build_nornir_inventory(devices):
    import yaml

    inventory = {"hosts": {}, "groups": {}, "defaults": {}}
    for dev in devices:
        name = dev["name"]
        inventory["hosts"][name] = {
            "hostname": dev["ip"],
            "platform": dev.get("platform", "vrp"),
            "username": dev.get("username", "admin"),
            "password": dev.get("password", "admin"),
        }
    with open("/workspace/config.yaml", "w") as f:
        yaml.dump(inventory, f)


def instant_huawei_check(output, template):
    tpl_path = f"/workspace/workflow/textfsm_templates/{template}"
    if os.path.exists(tpl_path):
        with open(tpl_path) as f:
            fsm = textfsm.TextFSM(f)
            return {"headers": fsm.header, "records": fsm.ParseText(output)}
    return {"error": f"Template {template} not found"}


def deploy_configs(nr):
    results = nr.run(
        task=template_file, template="base_config.j2", path="./workflow/templates"
    )
    for host, res in results.items():
        config_text = res.result
        with open(f"{SHARED_CONFIG_DIR}/{host}_config.txt", "w") as f:
            f.write(config_text)
        nr.run(
            task=netmiko_send_config,
            config_commands=config_text.splitlines(),
            name=f"Deploy {host}",
        )
        # Quick check after deploy
        conn = nr.inventory.hosts[host].get_connection("netmiko", nr.config)
        output = conn.send_command("display version")
        parsed = instant_huawei_check(output, "huawei_display_version.tpl")
        with open(f"{SHARED_CONFIG_DIR}/{host}_instant_check.json", "w") as f:
            json.dump(parsed, f, indent=2)


def trigger_pyats():
    requests.post(PYATS_TRIGGER, json={"reason": "deployment_complete"})


if __name__ == "__main__":
    devices = get_inventory()
    build_nornir_inventory(devices)
    nr = InitNornir(config_file="config.yaml")
    deploy_configs(nr)
    trigger_pyats()
