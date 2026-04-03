# Data Pipeline & Dashboard Project

Here is the data pipeline and dashboard assignment! I've built a Python script to clean the data, another script to aggregate the analytics, a FastAPI backend to serve the data, and a React frontend to visualize it all.

## How It Works

1. **Python Pipeline**: Extracts raw CSVs, strips out duplicates/garbage, handles missing values, and stitches products and orders together. It does this by running `run_pipeline.py`.
2. **FastAPI**: Acts as a simple layer serving my cleaned CSV files as JSON for the React app.
3. **React UI**: A Vite app spinning up a dashboard utilizing simple modern CSS and Recharts to visualize the data feeds.

## Folder Setup

- `clean_data.py` & `analyze.py`: The brains of the data pipeline.
- `run_pipeline.py`: The single script you can run that triggers both steps.
- `backend/`: Holds `app.py` and the `requirements.txt`.
- `frontend/`: The React code.
- `data/`: Where the raw CSVs live, and where the processed CSVs are dumped after you run the script!

---

## Step-by-Step Setup

Follow these exact steps to get this running locally on your computer.

### Step 1: Install Python dependencies
First, set up a virtual environment so we don't mess up your system Python:

```bash
# create the environment
python -m venv .venv

# activate it (windows)
.\.venv\Scripts\activate

# install packages
pip install -r backend/requirements.txt
```

### Step 2: Run the Data Pipeline
Before you can run the backend or frontend, we need to generate the cleaned data files! Just run this command:

```bash
python run_pipeline.py
```
*You should see some print statements confirming the data was saved.*

### Step 3: Boot the Backend
With the virtual environment still active, run the FastAPI server:

```bash
uvicorn backend.app:app --reload --port 8000
```
*(Leave this terminal window open!)*

### Step 4: Boot the Frontend
Open a **new** terminal window, navigate to the `frontend` folder, and start Vite:

```bash
cd frontend
npm install
npm run dev
```

That's it! Open your browser to `http://localhost:5173` and enjoy the dashboard.

---

### A few notes:
- I've assumed that if an entire product category lacks a price, we fall back to the overall median amount.
- The React charts are all totally responsive.
- If you want to run my unit tests on the data cleaning, you can literally just pip install `pytest` and run `pytest tests/`.
