# Personal Finance — Setup Guide

A personal finance dashboard built with Streamlit. Reads spending, savings, and giving data from a Google Sheet and presents it as a clean, mobile-friendly UI.

---

## Google Sheet Structure

The app reads from a single sheet tab. The layout it expects:

| Column | Contents |
|--------|----------|
| A | Transaction name / description |
| B | Spending amount (positive = credit, negative = debit) |
| C | Savings amount |
| D | Giving amount |

**Data rows start at row 3** (rows 1–2 are treated as headers/reserved).

**Totals are read from cells `I5:K5`** in the same sheet tab:
| I5 | J5 | K5 |
|----|----|----|
| Spending total | Savings total | Giving total |

These summary cells should contain formulas that sum up each respective column — the app displays them as the hero balance figures at the top of each view.

---

## Google OAuth Setup

The app uses OAuth 2.0 to authenticate with Google and access your sheet.

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project (or use an existing one).
2. Enable the **Google Sheets API** for the project.
3. Navigate to **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**.
4. Set the application type to **Web application**.
5. Under **Authorized redirect URIs**, add your app's URL:
   - Local: `http://localhost:8501`
   - Deployed: `https://your-app.streamlit.app`
6. Copy the **Client ID** and **Client Secret** — you'll need these as secrets below.

> Make sure the Google account you sign in with has at least **viewer access** to the spreadsheet.

---

## Streamlit Secrets

All sensitive config is managed via [Streamlit Secrets Management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management). In your app's settings on Streamlit Cloud, paste the following into the **Secrets** panel:

```toml
CLIENT_ID      = "your-google-oauth-client-id"
CLIENT_SECRET  = "your-google-oauth-client-secret"
SPREADSHEET_ID = "the-id-from-your-google-sheet-url"
SHEET_NAME     = "Your Sheet Tab Name"
TAX_RATE       = 0.00   # local sales tax rate as a decimal
HOURLY_RATE    = 0.000      # your hourly wage, used by the purchase estimator
```

### Where to find each value

- **`CLIENT_ID` / `CLIENT_SECRET`** — Google Cloud Console → APIs & Services → Credentials → your OAuth 2.0 client.
- **`SPREADSHEET_ID`** — the long string in your Google Sheet URL:
  `https://docs.google.com/spreadsheets/d/`**`THIS_PART`**`/edit`
- **`SHEET_NAME`** — the exact name of the tab at the bottom of your spreadsheet (case-sensitive).
- **`TAX_RATE`** — your local sales tax as a decimal (e.g. `0.07375` for 7.375%).
- **`HOURLY_RATE`** — your hourly wage used by the Purchase Estimator to show how many hours a purchase costs.

---

## Running Locally

1. Install dependencies:
   ```bash
   pip install streamlit pandas requests
   ```

2. Create a `.streamlit/secrets.toml` file in the project root with the same keys listed above.

3. Run the app:
   ```bash
   streamlit run app.py
   ```

4. Make sure `http://localhost:8501` is listed as an authorized redirect URI in your Google Cloud OAuth client.

---

## Deploying to Streamlit Cloud

1. Push `app.py` to a GitHub repository.
2. Connect the repo at [share.streamlit.io](https://share.streamlit.io).
3. In the app's **Settings → Secrets**, paste the TOML block from above.
4. Add your deployed app URL (e.g. `https://your-app.streamlit.app`) as an authorized redirect URI in Google Cloud Console.
5. Deploy — secrets propagate within ~1 minute.
