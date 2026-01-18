# Multi-Agent Voice Assistant for Auto Dealership

This project implements a voice-powered multi-agent assistant to help customers book test drives at an auto dealership.

## Tech Stack
- **Backend**: FastAPI, Python, LangGraph, LangChain, Groq (Llama-3), Hugging Face (Whisper & MMS-TTS)
- **Frontend**: Next.js, Tailwind CSS, Lucide React, Framer Motion

## Prerequisites
- Python 3.9+
- Node.js 18+
- Groq API Key

## Setup Instructions

### Backend
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Activate the virtual environment:
   ```bash
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
5. Run the server:
   ```bash
   python main.py
   ```

### Frontend
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## Usage
1. Open the frontend at `http://localhost:3000`.
2. Click the microphone icon and say: "I want to book a test drive for an SUV."
3. Follow the agent's instructions to pick a model and confirm the time.
