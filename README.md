# DriveAI: Multi-Agent Voice Assistant for Test Drives

DriveAI is a state-of-the-art multi-agent voice assistant designed for automotive dealerships. It provides a seamless, hands-free experience for customers to browse car models and book test drives using natural language.

---

## 🚀 Key Features

-   **Proactive Voice Greeting**: Greets users verbally upon starting the consultation.
-   **Multi-Agent Orchestration**: Powered by **LangGraph** and **Groq (Llama 3.3)** to manage deep conversational state.
-   **Interactive Flow**: Automatically lists car models based on category intent and confirms specific choices.
-   **Local Persistence**: Saves all test drive bookings to a local `bookings.json` database.
-   **Modern UI**: Glassmorphic React interface with real-time voice activity animations.
-   **Local Speech Processing**: Uses Hugging Face's **Whisper-tiny** (STT) and **MMS-TTS** (TTS) for high-speed, local processing.

---

## 🛠️ Tech Stack

-   **Backend**: FastAPI, LangGraph, LangChain, Groq API, Transformers, Torch.
-   **Frontend**: Next.js 15, Tailwind CSS, Framer Motion, Axios.
-   **Speech**: OpenAI Whisper (STT), Facebook MMS (TTS).

---

## 📋 Prerequisites

-   **Python 3.10+**
-   **Node.js 18+**
-   **Groq API Key**: Get one at [console.groq.com](https://console.groq.com).

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/the-devansh/TestDriveAgent.git
cd TestDriveAssistant
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

**Environment Variables**:
Create a `.env` file in the `backend/` directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

---

## 🏃 Running the Application

### Start the Backend
```bash
cd backend
python main.py
```
*The server will run at `http://localhost:8000`*

### Start the Frontend
```bash
cd frontend
npm run dev
```
*The app will be available at `http://localhost:3000`*

---

## 🎙️ Sample Conversation Flow

1.  **Start**: Click "Start Consultation" to hear the greeting.
2.  **Intent**: *"I want to book a test drive for an SUV tomorrow at 11 AM."*
3.  **Discovery**: Agent lists SUVs (e.g., TrailBlazer X, MountainPeak 360) and asks for confirmation.
4.  **Confirmation**: *"The TrailBlazer please."*
5.  **Success**: Agent confirms booking and saves it to `backend/data/bookings.json`.

---

## 📂 Project Structure

- `backend/logic/agents.py`: LangGraph state machine and tool definitions.
- `backend/services/speech.py`: STT/TTS local model integration.
- `backend/data/`: `cars.json` (Knowledge Base) & `bookings.json` (Local DB).
- `frontend/src/components/VoiceInterface.tsx`: Main voice UI logic.
- `frontend/src/lib/wav-utils.ts`: Browser-side audio processing.
