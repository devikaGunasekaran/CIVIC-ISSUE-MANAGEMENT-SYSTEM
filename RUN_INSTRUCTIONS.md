# HOW TO RUN THE PROJECT 🚀

Follow these steps to start both the Backend (FastAPI) and Frontend (React/Vite).

---

## **1. BACKEND SETUP (Terminal 1)**

You have already activated the virtual environment. Now run these commands:

### **Install Dependencies** (If not already done)
```powershell
pip install -r backend/requirements.txt
```

### **Initialize Database** (Optional - if first time)
```powershell
python backend/create_db.py
python backend/seed_chennai_admins.py
```

### **Start the Backend Server**
```powershell
python -m uvicorn backend.main:app --reload
```
*   **API will be available at**: `http://localhost:8000`
*   **Swagger Docs**: `http://localhost:8000/docs`

---

## **2. FRONTEND SETUP (Terminal 2)**

Open a **new terminal** and run these commands:

### **Go to Frontend Folder**
```powershell
cd frontend
```

### **Install Dependencies** (If not already done)
```powershell
npm install
```

### **Start the Frontend Server**
```powershell
npm run dev
```
*   **WebApp will be available at**: `http://localhost:5173` (or indicated in terminal)

---

## **3. ADMIN ACCESS (Testing)**

If you ran the seed script, you can login with these accounts:

*   **Super Admin**: `admin` / `admin123`
*   **Anna Nagar Admin**: `annanagar_admin` / `admin123`
*   **T Nagar Admin**: `tnagar_admin` / `admin123`

---

## **💡 PRO TIP**
Keep both terminals open. If you change any AI Agent code, the backend will auto-restart!
