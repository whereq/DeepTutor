# Guided Learning Module

## Overview

Guided Learning is a personalized learning system driven by the user's learning request. The system designs a progressive knowledge point learning plan from the user's input, then helps users gradually master the topic through interactive pages and intelligent Q&A.

## Features

1. **Intelligent Learning Plan Design** (DesignAgent)
   - Analyzes the user's learning request
   - Identifies core knowledge points and organizes them in progressive relationships
   - Generates 3-5 structured knowledge point learning plans

2. **Learning Progress Management** (GuideManager)
   - Tracks current learning state
   - Manages transitions between knowledge points (based on explicit user progression signals)
   - Provides learning progress feedback

3. **Interactive Page Generation** (InteractiveAgent)
   - Converts knowledge points into visual, interactive HTML pages
   - Designs appropriate interactive elements based on knowledge characteristics
   - Supports HTML bug fixing functionality

4. **Intelligent Q&A Assistant** (ChatAgent)
   - Answers user questions during learning
   - Provides contextually relevant answers based on current knowledge point and chat history
   - Provides additional explanations for potential user difficulties

5. **Learning Summary Generation** (SummaryAgent)
   - Generates personalized learning summaries after completing all knowledge points
   - Analyzes learning process and mastery level
   - Provides follow-up learning suggestions

## Directory Structure

```
guide/
├── __init__.py
├── guide_manager.py          # Session manager (includes learning progress management logic)
├── agents/
│   ├── __init__.py
│   ├── base_guide_agent.py   # Agent base class
│   ├── design_agent.py        # Learning plan design agent
│   ├── interactive_agent.py    # Interactive page generation agent
│   ├── chat_agent.py          # Q&A agent
│   └── summary_agent.py       # Summary generation agent
└── prompts/
    ├── zh/                    # Chinese prompts
│   ├── design_agent.yaml
    │   ├── interactive_agent.yaml
    │   ├── chat_agent.yaml
    │   └── summary_agent.yaml
    └── en/                    # English prompts (optional)
```

## API Endpoints

### REST API

- `POST /api/v1/guide/create_session` - Create learning session
- `POST /api/v1/guide/start` - Start learning
- `POST /api/v1/guide/next` - Move to next knowledge point
- `POST /api/v1/guide/chat` - Send chat message
- `POST /api/v1/guide/fix_html` - Fix HTML page
- `GET /api/v1/guide/session/{session_id}` - Get session information
- `GET /api/v1/guide/session/{session_id}/html` - Get current HTML

### WebSocket

- `WS /api/v1/guide/ws/{session_id}` - Real-time interaction endpoint

## Usage Flow

1. **Describe Learning Goal**
   - User describes what they want to learn in the frontend
   - System calls `create_session` to create a learning session

2. **Generate Learning Plan**
   - DesignAgent analyzes the user's learning request
   - Generates 3-5 progressive knowledge points
   - Displays learning plan to user

3. **Start Learning**
   - User clicks "Start Learning"
   - System generates interactive page for first knowledge point
   - User can view interactive content on the right side

4. **Learning Interaction**
   - User can ask questions in the left chat box
   - ChatAgent answers questions based on current knowledge point
   - User can click "Next" to move to next knowledge point

5. **Complete Learning**
   - After completing all knowledge points, system generates learning summary
   - Summary includes learning review, mastery assessment, and improvement suggestions

## Data Storage

All session data is stored in the `user/guide/` directory, with each session saved as an independent JSON file:
- File name format: `session_{session_id}.json`
- Contains complete session state, knowledge points, chat history, etc.

## Configuration Requirements

- LLM environment variables must be configured (LLM_MODEL, LLM_API_KEY, LLM_HOST)
- Ensure the user provides a clear enough learning request
- Recommend using LLM models that support JSON format output

## Notes

1. **Knowledge Point Count**: System automatically generates 3-5 knowledge points to ensure learning plan is neither too general nor too fragmented
2. **HTML Generation**: If LLM-generated HTML has issues, can use Debug functionality to fix
3. **Chat History**: Each knowledge point's chat history is independent for easier context management
4. **Session Persistence**: Session data is automatically saved, can resume learning progress at any time

## Extensibility

- Can add more interaction types (e.g., animations, 3D visualizations)
- Can integrate more learning tools (e.g., practice questions, quizzes)
- Can add learning path recommendation functionality
- Can support multi-user collaborative learning
