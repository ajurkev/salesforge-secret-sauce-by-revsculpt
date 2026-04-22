# Demo Prompt — Create 5 Multichannel Campaigns

Copy-paste this into a Claude Code session with Salesforge MCP connected. Replace `YOUR_API_KEY` and `YOUR_WORKSPACE_ID` with your values.

---

```
Skills from: github.com/ajurkev/salesforge-secret-sauce-by-revsculpt

Connect to Salesforge MCP with API key: YOUR_API_KEY

I need to create 5 multichannel campaigns in Salesforge.

Workspace: YOUR_WORKSPACE_ID

For each campaign:
1. Create sequence with name "Demo [N] — [Vertical] + [Trigger]"
2. Add 6 steps via branch chaining (re-fetch branches after each node):
   - Step 1: Email (actionId 3, waitDays 0) — with spintax in body
   - Step 2: Email follow-up (actionId 3, waitDays 3)
   - Step 3: LinkedIn view profile (actionId 4, waitDays 1)
   - Step 4: LinkedIn connection request (actionId 1, waitDays 1) — with personalized note
   - Step 5: LinkedIn message (actionId 2, waitDays 2)
   - Step 6: LinkedIn follow-up (actionId 2, waitDays 3)
3. Set schedule: Mon-Fri 8-17 ET, disabled days from:0 to:23
4. Settings: plainTextEmailsEnabled true, openTrackingEnabled false
5. Attach sender profile (auto-detect from workspace)
6. Sequence stays in DRAFT — never launch

Variables use {{double_braces}}: {{first_name}}, {{company}}
Spintax also uses {{double_braces}}: {{option 1 | option 2 | option 3}}

The 5 campaigns:

Campaign 1 — Healthcare + Audit Failed
Email 1 subject: {{first_name}}, {{HIPAA documentation gaps at {{company}} | HIPAA compliance risk at {{company}}}}
Email 1 body: HIPAA audit flagged a multi-clinic group. Most healthcare companies still manage this manually. We cut documentation time by 60%. Worth a quick chat?
Email 2 body: The company we worked with had the same manual processes. One failed audit later, they automated everything. Happy to share what they changed.
LinkedIn connect: {{first_name}}, I work with healthcare companies on HIPAA compliance automation. Noticed {{company}} is growing.
LinkedIn message: We built a walkthrough showing how healthcare companies automated compliance. Want me to send it over?
LinkedIn follow-up: If HIPAA is already handled, no worries. But if manual, this 15-min walkthrough has helped 20+ companies.

Campaign 2 — Construction + OSHA
Email 1 subject: {{first_name}}, {{OSHA flagged your safety records | safety documentation gaps at {{company}}}}
Email 1 body: OSHA cited a contractor for incomplete safety docs. Most still manage this on paper. We helped a similar contractor automate and no citations in 3 years. Worth 5 minutes?
Email 2 body: The $500K fine was preventable. The data existed but was scattered across folders. Automated audit trails fix this in 2 weeks.
LinkedIn connect: {{first_name}}, I work with construction companies on OSHA compliance automation. Noticed {{company}} is scaling.
LinkedIn message: We built a walkthrough showing how contractors automate safety docs and save 20+ hours/week. Want me to send it?
LinkedIn follow-up: If compliance is handled, no worries. But if your team spends more time on paperwork than jobsites, that is what we fix.

Campaign 3 — Logistics + eFTI
Email 1 subject: {{first_name}}, {{eFTI mandate and {{company}} | customs compliance at {{company}}}}
Email 1 body: eFTI mandate is approaching. Most forwarders still pass paper documents. We helped a forwarder go fully digital in 3 weeks. Worth a look?
Email 2 body: The forwarder we worked with reduced clearance time by 40% after automating customs documentation. Happy to share the playbook.
LinkedIn connect: {{first_name}}, I work with logistics companies on customs compliance automation. Noticed {{company}} is expanding.
LinkedIn message: We built a walkthrough on automating freight documentation. Want me to send it over?
LinkedIn follow-up: If eFTI compliance is sorted, no worries. But if your team is still assembling docs manually, this walkthrough helps.

Campaign 4 — Manufacturing + Recall
Email 1 subject: {{first_name}}, {{competitor recalled 50K units | traceability gaps at {{company}}}}
Email 1 body: A manufacturer recalled 50K units because they could not trace a defective batch. Most cannot trace in under an hour. We automate this. Worth a look?
Email 2 body: Our client traces any batch in under 5 minutes — automated from receipt to shipment. Happy to show you how it works for {{company}}.
LinkedIn connect: {{first_name}}, I work with manufacturers on product traceability automation. Noticed {{company}} is growing.
LinkedIn message: We built a walkthrough on batch traceability automation. Want me to send it over?
LinkedIn follow-up: If traceability is automated, ignore this. But if your team would struggle to trace a batch in under an hour, that is the gap we close.

Campaign 5 — Food & Bev + FDA
Email 1 subject: {{first_name}}, {{FDA inspection found gaps | FSMA 204 traceability at {{company}}}}
Email 1 body: FDA flagged traceability gaps at a food company. FSMA 204 requires electronic farm-to-fork tracking. We automated this for a client across 4 facilities in 3 weeks. Relevant for {{company}}?
Email 2 body: The food company we worked with passed their next FDA inspection with zero observations after automating. Happy to share what they changed.
LinkedIn connect: {{first_name}}, I work with food companies on FDA compliance automation. Noticed {{company}} is scaling.
LinkedIn message: We built a walkthrough on FSMA 204 traceability automation. Want me to send it over?
LinkedIn follow-up: If traceability is handled, no worries. But if your team cannot trace a batch across facilities in under an hour, this walkthrough helps.

Create all 5 sequences now. Show me progress as you go.
```

---

## Launcher Script (10+ campaigns from files)

```bash
python3 launcher.py --key YOUR_API_KEY --workspace YOUR_WORKSPACE_ID --limit 10
```

Creates 10 multichannel sequences from campaign files in `campaigns/` folder, auto-attaches senders, enrolls contacts. ~5 minutes.
