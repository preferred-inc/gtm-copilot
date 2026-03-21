# GTM Copilot

This project focuses on building programs and prompts to automate Google Tag Manager (GTM) implementation tasks using AI.

## How it Works

1. **Extraction**: Using the Google Tag Manager API, the tool retrieves existing components such as tags, triggers, and variables, and saves them in JSON format.
2. **AI-Powered Modification**: AI is used to update the JSON files, performing the actual tag implementation logic within the files.
3. **Synchronization**: Once the implementation (JSON editing) is complete, the changes are synced back to Google Tag Manager using the API.

## Architecture

To ensure portability and ease of setup, this project is implemented using **only the Python standard library**. No external dependencies (such as `requests` or `google-auth`) are required.

- **Programming Language**: Python 3.x (Standard Library only)

## AI-Powered GTM Generation

Enter a URL and automatically generate optimal GTM configurations.

### Flow
```
URL input → Site analysis (Playwright) → AI generation (Claude) → Preview → Apply to GTM
```

### Supported Site Types
- **EC**: purchase, add_to_cart, view_item and other ecommerce events
- **SaaS**: sign_up, login, CTA click tracking
- **Landing Page**: form_submit, scroll_depth, CTA click
- **Media**: scroll_depth, article_view, outbound_click
- **Corporate**: form_submit, basic tracking

### Getting Started
```bash
# Add ANTHROPIC_API_KEY to src/.env

# Docker
docker compose up --build

# Open http://localhost:3000/generate
```

---

## Agent Skills Setup

For general information on Agent Skills, please refer to [agentskills.io](https://agentskills.io/home).

To use the GTM Copilot skills, follow these steps:

1. **Download**: Obtain the pre-built `gtm-copilot_vX.X.X.zip` from the [Releases](https://github.com/sem-technology/gtm-copilot/releases) page.
2. **Setup**: Extract the zip file and place the contents into your AI Agent's skill directory (e.g., `.agent/skills/gtm-copilot/`).
3. **Authentication**: Copy `.env.example` to `.env` in the skill directory and update your credentials.
4. **Usage**: Once placed, your AI Agent will automatically recognize the tools defined in `SKILL.md` and can start automating your GTM workflow.
