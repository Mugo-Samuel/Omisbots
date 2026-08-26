import json
import os
import re
from datetime import datetime
from urllib.parse import urlparse

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

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

DEFAULT_STORE_PATH = os.path.join(os.path.dirname(__file__), "data", "omisbots_bots.json")
DEFAULT_USERS_PATH = os.path.join(os.path.dirname(__file__), "data", "omisbots_users.json")


def get_store_path():
    return os.getenv("OMISBOTS_STORE_PATH", DEFAULT_STORE_PATH)


def get_users_path():
    return os.getenv("OMISBOTS_USERS_PATH", DEFAULT_USERS_PATH)


def load_users():
    users_path = get_users_path()
    if not os.path.exists(users_path):
        return []

    try:
        with open(users_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return []

    return payload if isinstance(payload, list) else []


def save_users(users):
    users_path = get_users_path()
    directory = os.path.dirname(users_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(users_path, "w", encoding="utf-8") as handle:
        json.dump(users, handle, indent=2)


def current_user():
    email = session.get("user_email")
    if not email:
        return None
    return next((user for user in load_users() if user["email"] == email), None)


@app.before_request
def require_authentication():
    if request.path.startswith("/dashboard") and current_user() is None:
        return redirect(url_for("auth", next=request.path))
    if request.path.startswith(("/api/agents", "/api/bot-template")) and current_user() is None:
        return jsonify({"error": "Authentication required."}), 401


def load_bots(initial_bots):
    store_path = get_store_path()
    if not os.path.exists(store_path):
        return list(initial_bots)

    try:
        with open(store_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return list(initial_bots)

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict) and isinstance(payload.get("bots"), list):
        return payload["bots"]

    return list(initial_bots)


def save_bots():
    store_path = get_store_path()
    directory = os.path.dirname(store_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(store_path, "w", encoding="utf-8") as handle:
        json.dump(BOT_STORAGE, handle, indent=2)


def build_bot_template(website):
    parsed = urlparse(website if "//" in website else f"https://{website}")
    hostname = (parsed.hostname or "").lower()
    if (
        parsed.scheme not in {"http", "https"}
        or not hostname
        or not re.fullmatch(r"[a-zA-Z0-9.-]+", hostname)
    ):
        return None

    business_name = re.sub(
        r"[^a-zA-Z0-9]+",
        " ",
        hostname.removeprefix("www.").split(".")[0],
    ).strip()
    for suffix in ("clinic", "hospital", "school", "academy", "support"):
        if business_name.lower().endswith(suffix) and len(business_name) > len(suffix):
            business_name = f"{business_name[:-len(suffix)]} {suffix}"
            break
    business_name = business_name.title() or "Website"
    website_text = f"{hostname} {parsed.path}".lower()

    template = BOT_TEMPLATES[0]
    if any(word in website_text for word in ("hospital", "clinic", "health", "medical")):
        template = next(item for item in BOT_TEMPLATES if item["id"] == "hospital")
    elif any(word in website_text for word in ("school", "academy", "college", "university")):
        template = next(item for item in BOT_TEMPLATES if item["id"] == "school")
    elif any(word in website_text for word in ("support", "help", "service")):
        template = next(item for item in BOT_TEMPLATES if item["id"] == "support")

    return {
        "name": f"{business_name} Assistant",
        "template": template["name"],
        "description": template["description"],
        "website": parsed.geturl(),
    }


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
    {
        "title": "Connect business profile",
        "detail": "Add your website, brand, and contact details.",
        "done": True,
    },
    {
        "title": "Choose bot template",
        "detail": "Select a template aligned to sales, support, education, or healthcare.",
        "done": True,
    },
    {
        "title": "Train the bot",
        "detail": "Add common FAQs, service lines, and typical customer questions.",
        "done": False,
    },
    {
        "title": "Set lead routing",
        "detail": "Send qualified conversations to your CRM or team inbox.",
        "done": False,
    },
    {
        "title": "Go live",
        "detail": "Publish the bot to your website, WhatsApp, or chatbot channels.",
        "done": False,
    },
]


PRICING_PLANS = [
    {
        "name": "Starter",
        "price": "$29",
        "description": "For solo founders and small service businesses.",
        "features": [
            "1 bot",
            "Basic analytics",
            "Email support",
            "Lead capture",
        ],
    },
    {
        "name": "Growth",
        "price": "$79",
        "description": "For teams scaling website and WhatsApp automation.",
        "features": [
            "Unlimited bots",
            "Advanced analytics",
            "Lead routing",
            "Priority support",
        ],
        "highlight": True,
    },
    {
        "name": "Enterprise",
        "price": "$199",
        "description": "For agencies and larger businesses with custom workflows.",
        "features": [
            "White-label branding",
            "Custom integrations",
            "Team workspaces",
            "Dedicated onboarding",
        ],
    },
]


WORKSPACE_MEMBERS = [
    {
        "name": "Mugo Samuel",
        "role": "Owner",
        "email": "mugo@omisbots.com",
        "status": "Online",
        "access": "Full",
    },
    {
        "name": "Alicia Njeri",
        "role": "Operations Lead",
        "email": "alicia@omisbots.com",
        "status": "In meeting",
        "access": "Team",
    },
    {
        "name": "Kofi Mensah",
        "role": "Sales Manager",
        "email": "kofi@omisbots.com",
        "status": "Online",
        "access": "Team",
    },
    {
        "name": "Nadia Kibet",
        "role": "Support Specialist",
        "email": "nadia@omisbots.com",
        "status": "Away",
        "access": "View",
    },
]


BILLING_INVOICES = [
    {
        "id": "INV-1042",
        "date": "2026-08-15",
        "client": "Northview Clinic",
        "amount": "$79.00",
        "status": "Paid",
    },
    {
        "id": "INV-1043",
        "date": "2026-08-18",
        "client": "CareDesk",
        "amount": "$29.00",
        "status": "Pending",
    },
    {
        "id": "INV-1044",
        "date": "2026-08-20",
        "client": "Bright Academy",
        "amount": "$199.00",
        "status": "Draft",
    },
]


DEPLOYMENT_CHANNELS = [
    {
        "name": "Website widget",
        "status": "Live",
        "channel": "Embedded",
        "traffic": "2.4k visits",
    },
    {
        "name": "WhatsApp flow",
        "status": "Live",
        "channel": "Messaging",
        "traffic": "840 messages",
    },
    {
        "name": "Telegram bot",
        "status": "Draft",
        "channel": "Messaging",
        "traffic": "Not launched",
    },
    {
        "name": "Instagram DM",
        "status": "Queued",
        "channel": "Social",
        "traffic": "Pilot stage",
    },
]


AUTOMATION_WORKFLOWS = [
    {
        "name": "Lead handoff",
        "trigger": "New lead captured",
        "action": "Send to CRM and notify sales",
        "status": "Enabled",
    },
    {
        "name": "Support escalation",
        "trigger": "High-priority complaint",
        "action": "Alert support and assign ticket",
        "status": "Enabled",
    },
    {
        "name": "Review follow-up",
        "trigger": "Conversation ends",
        "action": "Send summary and next-step prompt",
        "status": "Draft",
    },
]


INTEGRATION_CONNECTORS = [
    {
        "name": "HubSpot CRM",
        "status": "Connected",
        "type": "CRM",
        "details": "Sync leads and deal stages in real time.",
    },
    {
        "name": "Google Sheets",
        "status": "Connected",
        "type": "Sheets",
        "details": "Export customer conversations and metrics.",
    },
    {
        "name": "WhatsApp Business",
        "status": "Pending",
        "type": "Messaging",
        "details": "Enable outbound messages and quick replies.",
    },
    {
        "name": "Zapier",
        "status": "Connected",
        "type": "Automation",
        "details": "Trigger external actions from lead events.",
    },
    {
        "name": "Stripe",
        "status": "Draft",
        "type": "Billing",
        "details": "Prepare recurring billing for premium packages.",
    },
]

AGENT_STORAGE = []
AUTOMATION_STORAGE = []
AGENT_TEMPLATES = [
    {"id": "email-assistant", "name": "Email Assistant", "category": "Email", "description": "Reads, prioritizes, summarizes, and drafts replies for incoming email.", "tools": ["Gmail", "CRM", "WhatsApp"], "autonomy": "Ask before sending"},
    {"id": "lead-qualification", "name": "Lead Qualification Agent", "category": "Sales", "description": "Qualifies new leads, updates your CRM, and alerts your team.", "tools": ["CRM", "WhatsApp"], "autonomy": "Ask before sending"},
    {"id": "support-agent", "name": "Customer Support Agent", "category": "Support", "description": "Classifies support requests and prepares helpful next actions.", "tools": ["Knowledge base", "CRM"], "autonomy": "Draft only"},
]

CAMPAIGNS_DATA = [
    {
        "name": "Website lead nurture",
        "audience": "Visitors from product pages",
        "status": "Running",
        "open_rate": "48%",
        "click_rate": "9.6%",
        "budget": "$320",
    },
    {
        "name": "Support follow-up",
        "audience": "Recent support conversations",
        "status": "Scheduled",
        "open_rate": "41%",
        "click_rate": "7.2%",
        "budget": "$180",
    },
    {
        "name": "Education admissions push",
        "audience": "Parents and guardians",
        "status": "Draft",
        "open_rate": "36%",
        "click_rate": "6.1%",
        "budget": "$240",
    },
]


REPORTS_DATA = [
    {
        "label": "Pipeline value",
        "value": "$84.2k",
        "change": "+14.3%",
        "period": "vs last month",
    },
    {
        "label": "Qualified leads",
        "value": "214",
        "change": "+22.1%",
        "period": "this month",
    },
    {
        "label": "Bot conversion",
        "value": "18.4%",
        "change": "+3.2%",
        "period": "from last cycle",
    },
    {
        "label": "Avg. reply time",
        "value": "1.8 min",
        "change": "-26 sec",
        "period": "last 7 days",
    },
]


CONTENT_LIBRARY = [
    {
        "title": "Welcome message",
        "type": "Bot script",
        "status": "Published",
        "summary": "Warm greeting and service overview for new website visitors.",
    },
    {
        "title": "Lead qualification flow",
        "type": "Automation",
        "status": "Draft",
        "summary": "Collects names, needs, and urgency before routing to sales.",
    },
    {
        "title": "Billing reminder",
        "type": "Message",
        "status": "Scheduled",
        "summary": "Friendly reminder that helps reduce late renewals and churn.",
    },
    {
        "title": "Support triage prompt",
        "type": "Bot script",
        "status": "Published",
        "summary": "Directs customers into the correct issue category with clear follow-up.",
    },
]


TASKS_DATA = [
    {
        "title": "Review website onboarding flow",
        "owner": "Mugo",
        "due": "Today",
        "priority": "High",
        "status": "In progress",
    },
    {
        "title": "Prepare sales follow-up sequence",
        "owner": "Alicia",
        "due": "Tomorrow",
        "priority": "Medium",
        "status": "Queued",
    },
    {
        "title": "Sync customer notes to CRM",
        "owner": "Kofi",
        "due": "Friday",
        "priority": "Low",
        "status": "Planned",
    },
    {
        "title": "Confirm billing update for Growth plan",
        "owner": "Nadia",
        "due": "Next week",
        "priority": "High",
        "status": "Blocked",
    },
]


ACTIVITY_FEED = [
    {
        "event": "New lead captured",
        "detail": "Northview Clinic booked a discovery call through the sales bot.",
        "time": "2 minutes ago",
    },
    {
        "event": "Bot published",
        "detail": "CareDesk Support was updated and is ready for internal testing.",
        "time": "18 minutes ago",
    },
    {
        "event": "Campaign launched",
        "detail": "Website lead nurture went live for product-page visitors.",
        "time": "1 hour ago",
    },
    {
        "event": "Payment reminder",
        "detail": "A renewal reminder was scheduled for Bright Academy.",
        "time": "3 hours ago",
    },
]


CUSTOMER_ACCOUNTS = [
    {
        "name": "Northview Clinic",
        "plan": "Growth",
        "status": "Active",
        "owner": "Mugo Samuel",
        "health": "Healthy",
        "last_seen": "2h ago",
        "value": "$1,980/mo",
    },
    {
        "name": "CareDesk",
        "plan": "Starter",
        "status": "Trial",
        "owner": "Alicia Njeri",
        "health": "At risk",
        "last_seen": "1d ago",
        "value": "$490/mo",
    },
    {
        "name": "Bright Academy",
        "plan": "Enterprise",
        "status": "Active",
        "owner": "Kofi Mensah",
        "health": "Healthy",
        "last_seen": "4h ago",
        "value": "$4,200/mo",
    },
    {
        "name": "Harbor Retail",
        "plan": "Growth",
        "status": "Paused",
        "owner": "Nadia Kibet",
        "health": "Needs review",
        "last_seen": "6d ago",
        "value": "$1,240/mo",
    },
]


def get_bot_by_id(bot_id: str):
    for bot in BOT_STORAGE:
        if bot["id"] == bot_id:
            return bot

    return None


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/version")
def version():
    return jsonify(
        {
            "version": "OMISBOTS-2026-08-23-01",
            "message": "This is the latest deployment",
        }
    )


@app.route("/auth", methods=["GET", "POST"])
def auth():
    mode = request.args.get("mode", "login")
    next_url = request.args.get("next", url_for("dashboard"))
    error = None

    if request.method == "POST":
        mode = request.form.get("mode", "login")
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        users = load_users()
        existing_user = next((user for user in users if user["email"] == email), None)

        if not email or "@" not in email or not password:
            error = "Enter a valid email and password."
        elif mode == "signup" and not name:
            error = "Enter your name to create an account."
        elif mode == "signup" and existing_user:
            error = "An account with that email already exists. Log in instead."
        elif mode == "login" and (not existing_user or not check_password_hash(existing_user["password"], password)):
            error = "That email and password do not match."
        else:
            if mode == "signup":
                existing_user = {"name": name, "email": email, "password": generate_password_hash(password)}
                users.append(existing_user)
                save_users(users)
            session["user_email"] = email
            return redirect(next_url if next_url.startswith("/") else url_for("dashboard"))

    return render_template("auth.html", mode=mode, error=error, next_url=next_url)


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.get("/dashboard")
def dashboard():
    stats = {
        "bots": len(BOT_STORAGE),
        "responses": sum(bot["responses"] for bot in BOT_STORAGE),
        "live": sum(1 for bot in BOT_STORAGE if bot["status"] == "Live"),
        "leads": len(LEADS_STORAGE),
    }

    return render_template(
        "dashboard.html",
        bots=BOT_STORAGE,
        templates=BOT_TEMPLATES,
        stats=stats,
    )


@app.get("/dashboard/leads")
def leads_page():
    return render_template("leads.html", leads=LEADS_STORAGE)


@app.get("/dashboard/conversations")
def conversations_page():
    return render_template(
        "conversations.html",
        conversations=CONVERSATIONS_STORAGE,
    )


@app.get("/dashboard/analytics")
def analytics_page():
    return render_template(
        "analytics.html",
        analytics=ANALYTICS_DATA,
    )


@app.get("/dashboard/knowledge-base")
def knowledge_base_page():
    return render_template(
        "knowledge_base.html",
        knowledge=KNOWLEDGE_BASE,
    )


@app.get("/dashboard/settings")
def settings_page():
    return render_template("settings.html")


@app.get("/dashboard/onboarding")
def onboarding_page():
    return render_template(
        "onboarding.html",
        checklist=ONBOARDING_CHECKLIST,
    )


@app.get("/dashboard/pricing")
def pricing_page():
    return render_template(
        "pricing.html",
        plans=PRICING_PLANS,
    )


@app.get("/dashboard/workspace")
def workspace_page():
    return render_template(
        "workspace.html",
        members=WORKSPACE_MEMBERS,
    )


@app.get("/dashboard/billing")
def billing_page():
    return render_template(
        "billing.html",
        invoices=BILLING_INVOICES,
    )


@app.get("/dashboard/deployments")
def deployments_page():
    return render_template(
        "deployments.html",
        channels=DEPLOYMENT_CHANNELS,
    )


@app.get("/dashboard/automations")
def automations_page():
    return render_template(
        "automations.html",
        workflows=AUTOMATION_WORKFLOWS,
    )


@app.get("/dashboard/agents")
def agents_page():
    return render_template("agents.html", agents=AGENT_STORAGE, templates=AGENT_TEMPLATES)


@app.post("/dashboard/agents/create")
def create_agent():
    request_text = (request.form.get("request") or "").strip()
    template_id = request.form.get("template") or "custom-agent"
    template = next((item for item in AGENT_TEMPLATES if item["id"] == template_id), None)
    name = "Email Assistant" if "email" in request_text.lower() else (template["name"] if template else "Custom AI Agent")
    tools = template["tools"] if template else ["Knowledge base"]
    agent = {
        "id": f"agent-{len(AGENT_STORAGE) + 1:04d}",
        "name": name,
        "purpose": request_text or (template["description"] if template else "Complete an authorized business workflow."),
        "status": "Draft",
        "trigger": "New authorized event",
        "tools": tools,
        "memory": True,
        "autonomy": template["autonomy"] if template else "Ask before sending",
        "permissions": {"read": True, "draft": True, "send": False},
        "execution_count": 0,
        "success_rate": "Not run",
        "activity": [],
    }
    AGENT_STORAGE.insert(0, agent)
    return redirect(url_for("agent_detail", agent_id=agent["id"]))


@app.get("/dashboard/agents/<agent_id>")
def agent_detail(agent_id: str):
    agent = next((item for item in AGENT_STORAGE if item["id"] == agent_id), None)
    if not agent:
        return "Agent not found", 404
    return render_template("agent_detail.html", agent=agent)


@app.get("/dashboard/reports")
def reports_page():
    return render_template(
        "reports.html",
        reports=REPORTS_DATA,
    )


@app.get("/dashboard/content")
def content_page():
    return render_template(
        "content.html",
        content=CONTENT_LIBRARY,
    )


@app.get("/dashboard/tasks")
def tasks_page():
    return render_template(
        "tasks.html",
        tasks=TASKS_DATA,
    )


@app.get("/dashboard/activity")
def activity_page():
    return render_template(
        "activity.html",
        feed=ACTIVITY_FEED,
    )


@app.get("/dashboard/campaigns")
def campaigns_page():
    return render_template(
        "campaigns.html",
        campaigns=CAMPAIGNS_DATA,
    )


@app.get("/dashboard/integrations")
def integrations_page():
    return render_template(
        "integrations.html",
        connectors=INTEGRATION_CONNECTORS,
    )


@app.get("/dashboard/customers")
def customers_page():
    return render_template(
        "customers.html",
        customers=CUSTOMER_ACCOUNTS,
    )


@app.get("/dashboard/bot/<bot_id>")
def bot_detail(bot_id: str):
    bot = get_bot_by_id(bot_id)

    if not bot:
        return "Bot not found", 404

    conversations = [
        {
            "question": "Do you offer WhatsApp setup?",
            "answer": "Yes, we can help with website and WhatsApp flows.",
        },
        {
            "question": "What is the onboarding timeline?",
            "answer": "Most builds are ready in 1-2 weeks.",
        },
        {
            "question": "Can you route sales leads automatically?",
            "answer": "Yes — we can notify your team when a lead is qualified.",
        },
    ]

    return render_template(
        "bot_detail.html",
        bot=bot,
        conversations=conversations,
    )


@app.post("/dashboard/create-bot")
def create_bot():
    name = (request.form.get("name") or "").strip()
    website = (request.form.get("website") or "").strip()
    template_name = (
        request.form.get("template") or "Sales Assistant"
    ).strip()

    if not name or not website:
        return jsonify(
            {"error": "Bot name and website are required."}
        ), 400

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    bot = {
        "id": f"bot-{timestamp}",
        "name": name,
        "template": template_name,
        "website": website,
        "status": "Draft",
        "responses": 0,
        "updated": "just now",
        "team": "New Team",
        "botId": f"BOT-{timestamp}",
        "intent": "Create a bot tailored to your business workflow",
    }

    BOT_STORAGE.insert(0, bot)
    save_bots()

    return redirect(
        url_for(
            "bot_detail",
            bot_id=bot["id"],
        )
    )


@app.post("/api/bot-template")
def generate_bot_template():
    payload = request.get_json(silent=True) or request.form
    website = (payload.get("website") or "").strip()
    template = build_bot_template(website)

    if not template:
        return jsonify({"error": "Enter a valid website URL, such as https://example.com."}), 400

    return jsonify({"template": template})


@app.get("/api/bots")
def list_bots():
    return jsonify({"bots": BOT_STORAGE})


@app.get("/api/agents")
def list_agents():
    return jsonify({"agents": AGENT_STORAGE, "templates": AGENT_TEMPLATES})


@app.post("/api/agents")
def create_agent_api():
    request_text = (request.get_json(silent=True) or {}).get("request", "")
    with app.test_request_context("/dashboard/agents/create", method="POST", data={"request": request_text}):
        response = create_agent()
    return jsonify({"agent": AGENT_STORAGE[0]}), 201


@app.post("/api/agents/<agent_id>/test")
def test_agent(agent_id: str):
    agent = next((item for item in AGENT_STORAGE if item["id"] == agent_id), None)
    if not agent:
        return jsonify({"error": "Agent not found."}), 404
    agent["activity"] = ["Trigger received", "Instructions evaluated", "Permissions checked", "Test completed"]
    agent["execution_count"] += 1
    agent["success_rate"] = "100%"
    return jsonify({"agent": agent, "trace": agent["activity"]})


@app.post("/api/agents/<agent_id>/deploy")
def deploy_agent(agent_id: str):
    agent = next((item for item in AGENT_STORAGE if item["id"] == agent_id), None)
    if not agent:
        return jsonify({"error": "Agent not found."}), 404
    agent["status"] = "Running"
    return jsonify({"agent": agent, "message": "Agent is ready. Connect the configured tools to enable background execution."})


@app.post("/api/agents/<agent_id>/pause")
def pause_agent(agent_id: str):
    agent = next((item for item in AGENT_STORAGE if item["id"] == agent_id), None)
    if not agent:
        return jsonify({"error": "Agent not found."}), 404
    agent["status"] = "Paused"
    return jsonify({"agent": agent})


@app.get("/api/automations")
def list_automations():
    return jsonify({"automations": AUTOMATION_STORAGE})


@app.post("/api/automations")
def create_automation():
    description = ((request.get_json(silent=True) or {}).get("description") or "").strip()
    if not description:
        return jsonify({"error": "Automation description is required."}), 400

    automation = {
        "id": f"automation-{len(AUTOMATION_STORAGE) + 1:04d}",
        "name": "Lead qualification workflow",
        "description": description,
        "status": "Draft",
        "workflow": {
            "name": "Omisbots generated workflow",
            "active": False,
            "nodes": [
                {"name": "Website Form", "type": "n8n-nodes-base.webhook", "parameters": {"path": "omisbots-lead"}},
                {"name": "AI Qualification", "type": "omisbots.ai", "parameters": {"instructions": "Qualify the incoming lead using authorized business rules."}},
                {"name": "CRM", "type": "n8n-nodes-base.httpRequest", "parameters": {"credentialReference": "CRM_CREDENTIAL"}},
                {"name": "WhatsApp Notification", "type": "n8n-nodes-base.httpRequest", "parameters": {"credentialReference": "WHATSAPP_CREDENTIAL"}},
            ],
            "connections": {"Website Form": ["AI Qualification"], "AI Qualification": ["CRM"], "CRM": ["WhatsApp Notification"]},
            "errorHandling": "Continue to error workflow and record execution log",
        },
    }
    AUTOMATION_STORAGE.insert(0, automation)
    return jsonify({"automation": automation}), 201


@app.post("/api/automations/<automation_id>/deploy")
def deploy_automation(automation_id: str):
    automation = next((item for item in AUTOMATION_STORAGE if item["id"] == automation_id), None)
    if not automation:
        return jsonify({"error": "Automation not found."}), 404
    automation["status"] = "Ready to connect"
    return jsonify({"automation": automation, "message": "Workflow generated. Configure n8n to deploy it."})


@app.post("/chat")
def chat():
    try:
        payload = request.get_json(silent=True) or {}
        user_message = (request.form.get("message") or payload.get("message") or "").strip()
        if not user_message:
            return jsonify(
                {"error": "Message is required."}
            ), 400

        return jsonify({"reply": generate_reply(user_message)})
    except Exception as error:
        return jsonify(
            {"error": f"Unexpected server error: {error}"}
        ), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
    )
