# Koyeb deployment checklist

## 1. Push the repo to GitHub

Ensure the current workspace is pushed to the repository that Koyeb will import.

## 2. Create a Koyeb web service

- Open Koyeb dashboard
- Click Create Service
- Choose Import from GitHub
- Select the repository: Mugo-Samuel/Data-Analysis-Copilot
- Choose branch: main
- Set service type: Web Service
- Use the Dockerfile method or the built-in Docker setup

## 3. Use the correct runtime

The project includes:
- Dockerfile
- koyeb.yaml
- requirements.txt

The app is started with Gunicorn and binds to port 8000.

## 4. Domain setup

- Attach the custom domain: www.omisbots.site
- Confirm DNS is pointed to the Koyeb generated URL
- Wait for certificate issuance

## 5. Redeploy after linking the domain

If the site still shows the old page, the service is probably still attached to a different repo or older deployment.

Redeploy the current service after attaching the domain and confirm the app responds on the Koyeb URL.

## 6. Verify the live app

Check the deployed homepage and confirm it matches the current Omisbots app, not the older marketing page.

## Production entry point

The app is served by:

- webapp.py
- gunicorn webapp:app

This is already configured for Koyeb deployment.
