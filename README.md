# AI Table Topics Co-Host -- Production v1

A 4-page Streamlit application for running AI-assisted Toastmasters Table Topics sessions.

## Pages

1. **Home** -- Landing page with Launch Session and Quick Demo Mode
2. **Setup** -- Configure theme, speakers, audio, and guardrails
3. **Live** -- Two-column presenter view + operator controls
4. **Results** -- Session summary, speaker cards, and export (TXT/MD/CSV)

## Requirements

- Python 3.10+
- OpenAI API key (set in `.env` file)
- Microphone for audio recording

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
```

## Run

```bash
# From the project root directory:
streamlit run app/main.py
```

Or on Windows with the provided script:

```powershell
.\run.ps1
```

## Project Structure

```
tabletopics-production-v1/
  app/
    main.py              # Entry point (navigation + async hooks)
    state.py             # Session state contract
    pages/
      home.py            # Page 1: Home/Launch
      setup.py           # Page 2: Setup/Configure
      live.py            # Page 3: Live Session
      results.py         # Page 4: Results/Export
    ui/
      ui_shell.py        # Shared header, sidebar, CSS
      ui_presenter.py    # Presenter view components
      ui_controls.py     # Operator control panel
    coach.py             # Coach hint generation
    evaluator.py         # Async evaluation
    question_gen.py      # Question generation
    summarizer.py        # Answer summarization
    stt.py               # Speech-to-text
    tts.py               # Text-to-speech
    timer.py             # Speaker timer
    audio_io.py          # Audio recording
    recorder.py          # Low-level audio recorder
    bridge.py            # Speaker transition logic
    paths.py             # Directory paths
    validate_env.py      # Environment validation
    prompts/             # LLM prompt templates
  requirements.txt
  run.ps1
  run.sh
  .env
```
