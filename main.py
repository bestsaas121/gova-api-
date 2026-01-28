"""
GOVA AI Visibility API
Main FastAPI application entry point
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, HttpUrl, field_validator
from typing import Optional
import os
from dotenv import load_dotenv

from app.services.analyzer import analyze_url
from app.email.sender import send_report_email
from app.database.leads import save_lead

load_dotenv()

app = FastAPI(
    title="GOVA AI Visibility API",
    description="Analiza la visibilidad de sitios web para crawlers de IA",
    version="1.0.1",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.1"}

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:4321").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    url: str
    email: EmailStr
    name: Optional[str] = None
    consent: bool
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        return v
    
    @field_validator('consent')
    @classmethod  
    def validate_consent(cls, v):
        if not v:
            raise ValueError('El consentimiento es obligatorio')
        return v


class AnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    score: int
    status: str
    emoji: str
    summary: dict
    breakdown: dict
    recommendations: list
    preview_text: str
    crawlers: dict
    pdf_sent: bool


@app.get("/")
async def root():
    return {
        "message": "GOVA AI Visibility API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_website(request: AnalysisRequest):
    """
    Analiza una URL y devuelve el informe de visibilidad IA.
    También envía el PDF por email y guarda el lead.
    """
    try:
        # Perform analysis
        result = await analyze_url(request.url)
        
        # Save lead to database
        lead_id = await save_lead(
            url=request.url,
            email=request.email,
            name=request.name,
            score=result["score"],
            analysis_data=result
        )
        
        # Send PDF report via email
        pdf_sent = await send_report_email(
            email=request.email,
            name=request.name,
            url=request.url,
            analysis=result
        )
        
        return AnalysisResponse(
            success=True,
            analysis_id=lead_id,
            score=result["score"],
            status=result["status"],
            emoji=result["emoji"],
            summary=result["summary"],
            breakdown=result["breakdown"],
            recommendations=result["recommendations"],
            preview_text=result["preview_text"],
            crawlers=result["crawlers"],
            pdf_sent=pdf_sent
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar la URL: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "message": "Ha ocurrido un error inesperado"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
