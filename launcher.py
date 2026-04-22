"""
WEBINAR DEMO: Launch 50 multichannel campaigns in Salesforge via MCP.
Run this BEFORE the webinar to pre-create all sequences.
During the webinar, just show the Salesforge dashboard with 50 sequences in DRAFT.

Usage: python3 launch-50-campaigns.py --key YOUR_API_KEY --workspace WORKSPACE_ID
"""

import os
import re
import json
import time
import requests
import argparse
import csv

BASE = "https://multichannel-api.salesforge.ai/public/multichannel"
CORE = "https://api.salesforge.ai/public/v2"
DELAY = 2  # seconds between API calls

def api(method, url, headers, data=None):
    for attempt in range(3):
        try:
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                r = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == "PUT":
                r = requests.put(url, headers=headers, json=data, timeout=30)
            elif method == "PATCH":
                r = requests.patch(url, headers=headers, json=data, timeout=30)
            if r.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f" [429, waiting {wait}s]", end="", flush=True)
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json() if r.text else {}
        except Exception as e:
            if attempt < 2:
                time.sleep(3)
                continue
            print(f" ERROR: {e}")
            return None
    return None


def get_last_branch(headers, wks, seq):
    data = api("GET", f"{BASE}/workspaces/{wks}/sequences/{seq}/branches?limit=100", headers)
    branches = data.get("branches", [])
    for b in branches:
        if b.get("toNodeId") is None:
            return b["id"]
    return branches[-1]["id"] if branches else None


def create_campaign(headers, wks, campaign_file, campaign_num):
    """Create one multichannel sequence from a campaign file."""

    with open(campaign_file) as f:
        content = f.read()

    # Extract campaign name from first line
    name_match = re.search(r'# Campaign (\d+) — MULTICHANNEL — (.+)', content)
    if not name_match:
        print(f"  SKIP: can't parse {campaign_file}")
        return None

    campaign_name = f"Webinar Demo {campaign_num:02d} — {name_match.group(2)}"

    # Parse steps
    steps = []
    step_blocks = re.split(r'--- STEP \d+:', content)

    for block in step_blocks[1:]:  # skip header
        lines = block.strip().split('\n')
        header = lines[0].strip()

        if 'EMAIL' in header and 'FOLLOW' not in header:
            subject = ""
            body = ""
            for line in lines[1:]:
                if line.startswith('Subject:'):
                    subject = line.replace('Subject:', '').strip()
                elif line.startswith('Body:'):
                    body = line.replace('Body:', '').strip()
            wait = 0 if 'Day 0' in header else 3
            steps.append({"type": "email", "subject": subject, "message": f"<p>{body}</p>", "wait": wait})

        elif 'EMAIL FOLLOW' in header:
            body = ""
            for line in lines[1:]:
                if line.startswith('Subject:'):
                    subject = line.replace('Subject:', '').strip()
                elif line.startswith('Body:'):
                    body = line.replace('Body:', '').strip()
            steps.append({"type": "email", "subject": subject, "message": f"<p>{body}</p>", "wait": 3})

        elif 'VIEW PROFILE' in header:
            steps.append({"type": "linkedin_view", "wait": 1})

        elif 'CONNECTION REQUEST' in header:
            msg = ""
            for line in lines[1:]:
                if line.startswith('Message:'):
                    msg = line.replace('Message:', '').strip()
            steps.append({"type": "linkedin_connect", "message": msg, "wait": 1})

        elif 'LINKEDIN MESSAGE' in header and 'FOLLOW' not in header:
            msg = ""
            for line in lines[1:]:
                if line.startswith('Message:'):
                    msg = line.replace('Message:', '').strip()
            steps.append({"type": "linkedin_message", "message": msg, "wait": 2})

        elif 'FOLLOW-UP' in header:
            msg = ""
            for line in lines[1:]:
                if line.startswith('Message:'):
                    msg = line.replace('Message:', '').strip()
            steps.append({"type": "linkedin_message", "message": msg, "wait": 3})

    if not steps:
        print(f"  SKIP: no steps parsed from {campaign_file}")
        return None

    # 1. Create sequence
    seq_data = api("POST", f"{BASE}/workspaces/{wks}/sequences", headers, {
        "name": campaign_name, "timezone": "America/New_York"
    })
    if not seq_data:
        return None

    seq_id = seq_data["id"]
    print(f"  Seq {seq_id} created", end="", flush=True)
    time.sleep(DELAY)

    # 2. Create nodes with branch chaining
    action_map = {"email": 3, "linkedin_view": 4, "linkedin_connect": 1, "linkedin_message": 2}

    for i, step in enumerate(steps):
        branch_id = get_last_branch(headers, wks, seq_id)
        if not branch_id:
            print(f" ERROR: no branch for step {i+1}")
            break

        action_id = action_map.get(step["type"])
        node_data = {
            "actionId": action_id,
            "branchId": branch_id,
            "waitDays": step.get("wait", 0),
        }

        if step["type"] in ("email",):
            node_data["distributionStrategy"] = "equal"
            node_data["variants"] = [{
                "isEnabled": True,
                "exposureInPercentage": 100,
                "metadata": {
                    "name": "Variant A",
                    "subject": step.get("subject", ""),
                    "message": step.get("message", "")
                }
            }]
        elif step["type"] in ("linkedin_connect", "linkedin_message"):
            node_data["distributionStrategy"] = "equal"
            node_data["variants"] = [{
                "isEnabled": True,
                "exposureInPercentage": 100,
                "metadata": {
                    "name": "Variant A",
                    "message": step.get("message", "")
                }
            }]

        result = api("POST", f"{BASE}/workspaces/{wks}/sequences/{seq_id}/nodes/actions", headers, node_data)
        if result:
            print(f" → step {i+1}", end="", flush=True)
        time.sleep(DELAY)

    # 3. Set schedule
    api("PUT", f"{BASE}/workspaces/{wks}/sequences/{seq_id}/schedule", headers, {
        "timezone": "America/New_York",
        "schedule": {
            "monday": {"enabled": True, "from": 8, "to": 17},
            "tuesday": {"enabled": True, "from": 8, "to": 17},
            "wednesday": {"enabled": True, "from": 8, "to": 17},
            "thursday": {"enabled": True, "from": 8, "to": 17},
            "friday": {"enabled": True, "from": 8, "to": 17},
            "saturday": {"enabled": False, "from": 0, "to": 23},
            "sunday": {"enabled": False, "from": 0, "to": 23},
        }
    })

    # 4. Set settings
    api("PATCH", f"{BASE}/workspaces/{wks}/sequences/{seq_id}/settings", headers, {
        "plainTextEmailsEnabled": True,
        "openTrackingEnabled": False,
        "optOutLinkEnabled": False,
        "optOutTextEnabled": False,
    })

    print(f" DONE")
    return seq_id


def attach_senders_and_enroll(headers, wks, sender_profile_id, created_sequences):
    """Attach sender profiles and enroll contacts to all created sequences."""

    # Get all contacts in workspace
    print("\n--- Attaching senders + enrolling contacts ---\n")
    print("Fetching contacts...")
    contacts = []
    offset = 0
    while True:
        data = api("GET", f"{CORE}/workspaces/{wks}/contacts?limit=100&offset={offset}", headers)
        if not data or not data.get("data"):
            break
        contacts.extend(data["data"])
        if len(data["data"]) < 100:
            break
        offset += 100

    lead_ids = [c["id"] for c in contacts]
    print(f"Found {len(lead_ids)} contacts to enroll")

    if not lead_ids:
        print("WARNING: No contacts found. Skipping enrollment.")
        return

    success = 0
    for item in created_sequences:
        seq_id = item["sequence_id"]
        fname = item["file"]
        print(f"  [{seq_id}] {fname[:40]}...", end="", flush=True)

        # Attach sender
        result = api("POST", f"{BASE}/workspaces/{wks}/sequences/{seq_id}/sender-profiles", headers, {
            "senderProfileIds": [sender_profile_id]
        })
        if result:
            print(f" sender OK", end="", flush=True)
        time.sleep(DELAY)

        # Enroll contacts
        result = api("POST", f"{BASE}/workspaces/{wks}/sequences/{seq_id}/enrollments", headers, {
            "filters": {"leadIds": lead_ids},
            "limit": len(lead_ids)
        })
        if result:
            enrolled = len(result.get("leadIds", []))
            print(f" enrolled {enrolled}", end="", flush=True)
            success += 1
        time.sleep(DELAY)

        print(" DONE")

    print(f"\nSenders + contacts: {success}/{len(created_sequences)} sequences ready")


def main():
    parser = argparse.ArgumentParser(description="Launch multichannel campaigns in Salesforge")
    parser.add_argument("--key", required=True, help="Salesforge API key")
    parser.add_argument("--workspace", required=True, help="Workspace ID")
    parser.add_argument("--sender-profile-id", type=int, default=None, help="Sender profile ID to attach (auto-detects if not set)")
    parser.add_argument("--limit", type=int, default=50, help="Max campaigns to create")
    parser.add_argument("--start", type=int, default=1, help="Start from campaign N")
    parser.add_argument("--campaigns-dir", default=None, help="Path to campaign files (default: ./campaigns/)")
    args = parser.parse_args()

    headers = {"Authorization": args.key, "Content-Type": "application/json", "Accept": "application/json"}
    wks = args.workspace

    # Validate
    me = api("GET", f"{CORE}/me", headers)
    if not me:
        print("ERROR: API key invalid")
        return
    print(f"Connected: {me.get('apiKeyName', 'unknown')}")

    # Auto-detect sender profile if not provided
    sender_id = args.sender_profile_id
    if not sender_id:
        print("Detecting sender profiles...")
        profiles = api("GET", f"{BASE}/workspaces/{wks}/sender-profiles?limit=100", headers)
        if profiles and profiles.get("profiles"):
            sender_id = profiles["profiles"][0]["id"]
            sender_name = profiles["profiles"][0].get("name", "unknown")
            print(f"Using sender profile: {sender_name} (ID: {sender_id})")
        else:
            print("WARNING: No sender profiles found. Sequences will be created without senders.")

    # Find campaign files
    campaigns_dir = args.campaigns_dir or (os.path.dirname(os.path.abspath(__file__)) + "/campaigns")
    if not os.path.exists(campaigns_dir):
        print(f"ERROR: campaigns directory not found: {campaigns_dir}")
        print("Create a 'campaigns/' folder with .txt campaign files. See examples/ for format.")
        return

    files = sorted([f for f in os.listdir(campaigns_dir) if f.endswith('.txt')])
    files = files[args.start - 1:args.limit]

    if not files:
        print(f"ERROR: No .txt campaign files found in {campaigns_dir}")
        return

    print(f"\n{'='*60}")
    print(f"LAUNCHING {len(files)} MULTICHANNEL SEQUENCES")
    print(f"{'='*60}\n")

    # Phase 1: Create all sequences
    created = []
    for i, f in enumerate(files):
        num = i + args.start
        filepath = os.path.join(campaigns_dir, f)
        print(f"[{num:02d}/{len(files)}] {f}", end="", flush=True)
        seq_id = create_campaign(headers, wks, filepath, num)
        if seq_id:
            created.append({"file": f, "sequence_id": seq_id})
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"PHASE 1 DONE: {len(created)}/{len(files)} sequences created in DRAFT")
    print(f"{'='*60}")

    # Phase 2: Attach senders + enroll contacts
    if created and sender_id:
        attach_senders_and_enroll(headers, wks, sender_id, created)

    print(f"\n{'='*60}")
    print(f"ALL DONE: {len(created)} sequences ready in DRAFT")
    print(f"Senders: {'attached' if sender_id else 'NONE — add manually'}")
    print(f"Contacts: enrolled")
    print(f"Status: DRAFT — launch manually in Salesforge dashboard")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
