# StudyNotes AutoPoster 📝🚀

> **Automated, handwritten-style educational Instagram carousel note generation and publishing system.**  
> Built with Python 3.11+, FastAPI, Pillow, Matplotlib (mathtext formulas), SQLite, Google Gemini 3.8 Flash, and the Official Meta/Instagram Graph API.  
> **100% Zero-Cost & Free-Tier Friendly.**

---

## 1. What the Project Does

StudyNotes AutoPoster automatically transforms high-yield academic concepts (Mathematics, SQL, DBMS, Algorithms, Machine Learning, Operating Systems) into aesthetic, handwritten-style digital study notes formatted for Instagram carousels (1080 × 1350 px, 4:5 aspect ratio).

### Key Highlights
- **Authentic Notebook Aesthetic**: Warm cream notebook paper, subtle ruled lines, margin guide, authentic spiral binder coils, ballpoint ink blue body text, deep crimson headings with red double-underlines, and circled page numbers.
- **Accurate Mathematical Formulas**: Renders complex LaTeX mathematical notation (matrices, eigenvalues, summations, integrals, polynomials) into crisp transparent images using Matplotlib's mathtext engine.
- **Clean Code & SQL Boxes**: Clean monospace font (Consolas) with rounded containers and casual handwritten side annotations.
- **Structured AI Generation**: Prompts Gemini 3.8 Flash to output strict, validated JSON schemas with zero hallucination.
- **Offline & Zero-Cost Fallbacks**: Works 100% offline out-of-the-box using curated high-yield exam templates when no API key is provided.
- **Official Meta/Instagram Graph API**: Carousel container creation, polling, and publishing. Safe by default with `INSTAGRAM_PUBLISH_ENABLED=false` and `DRY_RUN=true`.
- **Lightweight Web Dashboard**: Single-page dashboard built with HTML5, Vanilla CSS, and Vanilla JavaScript for reviewing drafts, previewing slides, approving, and publishing.
- **Scheduled Automation**: GitHub Actions workflows for automated daily generation and publishing.

---

## 2. Architecture & Pipeline

```
                    ┌─────────────────────────┐
                    │  SQLite Topic Database  │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │     Topic Selector      │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │    Gemini 3.8 Flash     │
                    │  (or Curated Fallback)  │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ Pydantic Content Check  │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  Pillow + Matplotlib    │
                    │  Handwritten Renderer   │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ Visual Quality Service  │
                    │ (1080x1350, Contrast)   │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ Caption & Hashtags Gen  │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ Human Approval / Review │
                    │   (FastAPI Dashboard)   │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ Meta Graph API v20.0+   │
                    │   (Carousel / Dry Run)  │
                    └───────────┬─────────────┘
                                │
                                ▼
                           Instagram
```

---

## 3. Requirements

- **Python**: 3.11 or higher (tested and verified on Python 3.14)
- **Operating System**: Windows, macOS, or Linux
- **Package Manager**: `pip`
- **Dependencies**: Listed in `requirements.txt` (FastAPI, Uvicorn, Pillow, Matplotlib, Pydantic v2, google-genai, HTTPX, Pytest, Ruff)

---

## 4. Installation

Clone this repository and install dependencies:

```bash
git clone https://github.com/your-username/studynotes-autoposter.git
cd studynotes-autoposter

# (Optional) Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Initialize the database and seed the default 20 topics:

```bash
python -m scripts.seed_topics
```

---

## 5. Gemini API Setup (Free Tier)

1. Navigate to [Google AI Studio](https://aistudio.google.com/).
2. Click **Get API Key** and generate a free API key.
3. Open your `.env` file (copied from `.env.example`):
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-3.8-flash
   ```
4. *Note*: If `GEMINI_API_KEY` is not provided, the system automatically runs in offline mode with curated, high-yield engineering templates.

---

## 6. Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Application environment (`development`, `production`) |
| `APP_HOST` | `127.0.0.1` | Web server host |
| `APP_PORT` | `8000` | Web server port |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `GEMINI_API_KEY` | `""` | Google Gemini API key from AI Studio |
| `GEMINI_MODEL` | `gemini-3.8-flash` | Gemini model ID |
| `INSTAGRAM_PUBLISH_ENABLED` | `false` | Master toggle for live Instagram publishing |
| `DRY_RUN` | `true` | When true, simulates containers and returns mock media IDs |
| `INSTAGRAM_ACCESS_TOKEN` | `""` | Meta User Access Token (never commit) |
| `INSTAGRAM_USER_ID` | `""` | Instagram Business/Creator Account ID |
| `META_APP_ID` | `""` | Facebook Developer App ID |
| `META_APP_SECRET` | `""` | Facebook Developer App Secret |
| `PUBLIC_BASE_URL` | `http://localhost:8000` | Public URL accessible to Meta crawlers |
| `DATABASE_PATH` | `data/studynotes.db` | Path to SQLite database file |

---

## 7. Running Locally

Start the FastAPI application and dashboard:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
- **Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Documentation (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **API Health Endpoint**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 8. Generating a Post via CLI

### Generate Next Pending Topic in Queue
```bash
python -m scripts.generate_post --next
```

### Generate a Specific Topic
```bash
python -m scripts.generate_post --topic "SQL GROUP BY Clause"
```

### Generate with Offline Curated Template
```bash
python -m scripts.generate_post --topic "Cayley-Hamilton Theorem" --mock
```

Output is saved to `generated/drafts/<post_id>/`:
- `page_01.png`, `page_02.png`, ... (1080 × 1350 px PNGs)
- `metadata.json` (Structured JSON record)
- `caption.txt` (Instagram caption with emojis and hashtags)

---

## 9. Web Dashboard

The included web dashboard provides complete visual control without requiring third-party tools:
- **Overview**: Real-time counter cards (Total Topics, Pending, Drafts, Approved, Published, Failed).
- **Topics Queue**: Filter by category, inspect difficulty/priority, add new topics, or trigger instant one-click generation.
- **Drafts & Visual Review**: Interactive carousel slide viewer for inspecting 1080×1350 note pages, full-screen zoom, caption inspector, and Approve / Reject / Regenerate / Publish actions.
- **Published Archive**: Complete audit history with Instagram Media IDs.
- **Settings**: Toggle publish status, switch Dry Run, inspect API connectivity, and configure daily cron schedule.

---

## 10. Dry-Run Mode

By default, `DRY_RUN=true` and `INSTAGRAM_PUBLISH_ENABLED=false`.

In Dry-Run mode:
1. Notes are fully generated and rendered to disk.
2. The Instagram container creation, slide pairing, and publication workflows are executed and logged in detail with simulated network delay.
3. Media containers receive simulated IDs (`dryrun_item_...`, `dryrun_carousel_...`, `dryrun_media_...`).
4. **No live calls are made to Meta servers**, protecting your Instagram account from accidental spam, duplicate posts, or API policy violations.

To test publishing in Dry-Run mode:
```bash
python -m scripts.publish_post --id 1 --force
```

---

## 11. Official Meta / Instagram Graph API Configuration

To publish to real Instagram accounts:

### Prerequisites:
1. An **Instagram Professional Account** (Business or Creator).
2. A **Facebook Page** connected to your Instagram account.
3. A **Meta Developer App** created at [developers.facebook.com](https://developers.facebook.com/).

### Setup Steps:
1. Add the **Instagram Graph API** product to your Meta App.
2. Generate a **User Access Token** with permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
   - `pages_show_list`
3. Retrieve your **Instagram User ID**:
   ```bash
   GET https://graph.facebook.com/v20.0/me/accounts?access_token={TOKEN}
   # Find your page, then query:
   GET https://graph.facebook.com/v20.0/{PAGE_ID}?fields=instagram_business_account&access_token={TOKEN}
   ```
4. Set the credentials in `.env`:
   ```env
   INSTAGRAM_ACCESS_TOKEN=EAAB...
   INSTAGRAM_USER_ID=178414...
   INSTAGRAM_PUBLISH_ENABLED=true
   DRY_RUN=false
   PUBLIC_BASE_URL=https://your-public-domain.com
   ```
5. *Note on Public Base URL*: Meta's servers need to download the images from a public URL. For local testing, use a free tunneling tool like [ngrok](https://ngrok.com/):
   ```bash
   ngrok http 8000
   # Set PUBLIC_BASE_URL=https://your-tunnel-id.ngrok-free.app
   ```

---

## 12. GitHub Actions Setup & Scheduling

Two pre-configured GitHub Actions workflows are included in `.github/workflows/`:

### 1. `generate.yml` (Daily Generation)
- **Schedule**: Every day at 12:00 PM UTC (`cron: '0 12 * * *'`).
- Selects the next pending topic, runs Gemini 3.8 Flash, renders note pages, validates image quality, and saves drafts as downloadable workflow artifacts.
- Can be triggered manually anytime via **Actions → Run workflow**.

### 2. `publish.yml` (Daily Publishing)
- **Schedule**: Every day at 2:00 PM UTC (`cron: '0 14 * * *'`).
- Reads the earliest approved post in the database and publishes it to Instagram using the official Graph API.
- Can be triggered manually with a specific Post ID or in Dry Run mode.

---

## 13. GitHub Secrets Configuration

In your GitHub repository, go to **Settings → Secrets and variables → Actions** and add:

| Secret Name | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API Key from Google AI Studio |
| `INSTAGRAM_ACCESS_TOKEN` | Meta Graph API User Access Token |
| `INSTAGRAM_USER_ID` | Instagram Business/Creator Account ID |
| `INSTAGRAM_PUBLISH_ENABLED` | Set to `true` when ready for live publishing |
| `PUBLIC_BASE_URL` | Public domain or CDN URL where generated images can be fetched |

---

## 14. Troubleshooting

### 1. Fonts Look Like Default Font
- Check that open-source TTF fonts exist in `assets/fonts/` (`SegoePrint.ttf`, `PatrickHand-Regular.ttf`, `Consolas.ttf`).
- The system gracefully falls back to Windows system fonts (`C:\Windows\Fonts`) or PIL defaults.

### 2. Formulas Fail to Render
- Ensure `matplotlib` is installed: `pip install matplotlib`.
- The formula renderer supports LaTeX Mathtext without requiring local LaTeX installations.
- Complex matrix brackets `[` and `]` are automatically parsed and aligned by the built-in matrix renderer.

### 3. Meta API Returns Code 190
- Error code 190 means your Meta User Access Token has expired.
- Generate a long-lived access token (valid for 60 days) via Meta's Graph API Explorer.

### 4. Port 8000 Already in Use
- Run on a different port:
  ```bash
  python -m uvicorn app.main:app --port 8080 --reload
  ```

---

## 15. Security Best Practices

- **Never Commit Secrets**: `.env` and SQLite `.db` files are strictly ignored by `.gitignore`.
- **Secrets Redaction**: `app/logging_config.py` automatically scrubs access tokens, API keys, and Bearer tokens before writing to `logs/app.log`.
- **Official Graph API Only**: Zero browser automation, zero password scraping, zero unofficial reverse-engineered APIs.
- **Path Traversal Protection**: File and path utilities sanitize inputs to prevent directory traversal.

---

## 16. How to Add New Templates

Create a new template file in `app/renderer/templates/your_template.py`:

```python
from PIL import Image, ImageDraw
from app.content.schemas import PageContent
from app.renderer.canvas import DESIGN_TOKENS
from app.renderer.decorations import draw_heading_with_underline

def render_your_template_page(canvas: Image.Image, page_content: PageContent) -> Image.Image:
    draw = ImageDraw.Draw(canvas)
    x = DESIGN_TOKENS["content_x_start"]
    y = DESIGN_TOKENS["content_y_start"]
    # Add domain-specific drawing logic here...
    return canvas
```

Register it in `app/renderer/renderer.py` inside `render_single_page()`:

```python
elif "your_subject" in subj_lower:
    render_your_template_page(canvas, page_content)
```

---

## 17. How to Add New Topics

### Option 1: Via the Web Dashboard
Navigate to the **Topics Queue** tab, click **+ Add Topic**, enter name, category, difficulty, priority, and save.

### Option 2: Via `data/topics.json`
Add an entry to `data/topics.json`:

```json
{
  "id": "algo-dijkstra",
  "topic": "Dijkstra's Shortest Path Algorithm",
  "category": "Algorithms",
  "difficulty": "intermediate",
  "priority": 85,
  "status": "pending"
}
```

Then run `python -m scripts.seed_topics`.

---

## 18. How to Change Posting Schedule

1. Open `.github/workflows/generate.yml` and `.github/workflows/publish.yml`.
2. Edit the `cron` line under `on.schedule`:
   ```yaml
   on:
     schedule:
       # Example: Run at 9:00 AM UTC and 6:00 PM UTC twice daily
       - cron: '0 9,18 * * *'
   ```
3. Commit and push changes to GitHub.

---

## 19. Running Tests

Run the full automated test suite:

```bash
python -m pytest -v
```

Run code formatting and linting:

```bash
python -m ruff check app tests scripts
```

---

## 20. License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
