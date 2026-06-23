from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json, os, io
from schemas import DynamicRecommendation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

router = APIRouter()
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "output", "violations.json")

@router.get("/recommendation", response_model=DynamicRecommendation)
def get_recommendation():
    if not os.path.exists(DATA_PATH): return {"vehicle": "N/A", "message": "Clear", "score": 0, "severity": "None", "impact_lanes": 0}
    with open(DATA_PATH, "r") as f: violations = json.load(f)
    if not violations: return {"vehicle": "N/A", "message": "Clear", "score": 0, "severity": "None", "impact_lanes": 0}
    
    processed = []
    for v in violations:
        score = round((v["duration"] * 0.5) + (v["impact"] * 0.3) + (v["lane_importance"] * 10 * 0.2), 1)
        severity = "Critical" if score > 35 else ("High" if score > 20 else "Medium")
        processed.append({**v, "score": score, "severity": severity})
        
    highest = max(processed, key=lambda x: x["score"])
    return {
        "vehicle": highest["vehicle"],
        "message": f"Dispatch clearing crew to evict vehicle {highest['vehicle']} immediately.",
        "score": highest["score"],
        "severity": highest["severity"],
        "impact_lanes": highest["lane_importance"]
    }

@router.get("/report")
def generate_report():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    story = [
        Paragraph("PARKPULSE AI SYSTEMS - URBAN COMMAND DISPATCH REPORT", ParagraphStyle('Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#0F172A'))),
        Paragraph("Generated Real-Time Telemetry Audit Report", styles['Normal']),
        Spacer(1, 20)
    ]
    
    with open(DATA_PATH, "r") as f: violations = json.load(f)
    table_data = [["Vehicle ID", "Block Time", "Impact Index", "Lanes Blocked", "Calculated Priority Score"]]
    
    for v in violations:
        score = round((v["duration"] * 0.5) + (v["impact"] * 0.3) + (v["lane_importance"] * 10 * 0.2), 1)
        table_data.append([v["vehicle"], f"{v['duration']}m", f"{v['impact']}%", str(v["lane_importance"]), f"{score} pts"])
        
    t = Table(table_data, colWidths=[110, 100, 110, 100, 130])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 8)
    ]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment;filename=parkpulse_audit.pdf"})
