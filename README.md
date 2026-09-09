👓 VisionCare AI

AI-Powered Optical Center Customer Service & Triage Agent

VisionCare AI is an interactive AI-powered customer service and triage agent built with Python and integrated with a Telegram Bot for a virtual optical center, Clear Vision Optical Center – Taiz.

The system uses Google Gemini for intelligent conversational interactions and provides persistent conversation memory through SQLite. It supports intelligent appointment booking, medical-safety triage, and real-time human handoff through a dedicated Telegram staff group.

The system is designed as a customer-support and decision-support assistant. It does not provide medical diagnoses, prescribe medications, or replace qualified healthcare professionals.

---

🌟 Key Features

🧠 AI Agent & Tool Calling

- AI-powered conversational customer service.
- Automatic use of specialized tools through function calling.
- Appointment booking through an integrated booking tool.
- Human escalation through a dedicated handoff tool.
- Context-aware conversations using persistent customer memory.

🔄 Bi-Directional Human Handoff

VisionCare AI provides a complete communication bridge between customers and human staff.

- Automatically escalates conversations when a customer requests a human representative.
- Can escalate potentially urgent situations according to predefined safety rules.
- Sends a support ticket directly to a private Telegram Staff Group.
- Staff members can reply directly to the ticket message using Telegram's Reply feature.
- The bot automatically forwards the staff member's response to the customer's private conversation.
- Automatically pauses AI responses while a human representative is handling the conversation.
- Subsequent customer messages can be forwarded to the staff group during an active handoff.
- Supports "/resolve" for staff members to close an active support ticket.
- Supports "/bot" for customers to return to AI-assisted conversations.

💾 Persistent Conversation Memory

Conversation history is stored using SQLite.

The system:

- Stores customer conversation history locally.
- Retrieves the most recent "MEMORY_WINDOW" messages for each customer.
- Keeps customer conversations isolated from one another.
- Preserves conversation context even after the server restarts.
- Maintains session and handoff states independently for each customer.

🛡️ Medical Safety & Triage

VisionCare AI follows strict medical-safety principles.

The AI assistant:

- Does not provide medical diagnoses.
- Does not prescribe medication.
- Does not claim to replace an optometrist, ophthalmologist, or laboratory/medical professional.
- Identifies potentially urgent symptoms according to predefined safety instructions.
- Escalates potentially serious cases to human staff when appropriate.
- Encourages customers to seek appropriate professional medical care when necessary.

Examples of potentially urgent symptoms include sudden vision loss, severe eye pain, and other predefined warning signs.

📅 Appointment Booking

The system supports appointment-related operations, including:

- Collecting appointment information.
- Recording booking details.
- Storing appointments locally.
- Connecting the AI conversation with the booking service.
- Allowing human staff to intervene when necessary.

⚡ Resilient Network Handling

The application includes mechanisms for handling unreliable network conditions.

These include:

- Network timeout handling.
- Automatic retry mechanisms.
- Error handling for external API requests.
- More reliable communication between the Telegram Bot and AI services.

---

🏗️ Project Architecture

VisionCare AI follows a clean and modular architecture designed to separate AI logic, Telegram communication, database management, and business services.

visioncare-ai/
│
├── ai/
│   ├── gemini.py
│   │   # Gemini integration, conversation memory,
│   │   # and AI tool/function calling
│   │
│   └── prompts.py
│       # System instructions and Knowledge Base
│
├── bot/
│   ├── handlers.py
│   │   # Private customer messages and staff-group replies
│   │
│   └── telegram.py
│       # Telegram application setup and message routing
│
├── database/
│   ├── database.py
│   │   # SQLite tables, database operations,
│   │   # and automatic field migrations
│   │
│   └── memory.py
│       # Conversation history and session-state management
│
├── services/
│   ├── handoff.py
│   │   # Customer ↔ Staff Group communication bridge
│   │
│   └── booking.py
│       # Appointment booking and storage logic
│
├── config.example.py
│   # Example configuration and environment settings
│
├── main.py
│   # Application entry point
│
├── test_sqlite.py
│   # SQLite database and customer-isolation tests
│
├── requirements.txt
│   # Python dependencies
│
└── README.md

---

🔄 System Workflow

The overall interaction flow can be summarized as:

Customer
   │
   ▼
Telegram Bot
   │
   ▼
AI Agent
   │
   ├──────────────► Knowledge Base
   │
   ├──────────────► Conversation Memory
   │
   ├──────────────► Appointment Booking
   │
   └──────────────► Human Handoff
                         │
                         ▼
                  Staff Telegram Group
                         │
                         ▼
                   Human Staff Member
                         │
                         ▼
                  Customer Conversation

During an active human handoff, the AI assistant stops responding automatically so that the human representative can communicate with the customer without interference.

---

🧩 Core Components

AI Layer

The AI layer is responsible for:

- Gemini model integration.
- System prompt management.
- Knowledge Base integration.
- Conversation context.
- Tool/function calling.
- Medical-safety instructions.
- Customer-support decision logic.

---

Telegram Bot Layer

The Telegram layer handles:

- Customer conversations.
- Staff-group interactions.
- Message routing.
- Staff replies.
- Handoff notifications.
- "/resolve" command.
- "/bot" command.
- Active-session management.

---

Database Layer

SQLite is used for persistent local storage.

The database manages:

- Conversation history.
- Customer sessions.
- Handoff states.
- Appointment records.
- Ticket-related information.

Customer data and conversation history are logically isolated to prevent one customer's context from being mixed with another customer's conversation.

---

Services Layer

The services layer contains application-specific business logic.

"booking.py"

Responsible for appointment-related operations.

"handoff.py"

Responsible for communication between:

Customer ↔ AI Agent ↔ Staff Group ↔ Human Staff

This allows human representatives to take over conversations when required.

---

👨‍💻 Technologies Used

Technology| Purpose
Python| Core application development
Google Gemini| AI conversational agent
Telegram Bot API| Customer and staff communication
SQLite| Persistent local storage
Function Calling / Tools| Appointment booking and human handoff
Async Programming| Telegram and network operations

---

🔐 Security & Privacy

The project follows several principles for safer handling of customer interactions:

- API credentials should never be committed to GitHub.
- Sensitive configuration should be stored outside the source code.
- Customer conversations are isolated by customer/session identifiers.
- Medical responses are constrained by system-level safety instructions.
- Human escalation is available for situations that require professional intervention.

«Important: This project is a customer-support and decision-support system. It is not intended to provide autonomous medical diagnosis or replace qualified healthcare professionals.»

---

⚙️ Configuration

Create your local configuration based on:

config.example.py

Configuration values may include:

Telegram Bot Token
Gemini API Key
Staff Group ID
Database Configuration
Memory Window

Never upload real API keys, bot tokens, passwords, or other secrets to GitHub.

---

🚀 Getting Started

1. Clone the Repository

git clone https://github.com/YOUR_USERNAME/visioncare-ai.git
cd visioncare-ai

Replace "YOUR_USERNAME" with your GitHub username.

---

2. Create a Virtual Environment

Windows

python -m venv .venv
.venv\Scripts\activate

Linux / macOS

python3 -m venv .venv
source .venv/bin/activate

---

3. Install Dependencies

pip install -r requirements.txt

---

4. Configure the Application

Create your local configuration from the example configuration file:

cp config.example.py config.py

On Windows, you can simply copy the file manually:

config.example.py → config.py

Then configure the required credentials and settings.

---

5. Run the Application

python main.py

The Telegram bot should then start and begin processing incoming customer messages.

---

🧪 Testing

The project includes a SQLite testing script:

python test_sqlite.py

The test focuses on database behavior and customer conversation isolation.

---

🤝 Human Handoff Example

A typical escalation workflow looks like this:

Customer
   │
   │ "I want to speak with a staff member."
   ▼
AI Agent
   │
   │ Creates handoff ticket
   ▼
Staff Telegram Group
   │
   │ Staff replies using Telegram Reply
   ▼
Handoff Service
   │
   ▼
Customer

While the ticket is active:

Customer Message
       │
       ▼
Staff Group
       │
       ▼
Human Staff
       │
       ▼
Customer

The AI remains paused until the staff member resolves the ticket.

---

🧠 Why This Project?

Traditional customer-service systems often depend heavily on manual responses.

VisionCare AI explores how AI Agents, tool calling, persistent memory, and human-in-the-loop workflows can be combined to create a more interactive customer-service system.

The project demonstrates practical concepts including:

- AI Agents
- Function Calling
- AI Automation
- Telegram Bots
- REST/API integrations
- Persistent Memory
- Human-in-the-Loop Systems
- Medical Safety Guardrails
- Automated Appointment Booking
- Real-Time Human Handoff

---

📌 Project Status

Development Status: Active Development

The system is being developed as an experimental AI-powered customer-service platform and may continue to evolve as additional features, testing, and improvements are introduced.

---

⚠️ Disclaimer

VisionCare AI is a software engineering and AI project intended for customer support, information assistance, appointment management, and human escalation.

It must not be used as a substitute for professional medical evaluation.

The system does not provide a final medical diagnosis and does not prescribe medications.

Any potentially serious medical concern should be evaluated by an appropriately qualified healthcare professional.

---

👤 Author

Hussein Adel

AI & Data Science 

---

⭐ If you find this project interesting, feel free to explore the repository and follow its development.