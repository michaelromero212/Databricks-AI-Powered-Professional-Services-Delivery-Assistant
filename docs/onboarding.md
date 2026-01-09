# Onboarding Guide

Welcome to the PS Delivery Assistant! This guide will help you get started.

## For Non-Technical Users

### What This Tool Does

The PS Delivery Assistant helps you:
- **View all engagements** in one dashboard
- **Identify at-risk projects** before issues escalate
- **Generate AI insights** from delivery notes
- **Track how the team** is adopting AI tools

### Getting Access

1. Ask your administrator for the application URL
2. Open the URL in your browser (Chrome recommended)
3. No login required for this POC

### Using the Dashboard

1. **Dashboard** - See overall health of all engagements
2. **Engagements** - Browse and filter by status
3. **AI Insights** - Generate and view AI analysis
4. **Metrics** - See adoption statistics
5. **Settings** - Check system status

### Generating AI Insights

1. Go to **Engagements** and click on any engagement
2. Click the **AI Insights** tab
3. Click **Health Summary** or another insight type
4. Wait 5-10 seconds for the AI to generate
5. View the insight in the panel below

---

## For Technical Users

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- Hugging Face account with API token
- (Optional) Databricks workspace access

### Local Development Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd Databricks-AI-Powered-Professional-Services-Delivery-Assistant

# 2. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your HUGGINGFACE_API_TOKEN

# 5. Generate sample data
python data/mock_data_generator.py

# 6. Start backend (Terminal 1)
cd app/backend
python api.py

# 7. Start frontend (Terminal 2)
cd app/frontend
npm install
npm run dev

# 8. Open browser
open http://localhost:5173
```

### Databricks Setup

1. Configure Databricks CLI:
```bash
databricks configure --token
# Enter: https://your-workspace.cloud.databricks.com
# Enter: your-personal-access-token
```

2. Upload notebooks:
```bash
databricks workspace mkdirs /Shared/ps_delivery_assistant
databricks workspace import databricks/notebooks/01_data_ingestion.py \
  /Shared/ps_delivery_assistant/01_data_ingestion -l PYTHON
```

3. Upload data to DBFS:
```bash
databricks fs cp data/generated/engagements.json \
  dbfs:/FileStore/ps_assistant/data/engagements.json
```

4. Run notebooks in order in Databricks workspace

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "AI service unavailable" | Check HUGGINGFACE_API_TOKEN in .env |
| Frontend won't start | Run `npm install` in app/frontend |
| API returns 500 | Check backend logs in terminal |
| Charts not loading | Refresh the page |

### Getting Help

- Check `docs/usage.md` for feature details
- Review `docs/architecture.md` for system design
- Open an issue on GitHub for bugs
