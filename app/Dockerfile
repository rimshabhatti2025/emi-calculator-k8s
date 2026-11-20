# Official lightweight Node.js image
FROM node:20-alpine

# Set working directory
WORKDIR /usr/src/app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install --omit=dev

# Copy the rest of the application code
COPY . .

# Create a non-root user and change ownership
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN chown -R appuser:appgroup /usr/src/app
USER appuser

# Expose port and start the app
EXPOSE 80
CMD ["node", "server.js"]
