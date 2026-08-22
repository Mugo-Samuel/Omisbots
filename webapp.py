import json
import os
from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request, url_for

from chatbot import generate_reply, is_greeting

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

BOT_TEMPLATES = [
    {
        "id": "sales",
        "name": "Sales Assistant",
        "description": "Qualifies leads and suggests the right service or product.",
        "category": "Sales",
        "color": "#8b5cf6",
    },
    {
        "id": "support",
        "name": "Customer Support",
        "description": "Answers frequent questions and routes issues to a human team.",
        "category": "Support",
        "color": "#22c55e",
    },
    {
        "id": "hospital",
        "name": "Hospital Assistant",
        "description": "Handles appointments, questions, and basic front-desk tasks.",
        "category": "Healthcare",
        "color": "#f97316",
    },
    {
        "id": "school",
        "name": "School Assistant",
        "description": "Supports admissions, timetables, and common student questions.",
        "category": "Education",
        "color": "#06b6d4",
    },
]

BOT_STORAGE = [
    {
        "id": "bot-1001",
        "name": "Milo Sales Bot",
        "template": "Sales Assistant",
        "website": "https://examplebusiness.com",
        "status": "Live",
        "responses": 248,
        "updated": "2h ago",
        "team": "Sales Team",
        "botId": "BOT-1001",
        "intent": "Qualify leads and recommend the right package",
    },
    {
        "id": "bot-1002",
        "name": "CareDesk Support",
        "template": "Customer Support",
        "website": "https://support.examplebusiness.com",
        "status": "Draft",
        "responses": 94,
        "updated": "1d ago",
        "team": "Support Team",
        "botId": "BOT-1002",
        "intent": "Answer FAQs and route issues to a human agent",
    },
]

STORE_PATH = os.getenv("OMISBOTS_STORE_PATH", os.path.join(os.path.dirname(__file__), "data", "omisbots_bots.json"))


def load_bots(initial_bots):
    if not os.path.exists(STORE_PATH):
        return list(initial_bots)

    try:
        with open(STORE_PATH, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return list(initial_bots)

    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("bots"), list):
        return payload["bots"]
    return list(initial_bots)


def save_bots():
    directory = os.path.dirname(STORE_PATH)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(STORE_PATH, "w", encoding="utf-8") as handle:
        json.dump(BOT_STORAGE, handle, indent=2)


BOT_STORAGE = load_bots(BOT_STORAGE)

LEADS_STORAGE = [
    {
        "id": "lead-001",
        "name": "Nia Patel",
        "contact": "nia@northviewclinic.com",
        "company": "Northview Clinic",
        "source": "Website",
        "bot": "Milo Sales Bot",
        "date": "2026-08-18",
        "status": "Qualified",
    },
    {
        "id": "lead-002",
        "name": "Samuel Okafor",
        "contact": "samuel@caredesk.co",
        "company": "CareDesk",
        "source": "WhatsApp",
        "bot": "CareDesk Support",
        "date": "2026-08-19",
        "status": "New",
    },
    {
        "id": "lead-003",
        "name": "Aisha Bello",
        "contact": "aisha@brightschool.edu",
        "company": "Bright Academy",
        "source": "Instagram",
        "bot": "School Assistant",
        "date": "2026-08-20",
        "status": "Contacted",
    },
    {
        "id": "lead-004",
        "name": "Daniel Grant",
        "contact": "daniel@harborretail.com",
        "company": "Harbor Retail",
        "source": "Referral",
        "bot": "Milo Sales Bot",
        "date": "2026-08-21",
        "status": "Converted",
    },
]

CONVERSATIONS_STORAGE = [
    {
        "customer": "Nia Patel",
        "bot": "Milo Sales Bot",
        "question": "Can I get a custom pricing quote for a WhatsApp-ready sales bot?",
        "sentiment": "Positive",
        "time": "2 mins ago",
    },
    {
        "customer": "Samuel Okafor",
        "bot": "CareDesk Support",
        "question": "Do you support routing support issues to a human agent?",
        "sentiment": "Neutral",
        "time": "15 mins ago",
    },
    {
        "customer": "Aisha Bello",
        "bot": "School Assistant",
        "question": "How do I set up admissions information for parents?",
        "sentiment": "Positive",
        "time": "1 hour ago",
    },
]

KNOWLEDGE_BASE = [
    {
        "title": "Pricing packages",
        "category": "Sales",
        "summary": "Explain starter, growth, and enterprise pricing for bot deployments.",
        "updated": "2 days ago",
    },
    {
        "title": "Lead qualification workflow",
        "category": "Marketing",
        "summary": "Capture contact details, score intent, and route warm leads to sales teams.",
        "updated": "1 day ago",
    },
    {
        "title": "Support handoff guidelines",
        "category": "Support",
        "summary": "Escalate complex tickets to humans with context and customer details ready.",
        "updated": "6 hours ago",
    },
]

ANALYTICS_DATA = {
    "revenue": "$24,800",
    "conversion": "18.4%",
    "response_time": "1.8 min",
    "active_bots": 2,
    "weekly_leads": [12, 18, 15, 22, 27, 21, 31],
    "channel_mix": [
        {"label": "Website", "value": 42},
        {"label": "WhatsApp", "value": 31},
        {"label": "Instagram", "value": 17},
        {"label": "Referral", "value": 10},
    ],
}

ONBOARDING_CHECKLIST = [
    {"title": "Connect business profile", "detail": "Add your website, brand, and contact details.", "done": True},
    {"title": "Choose bot template", "detail": "Select a template aligned to sales, support, education, or healthcare.", "done": True},
    {"title": "Train the bot", "detail": "Add common FAQs, service lines, and typical customer questions.", "done": False},
    {"title": "Set lead routing", "detail": "Send qualified conversations to your CRM or team inbox.", "done": False},
    {"title": "Go live", "detail": "Publish the bot to your website, WhatsApp, or chatbot channels.", "done": False},
]

PRICING_PLANS = [
    {"name": "Starter", "price": "$29", "description": "For solo founders and small service businesses.", "features": ["1 bot", "Basic analytics", "Email support", "Lead capture"]},
    {"name": "Growth", "price": "$79", "description": "For teams scaling website and WhatsApp automation.", "features": ["Unlimited bots", "Advanced analytics", "Lead routing", "Priority support"], "highlight": True},
    {"name": "Enterprise", "price": "$199", "description": "For agencies and larger businesses with custom workflows.", "features": ["White-label branding", "Custom integrations", "Team workspaces", "Dedicated onboarding"]},
]

WORKSPACE_MEMBERS = [
    {"name": "Mugo Samuel", "role": "Owner", "email": "mugo@omisbots.com", "status": "Online", "access": "Full"},
    {"name": "Alicia Njeri", "role": "Operations Lead", "email": "alicia@omisbots.com", "status": "In meeting", "access": "Team"},
    {"name": "Kofi Mensah", "role": "Sales Manager", "email": "kofi@omisbots.com", "status": "Online", "access": "Team"},
    {"name": "Nadia Kibet", "role": "Support Specialist", "email": "nadia@omisbots.com", "status": "Away", "access": "View"},
]

BILLING_INVOICES = [
    {"id": "INV-1042", "date": "2026-08-15", "client": "Northview Clinic", "amount": "$79.00", "status": "Paid"},
    {"id": "INV-1043", "date": "2026-08-18", "client": "CareDesk", "amount": "$29.00", "status": "Pending"},
    {"id": "INV-1044", "date": "2026-08-20", "client": "Bright Academy", "amount": "$199.00", "status": "Draft"},
]

DEPLOYMENT_CHANNELS = [
    {"name": "Website widget", "status": "Live", "channel": "Embedded", "traffic": "2.4k visits"},
    {"name": "WhatsApp flow", "status": "Live", "channel": "Messaging", "traffic": "840 messages"},
    {"name": "Telegram bot", "status": "Draft", "channel": "Messaging", "traffic": "Not launched"},
    {"name": "Instagram DM", "status": "Queued", "channel": "Social", "traffic": "Pilot stage"},
]

AUTOMATION_WORKFLOWS = [
    {"name": "Lead handoff", "trigger": "New lead captured", "action": "Send to CRM and notify sales", "status": "Enabled"},
    {"name": "Support escalation", "trigger": "High-priority complaint", "action": "Alert support and assign ticket", "status": "Enabled"},
    {"name": "Review follow-up", "trigger": "Conversation ends", "action": "Send summary and next-step prompt", "status": "Draft"},
]

INTEGRATION_CONNECTORS = [
    {"name": "HubSpot CRM", "status": "Connected", "type": "CRM", "details": "Sync leads and deal stages in real time."},
    {"name": "Google Sheets", "status": "Connected", "type": "Sheets", "details": "Export customer conversations and metrics."},
    {"name": "WhatsApp Business", "status": "Pending", "type": "Messaging", "details": "Enable outbound messages and quick replies."},
    {"name": "Zapier", "status": "Connected", "type": "Automation", "details": "Trigger external actions from lead events."},
    {"name": "Stripe", "status": "Draft", "type": "Billing", "details": "Prepare recurring billing for premium packages."},
]

CAMPAIGNS_DATA = [
    {"name": "Website lead nurture", "audience": "Visitors from product pages", "status": "Running", "open_rate": "48%", "click_rate": "9.6%", "budget": "$320"},
    {"name": "Support follow-up", "audience": "Recent support conversations", "status": "Scheduled", "open_rate": "41%", "click_rate": "7.2%", "budget": "$180"},
    {"name": "Education admissions push", "audience": "Parents and guardians", "status": "Draft", "open_rate": "36%", "click_rate": "6.1%", "budget": "$240"},
]

REPORTS_DATA = [
    {"label": "Pipeline value", "value": "$84.2k", "change": "+14.3%", "period": "vs last month"},
    {"label": "Qualified leads", "value": "214", "change": "+22.1%", "period": "this month"},
    {"label": "Bot conversion", "value": "18.4%", "change": "+3.2%", "period": "from last cycle"},
    {"label": "Avg. reply time", "value": "1.8 min", "change": "-26 sec", "period": "last 7 days"},
]

CONTENT_LIBRARY = [
    {"title": "Welcome message", "type": "Bot script", "status": "Published", "summary": "Warm greeting and service overview for new website visitors."},
    {"title": "Lead qualification flow", "type": "Automation", "status": "Draft", "summary": "Collects names, needs, and urgency before routing to sales."},
    {"title": "Billing reminder", "type": "Message", "status": "Scheduled", "summary": "Friendly reminder that helps reduce late renewals and churn."},
    {"title": "Support triage prompt", "type": "Bot script", "status": "Published", "summary": "Directs customers into the correct issue category with clear follow-up."},
]

TASKS_DATA = [
    {"title": "Review website onboarding flow", "owner": "Mugo", "due": "Today", "priority": "High", "status": "In progress"},
    {"title": "Prepare sales follow-up sequence", "owner": "Alicia", "due": "Tomorrow", "priority": "Medium", "status": "Queued"},
    {"title": "Sync customer notes to CRM", "owner": "Kofi", "due": "Friday", "priority": "Low", "status": "Planned"},
    {"title": "Confirm billing update for Growth plan", "owner": "Nadia", "due": "Next week", "priority": "High", "status": "Blocked"},
]

ACTIVITY_FEED = [
    {"event": "New lead captured", "detail": "Northview Clinic booked a discovery call through the sales bot.", "time": "2 minutes ago"},
    {"event": "Bot published", "detail": "CareDesk Support was updated and is ready for internal testing.", "time": "18 minutes ago"},
    {"event": "Campaign launched", "detail": "Website lead nurture went live for product-page visitors.", "time": "1 hour ago"},
    {"event": "Payment reminder", "detail": "A renewal reminder was scheduled for Bright Academy.", "time": "3 hours ago"},
]

CUSTOMER_ACCOUNTS = [
    {"name": "Northview Clinic", "plan": "Growth", "status": "Active", "owner": "Mugo Samuel", "health": "Healthy", "last_seen": "2h ago", "value": "$1,980/mo"},
    {"name": "CareDesk", "plan": "Starter", "status": "Trial", "owner": "Alicia Njeri", "health": "At risk", "last_seen": "1d ago", "value": "$490/mo"},
    {"name": "Bright Academy", "plan": "Enterprise", "status": "Active", "owner": "Kofi Mensah", "health": "Healthy", "last_seen": "4h ago", "value": "$4,200/mo"},
    {"name": "Harbor Retail", "plan": "Growth", "status": "Paused", "owner": "Nadia Kibet", "health": "Needs review", "last_seen": "6d ago", "value": "$1,240/mo"},
]


def get_bot_by_id(bot_id: str):
    for bot in BOT_STORAGE:
        if bot["id"] == bot_id:
            return bot
    return None


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/dashboard")
def dashboard():
    stats = {
        "bots": len(BOT_STORAGE),
        "responses": sum(bot["responses"] for bot in BOT_STORAGE),
        "live": sum(1 for bot in BOT_STORAGE if bot["status"] == "Live"),
        "leads": len(LEADS_STORAGE),
    }
    return render_template("dashboard.html", bots=BOT_STORAGE, templates=BOT_TEMPLATES, stats=stats)


@app.get("/dashboard/leads")
def leads_page():
    return render_template("leads.html", leads=LEADS_STORAGE)


@app.get("/dashboard/conversations")
def conversations_page():
    return render_template("conversations.html", conversations=CONVERSATIONS_STORAGE)


@app.get("/dashboard/analytics")
def analytics_page():
    return render_template("analytics.html", analytics=ANALYTICS_DATA)


@app.get("/dashboard/knowledge-base")
def knowledge_base_page():
    return render_template("knowledge_base.html", knowledge=KNOWLEDGE_BASE)


@app.get("/dashboard/settings")
def settings_page():
    return render_template("settings.html")


@app.get("/dashboard/onboarding")
def onboarding_page():
    return render_template("onboarding.html", checklist=ONBOARDING_CHECKLIST)


@app.get("/dashboard/pricing")
def pricing_page():
    return render_template("pricing.html", plans=PRICING_PLANS)


@app.get("/dashboard/workspace")
def workspace_page():
    return render_template("workspace.html", members=WORKSPACE_MEMBERS)


@app.get("/dashboard/billing")
def billing_page():
    return render_template("billing.html", invoices=BILLING_INVOICES)


@app.get("/dashboard/deployments")
def deployments_page():
    return render_template("deployments.html", channels=DEPLOYMENT_CHANNELS)


@app.get("/dashboard/automations")
def automations_page():
    return render_template("automations.html", workflows=AUTOMATION_WORKFLOWS)


@app.get("/dashboard/reports")
def reports_page():
    return render_template("reports.html", reports=REPORTS_DATA)


@app.get("/dashboard/content")
def content_page():
    return render_template("content.html", content=CONTENT_LIBRARY)


@app.get("/dashboard/tasks")
def tasks_page():
    return render_template("tasks.html", tasks=TASKS_DATA)


@app.get("/dashboard/activity")
def activity_page():
    return render_template("activity.html", feed=ACTIVITY_FEED)


@app.get("/dashboard/campaigns")
def campaigns_page():
    return render_template("campaigns.html", campaigns=CAMPAIGNS_DATA)


@app.get("/dashboard/integrations")
def integrations_page():
    return render_template("integrations.html", connectors=INTEGRATION_CONNECTORS)


@app.get("/dashboard/customers")
def customers_page():
    return render_template("customers.html", customers=CUSTOMER_ACCOUNTS)


@app.get("/dashboard/bot/<bot_id>")
def bot_detail(bot_id: str):
    bot = get_bot_by_id(bot_id)
    if not bot:
        return "Bot not found", 404

    conversations = [
        {"question": "Do you offer WhatsApp setup?", "answer": "Yes, we can help with website and WhatsApp flows."},
        {"question": "What is the onboarding timeline?", "answer": "Most builds are ready in 1-2 weeks."},
        {"question": "Can you route sales leads automatically?", "answer": "Yes — we can notify your team when a lead is qualified."},
    ]

    return render_template("bot_detail.html", bot=bot, conversations=conversations)


@app.post("/dashboard/create-bot")
def create_bot():
    name = (request.form.get("name") or "").strip()
    website = (request.form.get("website") or "").strip()
    template_name = (request.form.get("template") or "Sales Assistant").strip()

    if not name or not website:
        return jsonify({"error": "Bot name and website are required."}), 400

    bot = {
        "id": f"bot-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "name": name,
        "template": template_name,
        "website": website,
        "status": "Draft",
        "responses": 0,
        "updated": "just now",
        "team": "New Team",
        "botId": f"BOT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "intent": "Create a bot tailored to your business workflow",
    }
    BOT_STORAGE.insert(0, bot)
    save_bots()
    return redirect(url_for("bot_detail", bot_id=bot["id"]))


@app.get("/api/bots")
def list_bots():
    return jsonify({"bots": BOT_STORAGE})


@app.post("/chat")
def chat():
    try:
        user_message = (request.form.get("message") or "").strip()
        if not user_message:
            return jsonify({"error": "Message is required."}), 400

        if is_greeting(user_message):
            return jsonify({"reply": generate_reply(user_message)})

        return jsonify({"reply": generate_reply(user_message)})
    except Exception as error:
        return jsonify({"error": f"Unexpected server error: {error}"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
