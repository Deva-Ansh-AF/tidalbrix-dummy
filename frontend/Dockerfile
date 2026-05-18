# ── TidalBrix Dummy Frontend ─────────────────────────────────────────────
# The real app is React + Vite (built and served). 
# This dummy serves a single static HTML file via nginx — same container pattern,
# zero node build step needed.
FROM nginx:alpine

LABEL description="TidalBrix dummy frontend — static HTML served by nginx"

# Copy the single-page app
COPY index.html /usr/share/nginx/html/index.html

# nginx config: forward /api/* and other backend paths to the backend container
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=5s \
    CMD wget -qO- http://localhost:80/ || exit 1
