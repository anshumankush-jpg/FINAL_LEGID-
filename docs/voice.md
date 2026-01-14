# Voice Feature Documentation

## Overview

LEGID/LegalAI includes a complete ChatGPT-style voice input and text-to-speech feature that allows users to:
- Record voice messages using their microphone
- Automatically transcribe speech to text
- Optionally have AI responses read aloud automatically

## Architecture

### Frontend (Angular)
- **VoiceButtonComponent**: Circular button with animated states (idle, recording, processing, error)
- **VoiceService**: Handles API calls to backend STT/TTS endpoints
- **ChatComponent**: Integrates voice input and auto-read TTS playback

### Backend (FastAPI)
- **VoiceService**: Google Cloud Speech-to-Text and Text-to-Speech integration
- **Voice Routes**: `/api/voice/stt` and `/api/voice/tts` endpoints

## Features

### A) Voice Input Button

**Location**: Next to the chat input field

**States**:
1. **Idle**: Microphone icon (gray)
2. **Recording**: Animated sound bars with red pulse (recording indicator)
3. **Processing**: Spinner animation (transcribing)
4. **Error**: Warning icon (permission denied or transcription failed)

**Behavior**:
- Click to start recording
- Click again to stop recording
- Auto-stops after 60 seconds
- Shows recording duration indicator ("Listening... Xs")

### B) Recording

**Technology**: 
- Web Audio API (`navigator.mediaDevices.getUserMedia`)
- `MediaRecorder` API for audio capture

**Audio Format**:
- Preferred: `audio/webm;codecs=opus`
- Fallback: `audio/webm`, `audio/mp4`, `audio/wav`

**Features**:
- Echo cancellation enabled
- Noise suppression enabled
- Sample rate: 44.1kHz
- Maximum duration: 60 seconds

### C) Speech-to-Text (STT)

**Endpoint**: `POST /api/voice/stt`

**Request**:
- Content-Type: `multipart/form-data`
- Body: `audio` file (Blob)

**Response**:
```json
{
  "text": "Transcribed text here",
  "confidence": 0.95
}
```

**Backend Implementation**:
- Uses Google Cloud Speech-to-Text API
- Language: `en-CA` (Canadian English, configurable)
- Automatic punctuation enabled
- Fallback mock response if GCP not configured

**Frontend Integration**:
- Transcribed text is inserted into chat input
- Auto-sends if text ends with `.`, `?`, or `!`
- Otherwise, user can edit before sending

### D) Text-to-Speech (TTS) - Auto-Read

**Endpoint**: `POST /api/voice/tts`

**Request**:
```json
{
  "text": "Text to convert to speech",
  "voice": "en-CA-Neural2-D",
  "language": "en-CA",
  "speed": 1.0
}
```

**Response**:
- Content-Type: `audio/mpeg`
- Streaming audio blob (MP3 format)

**Personalization Integration**:
- Controlled by `auto_read_responses` preference in user profile
- When enabled, automatically plays TTS after each assistant response
- Can be toggled in Personalization settings page

**Manual Playback**:
- Speaker icon in message actions allows replaying TTS
- Shows "Playing..." state while audio is active

### E) Accessibility & Permissions

**Microphone Permission**:
- Browser prompts user on first use
- If denied, voice button is disabled with error state
- Clear error message guides user to browser settings

**Keyboard Support**:
- Voice button accessible via Tab key
- Enter key sends text message
- Voice button can be activated with Space/Enter

**Error Handling**:
- Permission denied: Shows guidance message
- STT failure: Toast notification with retry option
- TTS failure: Silent failure (doesn't block chat)

## Setup Instructions

### Backend Setup

1. **Install Dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

The following packages are required:
- `google-cloud-speech>=2.21.0`
- `google-cloud-texttospeech>=2.16.0`

2. **Configure Google Cloud**:
   - Create a GCP project (or use existing)
   - Enable Speech-to-Text API
   - Enable Text-to-Speech API
   - Create service account and download credentials JSON
   - Set environment variable:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
     ```
   - Or add to `.env` file:
     ```env
     GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
     GCP_PROJECT_ID=your-project-id
     ```

3. **Environment Variables** (`.env` in backend directory):
```env
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

4. **Start Backend**:
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### Frontend Setup

1. **Install Dependencies** (if not already installed):
```bash
cd frontend
npm install
```

2. **Start Frontend**:
```bash
ng serve
# Or
npm start
```

The frontend will run on `http://localhost:4200`

### Development Mode (Without GCP)

If Google Cloud is not configured, the system will:
- Return mock responses for STT (with clear logging about setup)
- Return mock responses for TTS (with clear logging about setup)
- Still allow testing the UI flow

**Note**: Mock responses are clearly marked and should not be used in production.

## API Endpoints

### POST /api/voice/stt

Convert speech audio to text.

**Request**:
- Method: POST
- Content-Type: multipart/form-data
- Body: `audio` (file)

**Response**:
```json
{
  "text": "Transcribed text",
  "confidence": 0.95
}
```

**Error Responses**:
- `400`: Invalid audio format or no file provided
- `413`: Audio file too large (>25MB)
- `500`: Processing error

### POST /api/voice/tts

Convert text to speech.

**Request**:
```json
{
  "text": "Text to convert",
  "voice": "en-CA-Neural2-D",
  "language": "en-CA",
  "speed": 1.0
}
```

**Response**:
- Content-Type: audio/mpeg
- Streaming MP3 audio

**Error Responses**:
- `400`: Text too long (>5000 chars) or empty
- `500`: Processing error

### GET /api/voice/voices

Get available TTS voices.

**Response**:
```json
{
  "voices": [
    {
      "name": "en-CA-Neural2-D",
      "language": "en-CA",
      "gender": "MALE",
      "display_name": "Neural Male"
    }
  ]
}
```

## Testing

### Test STT Endpoint

```bash
# Using curl
curl -X POST http://localhost:8080/api/voice/stt \
  -F "audio=@test_audio.webm"
```

### Test TTS Endpoint

```bash
# Using curl
curl -X POST http://localhost:8080/api/voice/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test", "language": "en-CA"}' \
  --output speech.mp3
```

### Test Frontend

1. Start backend on `localhost:8080`
2. Start frontend on `localhost:4200`
3. Navigate to chat interface
4. Click voice button (microphone icon)
5. Allow microphone permission
6. Speak and click again to stop
7. Verify transcription appears in input field

## Troubleshooting

### Microphone Permission Denied

**Issue**: Voice button shows error state immediately

**Solution**:
1. Check browser settings for microphone permissions
2. For Chrome: Settings → Privacy and Security → Site Settings → Microphone
3. Ensure `localhost:4200` is allowed

### STT Returns Mock Response

**Issue**: Always getting "Mock transcription" message

**Solution**:
1. Verify `GOOGLE_APPLICATION_CREDENTIALS` is set
2. Check that credentials file exists and is valid
3. Verify Speech-to-Text API is enabled in GCP project
4. Check backend logs for specific error messages

### TTS Not Playing

**Issue**: Auto-read enabled but no audio plays

**Solution**:
1. Check browser console for errors
2. Verify `auto_read_responses` preference is `true` in profile
3. Check backend logs for TTS errors
4. Verify Text-to-Speech API is enabled in GCP project

### CORS Errors

**Issue**: Frontend can't call voice endpoints

**Solution**:
1. Verify CORS is configured in `backend/app/main.py`
2. Ensure `localhost:4200` is in allowed origins
3. Check backend is running on correct port (8080)

## Production Deployment

### Environment Variables

Set in your deployment environment:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GCP_PROJECT_ID=your-project-id
```

### GCP Service Account Permissions

Ensure service account has:
- `Cloud Speech-to-Text API User`
- `Cloud Text-to-Speech API User`

### Cost Considerations

- Google Cloud Speech-to-Text: ~$0.006 per 15 seconds
- Google Cloud Text-to-Speech: ~$4 per 1 million characters
- Consider implementing rate limiting for production

## File Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── voice.py          # Voice API endpoints
│   ├── services/
│   │   └── voice_service.py      # Google Cloud STT/TTS integration
│   └── main.py                   # FastAPI app (includes voice router)
└── requirements.txt               # Includes google-cloud-speech, google-cloud-texttospeech

frontend/
└── src/
    └── app/
        ├── components/
        │   ├── chat/
        │   │   └── chat.component.ts      # Chat with voice integration
        │   └── voice-button/
        │       ├── voice-button.component.ts
        │       └── voice-button.component.css
        └── services/
            ├── voice.service.ts           # Voice API service
            └── profile.service.ts        # Profile service (for auto_read_responses)
```

## Future Enhancements

- [ ] Support for multiple languages
- [ ] Voice activity detection (auto-start/stop)
- [ ] Real-time streaming transcription
- [ ] Voice commands (e.g., "send message")
- [ ] Custom voice selection UI
- [ ] Offline fallback using Web Speech API
