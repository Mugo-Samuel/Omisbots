import re

CONTACT_EMAIL = "automatebots.io@gmail.com"

GREETINGS = [
    "hi", "hi there", "hello", "hae", "hello there", "hey", "hey there", "heya",
    "hiya", "yo", "holla", "sup", "whats up", "what's up", "howdy", "greetings",
    "good morning", "good afternoon", "good evening", "morning", "evening",
    "hola", "afternoon"
]

THANKS = ["thanks", "thank you", "thx", "ty", "appreciate it", "cheers"]
BYES = ["bye", "goodbye", "see you", "later", "cya", "farewell"]

BOT_LIBRARY = {
    "support": {
        "greeting": "Hi there! I'm Ava from support. I can help with order tracking, returns, or warranty questions — what do you need?",
        "thanks": "Happy to help! Let me know if there's anything else about your order.",
        "goodbye": "Take care! Reach back out any time you need an order checked.",
        "topics": [
            {"keywords": ["track", "order", "delivery", "shipping", "late", "where is", "arrive"], "reply": "I can pull that up. Order #BF-2048 is in transit and the courier expects delivery between 3:00 PM and 5:30 PM."},
            {"keywords": ["return", "refund", "exchange", "send back"], "reply": "No problem. I can start a return for you — just confirm the order number and the reason, and I'll email a prepaid label."},
            {"keywords": ["warranty", "broken", "damaged", "defect", "not working"], "reply": "Sorry to hear that. I can open a warranty claim now — could you share a quick photo of the issue and your order number?"},
            {"keywords": ["human", "agent", "person", "someone", "representative"], "reply": "Of course, I can route this to a human agent along with a summary of our conversation. One moment."},
            {"keywords": ["cancel"], "reply": "I can help cancel an order as long as it hasn't shipped yet. What's the order number?"},
        ],
        "fallback": f"I'm Ava, a support bot — I handle order tracking, returns, and warranty claims. That question is outside what I can look up here, so please email {CONTACT_EMAIL} and our team will help directly."
    },
    "sales": {
        "greeting": "Hey! Welcome in. Tell me a bit about what you're shopping for and I'll point you to the right option.",
        "thanks": "Anytime! I'll save these details so the sales team has context when they follow up.",
        "goodbye": "Thanks for stopping by — I've saved your details and someone will follow up soon.",
        "topics": [
            {"keywords": ["whatsapp", "telegram", "website", "web", "channel"], "reply": "Good choice. I'd suggest a support and sales hybrid: FAQs, lead capture, quote requests, and handoff to your team."},
            {"keywords": ["price", "cost", "budget", "quote", "$"], "reply": "I can prepare a starter quote. Most chatbot builds range from $200 to $800 depending on scope."},
            {"keywords": ["email", "contact", "follow up", "reach out"], "reply": "Great — could you share your email and preferred launch date so the sales team can follow up?"},
            {"keywords": ["automation", "automate", "workflow", "reminder"], "reply": "We can pair the chatbot with automations for lead alerts, reminders, and CRM updates."},
            {"keywords": ["demo", "trial", "test"], "reply": "I can set up a quick demo — what's the best email to send it to?"},
        ],
        "fallback": f"I'm the sales assistant — I help with product recommendations, pricing, and lead capture. For anything outside that, email {CONTACT_EMAIL} and our team can help directly."
    },
    "hospital": {
        "greeting": "Hello! I can help with appointments, departments, visiting hours, or billing — what do you need today?",
        "thanks": "You're welcome! Let me know if you'd like anything else arranged.",
        "goodbye": "Take care, and see you at your appointment!",
        "topics": [
            {"keywords": ["appointment", "book", "booking", "schedule", "dental", "doctor", "clinic"], "reply": "I can help with that. The next available slot is tomorrow at 10:30 AM or 2:00 PM — which works better for you?"},
            {"keywords": ["visiting hours", "visit", "hours"], "reply": "Visiting hours are 9:00 AM to 8:00 PM daily. Some wards may have different rules, so let me know which department."},
            {"keywords": ["bill", "billing", "invoice", "payment", "insurance"], "reply": "I can pull up billing details if you share your patient ID, or connect you to the billing desk directly."},
            {"keywords": ["emergency", "urgent"], "reply": "For a medical emergency, please call emergency services or go to the nearest ER right away — I'm not able to handle urgent care requests here."},
            {"keywords": ["reminder", "confirm", "cancel appointment"], "reply": "I can send a confirmation and a reminder two hours before your appointment, or help cancel/reschedule it."},
        ],
        "fallback": f"I'm the front desk bot — I handle appointments, departments, visiting hours, and billing questions. That's outside what I can help with here, so please email {CONTACT_EMAIL} for more clarification."
    },
    "furniture": {
        "greeting": "Hi there! I can help you compare pieces, check stock, or estimate delivery — what are you shopping for?",
        "thanks": "Glad I could help! Let me know if you'd like anything else sorted out.",
        "goodbye": "Thanks for stopping by — happy to help again whenever you're ready to order.",
        "topics": [
            {"keywords": ["sofa", "couch", "chair", "table", "bed", "compact", "apartment"], "reply": "I recommend the Luma two-seater: 162 cm wide, stain-resistant fabric, and delivery within 48 hours. Want to see color options?"},
            {"keywords": ["stock", "available", "in stock"], "reply": "Let me check — could you tell me the item name or SKU so I can confirm stock?"},
            {"keywords": ["delivery", "shipping", "arrive"], "reply": "Delivery to your area is available this Friday between 9:00 AM and 1:00 PM, with automated updates along the way."},
            {"keywords": ["warranty", "damaged", "broken", "defect"], "reply": "Sorry about that. I can start a warranty claim now — could you share your order number and a photo of the issue?"},
            {"keywords": ["price", "cost", "how much"], "reply": "Prices vary by piece — tell me which item you're interested in and I'll pull up the exact price."},
            {"keywords": ["payment", "pay", "checkout"], "reply": "I can send a secure payment link once you've picked your item and color."},
        ],
        "fallback": f"I'm the furniture store bot — I help with product recommendations, stock, delivery, and warranty questions. For anything else, email {CONTACT_EMAIL} and our team can clarify."
    },
    "lab": {
        "greeting": "Hey there! I'm the Omisbots assistant. Ask me about pricing and automations, or the kind of bot you need.",
        "thanks": "You're welcome! Anything else you'd like to know?",
        "goodbye": "Thanks for chatting — reach out any time you're ready to build.",
        "topics": [
            {"keywords": ["what do you do", "what does omisbots do", "about omisbots", "what is omisbots", "how does omisbots work"], "reply": "Omisbots connects customer-facing bots, intelligent AI agents, and business automations in one system. We help teams answer customers, capture leads, use business knowledge, and move work through tools like Gmail, CRMs, WhatsApp, and n8n."},
            {"keywords": ["bot", "website bot", "whatsapp bot", "telegram bot", "customer facing"], "reply": "Our bots meet customers on your website, WhatsApp, or Telegram. They can answer questions, collect details, qualify leads, and hand conversations to your team when needed."},
            {"keywords": ["ai agent", "agents", "rag", "memory", "tools", "intelligent agent"], "reply": "AI agents reason over your instructions and business knowledge, remember useful context, and use tools to complete tasks instead of only sending replies."},
            {"keywords": ["n8n", "gmail", "crm", "business systems", "integrate", "integration"], "reply": "Automations connect Omisbots to systems such as Gmail, your CRM, WhatsApp, and n8n. For example: a new email can be classified by AI, added to a CRM, and followed up on WhatsApp."},
            {"keywords": ["start", "get started", "build my bot", "create an agent", "sign up"], "reply": "Create an Omisbots account to open your workspace. From there you can create a bot, choose a workflow, and shape an agent around the work your business needs done."},
            {"keywords": ["price", "pricing", "cost", "charge", "budget", "$"], "reply": "Chatbot development usually ranges from $200 to $800 depending on channels, integrations, and conversation depth."},
            {"keywords": ["contact", "email", "call", "reach"], "reply": f"You can reach us at {CONTACT_EMAIL}. Share what you want the bot to do and which channel you need."},
            {"keywords": ["automation", "automate", "workflow", "reminder"], "reply": "We can automate lead alerts, follow-up messages, appointment reminders, spreadsheet updates, CRM handoffs, and simple reporting flows."},
            {"keywords": ["whatsapp", "builds", "channels", "telegram", "website", "web"], "reply": "We build bots for WhatsApp, Telegram, and websites. The best channel depends on where your customers already message you."},
            {"keywords": ["support", "customer", "faq", "order"], "reply": "A support bot can answer FAQs, check order details, collect issue information, route requests, and prepare a summary for your team."},
            {"keywords": ["booking", "appointment", "hospital", "calendar"], "reply": "A booking assistant can collect customer details, suggest available times, confirm appointments, and send automated reminders."},
            {"keywords": ["sales", "lead", "sell"], "reply": "A sales chatbot can qualify leads, recommend services, collect contact details, and notify your team when someone is ready to buy."},
            {"keywords": ["time", "how long", "timeline", "turnaround"], "reply": "Most builds take one to two weeks depending on complexity and how many integrations are involved."},
        ],
        "fallback": f"I'm the Omisbots assistant — I explain chatbot builds, automations, and pricing, so I'm not able to help with that here. For more clarification, email {CONTACT_EMAIL}."
    }
}

GREETING_REPLY = BOT_LIBRARY["lab"]["greeting"]
OFF_TOPIC_REPLY = BOT_LIBRARY["lab"]["fallback"]


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[!?.,]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_greeting(text: str) -> bool:
    clean = normalize(text)
    return any(clean == greeting or clean.startswith(f"{greeting} ") or clean.endswith(f" {greeting}") for greeting in GREETINGS)


def is_thanks(text: str) -> bool:
    clean = normalize(text)
    return any(thank in clean for thank in THANKS)


def is_bye(text: str) -> bool:
    clean = normalize(text)
    return any(word == clean or clean.startswith(f"{word} ") for word in BYES)


def find_reply(bot: dict, raw_text: str) -> str:
    clean = normalize(raw_text)

    if is_greeting(raw_text):
        return bot["greeting"]

    if is_thanks(raw_text):
        return bot["thanks"]

    if is_bye(raw_text):
        return bot["goodbye"]

    for topic in bot["topics"]:
        if any(keyword in clean for keyword in topic["keywords"]):
            return topic["reply"]

    return bot["fallback"]


def generate_reply(user_input: str, bot_key: str = "lab") -> str:
    bot = BOT_LIBRARY.get(bot_key, BOT_LIBRARY["lab"])
    return find_reply(bot, user_input)


def run_cli() -> None:
    print("Welcome to Omisbots. Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        if not user_input:
            continue
        print("Assistant:", generate_reply(user_input))


if __name__ == "__main__":
    run_cli()