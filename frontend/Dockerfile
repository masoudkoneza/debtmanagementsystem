# ── Frontend Dockerfile ───────────────────────────────────────────────────────
#
# Builds a Vite dev-server image for the DMS frontend.
# Hot Module Replacement (HMR) works because the source code is mounted as a
# Docker volume in docker-compose.yml — edits on the host are instantly
# reflected inside the container without rebuilding.

FROM node:20-slim

WORKDIR /app

# Install dependencies first so Docker caches this layer.
# Only re-runs when package.json or package-lock.json changes.
COPY package*.json ./
RUN npm install

# Copy source files.
# The volume mount in docker-compose.yml will override this at runtime for
# live reloading, but copying here ensures the image is self-contained
# for CI environments where volumes are not used.
COPY . .

# Expose the Vite dev server port (spec §3.1).
EXPOSE 5173

# Start the Vite dev server, binding to 0.0.0.0 so it is reachable
# from the host at http://localhost:5173.
CMD ["npm", "run", "dev"]
