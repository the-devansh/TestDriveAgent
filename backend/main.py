from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from services.speech import SpeechService
from logic.agents import run_agent

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

speech_service = SpeechService()

UPLOAD_DIR = "temp_audio"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/voice-chat")
async def voice_chat(audio: UploadFile = File(...)):
    # 1. Save uploaded audio
    input_filename = f"{UPLOAD_DIR}/{uuid.uuid4()}.wav"
    with open(input_filename, "wb") as f:
        f.write(await audio.read())

    # 2. STT
    text = speech_service.transcribe(input_filename)
    print(f"User said: {text}")

    # 3. Agentic Logic
    # For a simple demo, we use a single thread. In production, this would come from a cookie or session.
    response_text = run_agent(text, thread_id="user_session_1")
    print(f"Agent response: {response_text}")

    # 4. TTS
    output_filename = f"{UPLOAD_DIR}/{uuid.uuid4()}_response.wav"
    speech_service.synthesize(response_text, output_filename)

    # Clean up input file
    os.remove(input_filename)

    return {
        "user_text": text,
        "agent_text": response_text,
        "audio_url": f"/audio/{os.path.basename(output_filename)}"
    }

@app.get("/greet")
async def greet():
    """Returns an initial greeting audio on page load."""
    thread_id = "user_session_1"
    greeting_text = "Hello! Welcome to our dealership. How can I help you today? I can help you find SUVs, sedans, or book a test drive."
    
    # Use full path for saving
    output_filename = f"{uuid.uuid4()}_greeting.wav"
    output_path = os.path.join(UPLOAD_DIR, output_filename)
    speech_service.synthesize(greeting_text, output_path)
    
    # Store greeting in history
    from logic.agents import app as agent_app
    from langchain_core.messages import AIMessage
    config = {"configurable": {"thread_id": thread_id}}
    agent_app.update_state(config, {"messages": [AIMessage(content=greeting_text)]})

    return {
        "text": greeting_text,
        "audio_url": f"/audio/{output_filename}"
    }

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = f"{UPLOAD_DIR}/{filename}"
    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
