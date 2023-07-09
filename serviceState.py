import subprocess
import json

def get_service_status(service_name):
    cmd = f"systemctl status {service_name}"
    output = subprocess.check_output(cmd.split())
    output = output.decode("utf-8")
    state = output.split("\n")[2].split(":")[1].strip()
    return {"name": service_name, "state": state}

if __name__ == "__main__":
    service_name = "recorder"
    status = get_service_status(service_name)
    with open("service_status.json", "w") as f:
        json.dump(status, f)