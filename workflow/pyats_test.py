# Huawei-aware + TextFSM
import os
import json
import textfsm
from genie.testbed import load

RESULTS_DIR = "/workspace/shared_data/results"
RAW_FILE = os.path.join(RESULTS_DIR, "pyats_raw.json")
PARSED_FILE = os.path.join(RESULTS_DIR, "pyats_parsed.json")
TEMPLATE_DIR = "/workspace/workflow/textfsm_templates"

HUAWEI_COMMANDS = {
    "display version": "huawei_display_version.tpl",
    "display interface brief": "huawei_display_interface.tpl",
}


def parse_with_textfsm(output, template_file):
    path = os.path.join(TEMPLATE_DIR, template_file)
    if not os.path.exists(path):
        return {"error": f"Template missing: {template_file}"}
    with open(path) as f:
        fsm = textfsm.TextFSM(f)
        return {"headers": fsm.header, "records": fsm.ParseText(output)}


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    testbed_file = "/workspace/shared_data/configs/testbed.yaml"
    if not os.path.exists(testbed_file):
        return

    tb = load(testbed_file)
    raw_results = {}
    parsed_results = {}

    for dev in tb.devices.values():
        dev.connect()
        if "vrp" in dev.os.lower() or "huawei" in dev.os.lower():
            for cmd, tpl in HUAWEI_COMMANDS.items():
                output = dev.execute(cmd)
                raw_results.setdefault(dev.name, {})[cmd] = output
                parsed_results.setdefault(dev.name, {})[cmd] = parse_with_textfsm(
                    output, tpl
                )
        else:
            output = dev.parse("show version")
            raw_results.setdefault(dev.name, {})["show version"] = output
            parsed_results.setdefault(dev.name, {})["show version"] = output
        dev.disconnect()

    with open(RAW_FILE, "w") as f:
        json.dump(raw_results, f, indent=2)
    with open(PARSED_FILE, "w") as f:
        json.dump(parsed_results, f, indent=2)


if __name__ == "__main__":
    main()
