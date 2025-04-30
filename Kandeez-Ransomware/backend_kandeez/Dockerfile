FROM node:18

# Set working directory
WORKDIR /app

# Copy package.json and install deps
COPY package*.json ./
RUN npm install

# Copy the entire backend code
COPY . .

# Expose backend port
EXPOSE 5000

# Run your backend app
CMD ["node", "server.js"]
