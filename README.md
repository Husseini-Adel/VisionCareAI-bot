👓 VisionCare AI

AI-Powered Optical Center Customer Service & Triage Agent

An interactive AI assistant built with Python and integrated with a Telegram bot to provide customer service for a virtual optical center. The system uses Gemini 3.6 Flash and provides persistent conversation memory through SQLite, with support for intelligent tools for appointment booking and interactive real-time human handoff through a staff group, following strict medical safety rules.

---

🌟 Key Features

- 🧠 AI Agent & Tools (Function Calling): Automatic use of intelligent tools to register appointments or escalate the conversation to a human staff member without manual intervention.
- 🔄 Bi-directional Human Handoff:
  - Automatically transfers the customer when they request a staff member or when an emergency situation is detected.
  - Sends the handoff ticket directly to a private Telegram support team group ("Staff Group").
  - Allows staff members to reply from within the group using Reply to the notification message, allowing the bot to automatically forward the response to the customer's private conversation.
  - Pauses automated AI responses and forwards subsequent customer messages to the group to prevent interference between the AI and the human staff member.
  - Supports the "/resolve" command to close the ticket and the "/bot" command for the customer to resume automated AI responses at any time.
- 💾 Persistent Conversation Memory: Persistent conversation memory using SQLite, retrieving the latest "MEMORY_WINDOW" messages for each customer in complete isolation, ensuring context continuity even after the server restarts.
- 🛡️ Medical Safety & Triage: Strict adherence to not providing diagnoses or prescribing medications, with an immediate emergency routing and escalation system when serious symptoms are detected (sudden vision loss, severe pain, etc.).
- 📅 Appointment Booking: Booking appointments and services and storing them locally in the appointments table.
- ⚡ Resilient Network Handling: Advanced handling of network timeouts and automatic retries to prevent network interruptions.

---

🏗️ Project Architecture

The project is designed using a clean and scalable software architecture (Clean & Modular Architecture):

visioncare-ai/
│
├── ai/
│   ├── gemini.py         # Gemini 3.6 Flash integration, memory management, and tool integration
│   └── prompts.py        # Knowledge Base and system instructions
│
├── bot/
│   ├── handlers.py       # Private message handlers and staff-group replies
│   └── telegram.py       # Application setup and message routing
│
├── database/
│   ├── database.py       # SQLite tables, operations, and automatic field migrations
│   └── memory.py         # Interface for managing conversation history and session states
│
├── services/
│   ├── handoff.py        # Interactive communication bridge between customers and the support group
│   └── booking.py        # Appointment registration and storage logic
│
├── config.example.py     # Example configuration and settings
├── main.py               # Main entry point and application startup
├── test_sqlite.py        # Database and customer-isolation testing script
├── requirements.txt      # Required dependencies
└── README.md