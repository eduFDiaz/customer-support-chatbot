# LangGraph Chat Application

This repository contains a full-stack chat application built with LangGraph for the backend and Angular for the frontend. The application demonstrates a conversational AI assistant that can help users book, list, reschedule, or cancel dentist appointments.

## Project Structure

- `server/`: Backend server built with LangGraph and FastAPI
- `frontend/`: Frontend application built with Angular
- `env/`: Python virtual environment

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Angular CLI (`npm install -g @angular/cli`)

## Backend Setup

1. Create and activate a virtual environment:

```bash
# Create a virtual environment
python -m venv env

# Activate the virtual environment
# For Linux/Mac:
source env/bin/activate
# For Windows:
env\Scripts\activate
```

2. Install dependencies:

```bash
cd server
pip install -r requirements.txt
```

3. Start the server:

```bash
cd server
# Start the FastAPI server
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

The backend server will start at http://localhost:8000.

## Frontend Setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Start the development server:

```bash
cd frontend
ng serve
```

The Angular application will be available at http://localhost:4200.

## Using the Application

1. Open your browser and navigate to http://localhost:4200
2. Start chatting with the assistant to book, list, reschedule, or cancel appointments
3. When the assistant needs to perform sensitive operations (like booking an appointment), you'll be prompted to approve or deny the action

## Key Features

- Real-time chat with an AI assistant
- WebSocket communication between frontend and backend
- Tool calling with user approval for sensitive operations
- Markdown rendering for formatted messages
- Persistent chat history (per session)

## Development

- To modify the AI behavior, edit the files in the `server` directory
- To modify the frontend UI, edit the files in the `frontend/src` directory
- LangGraph flow is defined in `server/graph.py` and `server/graph_builder.py`
- The main FastAPI WebSocket handler is in `server/server.py`

## Testing

You can test the application manually by interacting with the chat interface, or you can run the example script:

```bash
cd server
python main.py
```

This will run through a series of example questions to demonstrate the application's capabilities.

## Troubleshooting

- If you encounter CORS issues, make sure your frontend application is listed in the allowed origins in `server/server.py`
- If WebSocket connections are failing, ensure that your browser supports WebSockets and that no firewall is blocking the connection
- For any issues with tool calls or interrupts, check the backend console logs for detailed error messages
