# Usage Guide

## Dashboard

The dashboard provides an overview of all engagements:

- **Stats**: Active, at-risk, insights generated, time saved
- **Health Distribution**: Pie chart of healthy/warning/critical
- **Insights Trend**: Daily AI usage over 30 days
- **Needs Attention**: At-risk engagements requiring action
- **Recent Insights**: Latest AI-generated summaries

## Engagements

### List View
- Filter by status: All, Active, At Risk, Completed, On Hold
- Click any row to view details
- Health score shown as visual bar

### Detail View

**Overview Tab**
- Owner, timeline, contract value, progress
- Team members and roles

**Tasks Tab**
- All tasks with phase, status, progress
- Timeline for each task

**Notes Tab**
- Delivery notes with sentiment coloring
- Risk notes highlighted in red
- Positive notes in green

**AI Insights Tab**
- Generate new insights with buttons
- View history of generated insights

## AI Insights

### Generating Insights

1. Select an engagement from dropdown
2. Choose insight type:
   - **Health Summary**: Overall assessment
   - **Risk Detection**: Identify concerns
   - **Theme Analysis**: Surface patterns
   - **Next Actions**: Recommended steps
3. Click "Generate Insight"
4. Wait 5-10 seconds

### Interpreting Results

The AI provides business-focused analysis:
- Specific observations about the engagement
- Actionable recommendations
- Risk signals if present

## Adoption Metrics

### Key Metrics
- Total insights generated
- Estimated time saved (10 min per insight)
- Stored insights count

### Charts
- **By Role**: Which roles use AI most
- **Time Saved**: Distribution across roles
- **Daily Trend**: Usage patterns over time

### AI Status Indicator
- Green: Connected to Hugging Face
- Yellow: Not connected (check token)

## Settings & Data

### System Status
- API health
- AI model connection
- Data mode (local/databricks)

### Sample Data
- Click "Regenerate Sample Data" to create fresh mock data
- Creates 15 engagements, tasks, notes, metrics

### Data Upload
- Upload JSON files to replace data
- Supports: engagements, tasks, delivery_notes

### Databricks Integration
- View notebook paths
- Link to Databricks workspace

## Tips

1. **At-risk engagements**: Check these first on the dashboard
2. **Generate all insights**: Use the engagement detail page
3. **Refresh data**: Go to Settings → Regenerate Sample Data
4. **Check AI status**: Metrics page shows connection status
