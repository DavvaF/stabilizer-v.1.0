# Video Stabilizer – Nästa steg

Denna version är förberedd för:
- Exportinställningar
- Förhandsvisning av före/efter-video
- API-baserad stabilisering för att undvika svarta kanter

## Nästa steg
- Implementera `ffmpeg`-driven exportinställning
- Implementera OpenCV-visning av före/efter
- Utforska användning av stabiliseringsmodeller som inte kräver croppning (ex. GANs eller motion smoothing API)

## Starta
```bash
streamlit run app.py
```