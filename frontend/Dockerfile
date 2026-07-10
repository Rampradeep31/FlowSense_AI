FROM node:18-alpine

WORKDIR /app

# Copy package parameters
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy frontend source files
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start Vite dev server bound to host IP for container access
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
