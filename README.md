# Trello DIO Project

This repository contains a simple project built during a bootcamp, focused on learning how to create agents with Google ADK and integrate them with external tools such as Trello.

The main idea of the project is to use an agent to help organize daily tasks by creating, listing, and moving Trello cards.

## What I learned

- How to create an agent with Google ADK
- How to expose Python functions as agent tools
- How to integrate an agent with the Trello API
- How to use environment variables for local configuration
- How to run the project locally for testing

## Project structure

```text
agents/
  eco_planner/
    requirements.txt
    agenttaskmanager/
      __init__.py
      agent.py
```

## Run locally

### 1. Clone the repository

```bash
git clone https://github.com/fercatalani/trello-agent-dio.git
cd projeto-trello-dio
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
cd agents/eco_planner
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file inside `agents/eco_planner` with your Trello credentials:

```env
TRELLO_API_KEY=your_api_key
TRELLO_API_SECRET=your_api_secret
TRELLO_TOKEN=your_token
```

## Run the agent

From `agents/eco_planner`, run:

```bash
adk web
```

If `adk` is not available in your shell, run it with Python:

```bash
python -m adk.web
```

## Notes

- This is a study project created during a bootcamp.
- The Trello board and lists must exist and be accessible by the configured token.
- Local environment folders such as `.lab-dio` are not meant to be committed.
