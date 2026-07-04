import http.client
import json
import os
import subprocess
import platform

OLIMN_API_KEY = os.environ.get("OLIMN_API_KEY", None)
if not OLIMN_API_KEY:
    raise ValueError("Please set OLIMN_API_KEY")

def send_dict_to_olimn(stem: str, content: dict) -> dict:
    """
    Send a dict to olimn
    :param stem: e.g. "host", "game"
    :param content: e.g.
        {
            "agents": str,
            "host": str,
            "lan": str,
            "la": str 
        }
    """
    conn = http.client.HTTPConnection("olimn.com")
    json_dump = json.dumps(content)

    conn.request("POST", f"/vlanet/api/{stem}", body=json_dump, headers={"X-API-Key": OLIMN_API_KEY, "Content-Type": "application/json"})
    response = conn.getresponse()
    body = response.read()
    json_body = json.loads(body)
    if response.status >= 400:
        print(f"POST /vlanet/api/host failed: {response.status} {response.reason}\n{body.decode()}")
        raise ConnectionError(f"POST /vlanet/api/host failed: {response.status} {response.reason}\n{body.decode()}")
    return json_body