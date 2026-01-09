# Architecture Overview

## System Components

### 1. Data Layer

**Local Mode (Default)**
- Data stored as JSON files in `data/generated/`
- Connector loads, caches, and serves data to API
- Suitable for development and demos

**Databricks Mode**
- Data stored in Delta tables in Databricks workspace
- Notebooks handle data ingestion and transformation
- SQL views provide aggregated metrics

```
Delta Tables:
├── ps_engagements      # Customer engagement records
├── ps_tasks            # Tasks and milestones
├── ps_delivery_notes   # Free-text observations
├── ps_notebook_usage   # Execution metadata
├── ps_ai_insights      # Generated AI insights
├── ps_ai_metrics       # Tool usage tracking
└── ps_adoption_metrics # Adoption by role
```

### 2. AI Layer

**Hugging Face Integration**
- Model: `mistralai/Mistral-7B-Instruct-v0.2`
- Inference API for serverless execution
- Prompt templates for PS-specific insights

**Insight Types**
| Type | Purpose |
|------|---------|
| `health_summary` | Overall engagement assessment |
| `risk_detection` | Identify blockers and concerns |
| `theme_extraction` | Surface patterns from notes |
| `action_recommendation` | Prioritized next steps |

### 3. Application Layer

**Backend (FastAPI)**
```
/api/health          GET    System status
/api/dashboard       GET    Overview data
/api/engagements     GET    List engagements
/api/engagements/:id GET    Engagement details
/api/insights        GET    List AI insights
/api/insights/generate POST Generate new insight
/api/metrics         GET    Adoption metrics
/api/data/regenerate POST   Regenerate sample data
```

**Frontend (React)**
```
/                    Dashboard overview
/engagements         Engagement list
/engagements/:id     Engagement detail
/insights            AI insights panel
/metrics             Adoption metrics
/settings            System config & data
```

### 4. Databricks Notebooks

| Notebook | Language | Purpose |
|----------|----------|---------|
| 01_data_ingestion | Python | Load data into Delta |
| 02_feature_engineering | SQL | Create aggregated views |
| 03_ai_insights | Python | Generate insights in Databricks |
| 04_metrics_tracking | Python | Track and persist usage |

## Data Flow

```
User Action → React Frontend → FastAPI Backend
                                    ↓
                 ┌──────────────────┴──────────────────┐
                 ↓                                     ↓
          Data Request                          AI Request
                 ↓                                     ↓
          Databricks Connector              Hugging Face Client
                 ↓                                     ↓
          JSON Files / Delta               Mistral-7B-Instruct
                 ↓                                     ↓
                 └──────────────────┬──────────────────┘
                                    ↓
                            JSON Response
                                    ↓
                            React UI Update
```

## Security Considerations

1. **Credential Management**
   - Tokens stored in `.env` (not committed)
   - Environment variables loaded at runtime
   - No hardcoded secrets

2. **API Security**
   - CORS configured for local development
   - Input validation on all endpoints
   - Error messages sanitized

3. **Data Privacy**
   - Mock data only (no real customer data)
   - No PII in generated samples
