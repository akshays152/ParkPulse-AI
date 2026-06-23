from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import stats, violations, reports, analyze

app = FastAPI(title="ParkPulse AI Framework")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(stats.router)
app.include_router(violations.router)
app.include_router(reports.router)
app.include_router(analyze.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
