# DataPulse

Automated data profiling, quality scoring and cleaning recommendations for CSV and Excel files, built with **Streamlit** and **MySQL**.

DataPulse was developed as the MCA 3rd-semester mini project (II MCA A, B & C) at SRM Institute of Science and Technology.

**Live demo:** [daatapulse.streamlit.app](https://daatapulse.streamlit.app)

Free apps on Streamlit Community Cloud go to sleep when idle, so the first load can take a moment. Sign up and sign in need a MySQL database. On the hosted demo they work only when a hosted database is connected through the app's Secrets (see [Deploying on Streamlit Community Cloud](#deploying-on-streamlit-community-cloud)). Everything else works without one.

## What it does

Upload a dataset, see what is wrong with it, review suggested fixes, apply the ones you agree with, and export the result with a full audit trail.

| # | Screen | What it does |
|---|--------|--------------|
| 1 | Login / Sign up | Floating dialogs. Accounts are stored in MySQL with bcrypt-hashed passwords. |
| 2 | Upload | Reads a CSV/XLSX file, computes row count, column count, missing % and duplicate %, and saves the upload record to MySQL. |
| 3 | Data Profiling | Per-column type, missing %, unique count, distribution charts and an interactive column inspector. |
| 4 | Quality Score & AI Suggestions | Detects missing values, duplicate rows and outliers, shows each as a suggestion you can accept or reject, and recomputes the Data Quality Score live. |
| 5 | Dashboard | Before vs after comparison: KPI deltas, radar chart of the four quality dimensions, missing-value and distribution charts. |
| 6 | Reports / Export | Download the cleaned dataset (CSV), a PDF cleaning report and the audit log (CSV). |

## Tech stack

| Area | Technology |
|------|------------|
| Language | Python 3.10+ (tested on 3.13) |
| UI and routing | Streamlit multi-page app (`st.navigation`), custom CSS dark theme |
| Data processing | Pandas, NumPy |
| Charts | Plotly |
| Database | MySQL / MariaDB |
| DB driver | mysql-connector-python |
| Security | bcrypt (password hashing), python-dotenv (credentials in `.env`) |
| Reports | fpdf2 (PDF), CSV export, openpyxl (Excel input) |

## Prerequisites

- Python 3.10 or newer
- Git
- MySQL 8 or MariaDB 10.4+ running locally. On Windows, [XAMPP](https://www.apachefriends.org) is the easiest way to get it.

## Quick start

The application lives in the `files` folder of this repository. Run every command below from inside it.

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>/files
```

### 2. Create a virtual environment (recommended)

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If you use conda instead: `conda create -n datapulse python=3.12` then `conda activate datapulse`.

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

The styling was built and tested on **Streamlit 1.51**. If a newer Streamlit version changes how the page looks, install the tested one with `pip install streamlit==1.51.0`.

### 4. Start MySQL

- **XAMPP:** open the XAMPP Control Panel and click **Start** next to MySQL. It should turn green and show port 3306.
- **Other installs:** make sure the MySQL service is running.

### 5. Create the database and the app user

This creates a database called `datapulse` and a user called `datapulse_app`. The tables themselves are created automatically the first time the app connects.

**Option A, phpMyAdmin (XAMPP):**

1. Open <http://localhost/phpmyadmin>.
2. Click the **SQL** tab.
3. Paste the contents of `setup_database.sql` and click **Go**.

**Option B, command line:**

```bash
mysql -u root -p < setup_database.sql
```

With XAMPP on Windows the `mysql` command is not on your PATH, so use the full path and leave out `-p` if root has no password:

```bash
C:\xampp\mysql\bin\mysql.exe -u root < setup_database.sql
```

The script uses the placeholder password `change_this_password`. That is fine for a local test, but for anything else change it in `setup_database.sql` **before** running the script, and use the same value in the next step.

### 6. Configure the connection

Copy the template and fill in the password you used in step 5.

Windows:

```bash
copy .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

Contents of `.env`:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=datapulse_app
DB_PASSWORD=change_this_password
DB_NAME=datapulse
```

`.env` is listed in `.gitignore`. Never commit it.

### 7. Run the app

```bash
streamlit run app.py
```

Streamlit opens <http://localhost:8501>. In the sidebar, under **System Status**, the **Database** line should read **Connected**.

## First run

1. Click the round button at the top right, choose **Create new account**, then sign in.
2. Go to **Upload** and drop in a CSV or Excel file. You should see "Saved to database (upload #1)".
3. Move through the stages with the sidebar or the **Previous / Next** buttons at the bottom of each page.
4. On **Quality Score & AI Suggestions**, accept or reject suggestions and watch the score change.
5. Open **Dashboard** for the before/after view, then **Reports / Export** to download the files.

To see the stored data, open phpMyAdmin, select the `datapulse` database and browse the `users`, `uploads` and `audit_log` tables.

If MySQL is not running, the app still starts in session-only mode (the sidebar shows **Offline (session only)**), but sign up, sign in and saving will not work.

## Deploying on Streamlit Community Cloud

1. Push the repository to GitHub. `.env` stays out of it because it is git-ignored.
2. Go to [share.streamlit.io](https://share.streamlit.io), click **Create app**, and pick the repository and branch.
3. Set **Main file path** to `files/app.py`. The app lives in the `files` folder, and `requirements.txt` sits next to `app.py`.
4. Under **Advanced settings**, choose a Python version (3.12 or 3.13 both work) and deploy.

### Connecting a database

Streamlit Cloud runs on its own servers, so `localhost` there is not your computer and a local XAMPP database cannot be reached. To enable sign up, sign in and saving on the hosted app:

1. Create a MySQL database that is reachable from the internet (for example a free tier from a hosted-MySQL provider) and run `setup_database.sql` against it.
2. In the app's **Settings → Secrets**, add the connection details as top-level keys:

```toml
DB_HOST = "your-database-host"
DB_PORT = "3306"
DB_USER = "your-database-user"
DB_PASSWORD = "your-database-password"
DB_NAME = "datapulse"
```

3. Save. The app restarts and the sidebar should show **Database: Connected**.

Streamlit exposes top-level secrets as environment variables, so `modules/db.py` reads them the same way it reads `.env`. Never put these values in the repository. If your provider requires an encrypted (SSL) connection, `db.py` needs the matching SSL options added to its connection settings.

Without a database the hosted app runs in session-only mode: profiling, scoring, the dashboard and exports all work, but accounts and saved history do not.

## How the Data Quality Score works

The composite score is a weighted average of four dimensions, each from 0 to 100:

| Dimension | Weight | Measured as |
|-----------|--------|-------------|
| Completeness | 30% | 100 minus the average missing-value percentage |
| Uniqueness | 25% | 100 minus the percentage of duplicate rows |
| Validity | 25% | Share of numeric values within 3 standard deviations of the column mean |
| Consistency | 20% | Share of values matching the expected format (currently email format; 100 if there is no email column) |

The suggestions come from rule-based statistics: missing-value counts, exact duplicate detection and Z-score outlier analysis. They are not produced by a trained machine-learning model, and nothing is changed until you accept it.

## Project structure

```
<your-repo>/
├── .gitignore
├── README.md
└── files/
    ├── app.py                 entry point: theme, sidebar, page routing
    ├── login.py               standalone login page (not used by app.py)
    ├── requirements.txt
    ├── setup_database.sql     creates the database and app user
    ├── .env.example           template for your local credentials
    ├── .streamlit/
    │   └── config.toml
    ├── modules/
    │   ├── db.py              MySQL access layer (users, uploads, audit log)
    │   ├── theme.py           dark theme, sidebar, dialogs, footer navigation
    │   ├── quality.py         detection rules, suggestions, quality score
    │   ├── reports.py         PDF and CSV export
    │   └── mock_data.py       sample dataset generator
    └── pages/
        ├── upload.py
        ├── data_profiling.py
        ├── quality_score.py
        ├── dashboard.py
        └── reports.py
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Sidebar says **Offline (session only)** | Check that MySQL is running, that the password in `.env` matches the one in `setup_database.sql`, and that you restarted `streamlit run` after editing `.env`. The file is only read at startup. |
| `Access denied for user 'datapulse_app'` | The user was not created, or the password differs. Run `setup_database.sql` again and make `.env` match. |
| `ModuleNotFoundError: No module named 'modules'` | You are not inside the `files` folder. `cd` into it and run the command again. |
| `ModuleNotFoundError` for `mysql`, `bcrypt` or `dotenv` | Run `pip install -r requirements.txt` in the same environment you start Streamlit from. |
| phpMyAdmin shows `#1046 No database selected` after running the script | Harmless. If the other boxes are green and `datapulse` appears in the left list, the setup worked. |
| The hosted app shows **Offline (session only)** | The cloud cannot reach a database on your own machine. Connect a hosted MySQL database and add its details under **Settings → Secrets** (see the deployment section). |
| The hosted app looks different from local | Pin the tested version by setting the first line of `requirements.txt` to `streamlit==1.51.0`, push, and reboot the app. |
| Port 8501 is already in use | `streamlit run app.py --server.port 8502` |
| The page looks unstyled after an update | Hard refresh with Ctrl+Shift+R, or open the app in a private window. |

## Current scope and limitations

- The **Upload** page reads your actual file and stores its summary in MySQL. The later stages (Profiling, Quality Score, Dashboard, Reports) currently run on a generated sample dataset keyed to the dataset name, so the whole pipeline can be demonstrated consistently. Running the engine on the uploaded file's own rows is the next planned step.
- Cleaned data is held in the session while the app runs. MySQL stores accounts, upload records and the audit log.
- Audit log entries identify the dataset by filename. The `upload_id` link exists in the schema but is not populated yet.

## Planned enhancements

- Run the full pipeline on the uploaded file's real data and keep cleaned files
- Isolation Forest outlier detection (scikit-learn) and fuzzy near-duplicate matching (RapidFuzz)
- Schema validation and format-consistency checks for dates, phone numbers and text
- Role-based access and per-user history
- Cloud deployment with a hosted MySQL database