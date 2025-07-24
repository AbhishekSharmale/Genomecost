# Deployment Guide

## Cloudflare Pages Deployment

### Frontend (Angular)
1. **Build Command**: `cd frontend && npm install && npm run build`
2. **Build Output**: `frontend/dist/genomecost-frontend`
3. **Root Directory**: `/` (project root)

### Environment Variables
Set in Cloudflare Pages dashboard:
- `NODE_VERSION`: `18`
- `NPM_VERSION`: `9`

### Custom Domain
Configure your domain in Cloudflare Pages settings.

## Backend Deployment (Railway)
1. Connect Railway to your Git repository
2. Set build command: `cd backend && pip install -r requirements.txt`
3. Set start command: `cd backend && uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

### Environment Variables for Backend
```
DATABASE_URL=your_postgresql_url
AZURE_CLIENT_ID=your_azure_client_id
AZURE_CLIENT_SECRET=your_azure_client_secret
AZURE_TENANT_ID=your_azure_tenant_id
SECRET_KEY=your_jwt_secret_key
```

## Git Commands
```bash
git init
git add .
git commit -m "Initial commit: GenomeCostTracker"
git branch -M main
git remote add origin https://github.com/yourusername/genomecost-tracker.git
git push -u origin main
```