# Use a Node.js image
FROM node:16

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json first
COPY package.json .
COPY package-lock.json .

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy the entire app after installing dependencies
COPY . .

# Expose the port Vite uses (default 5173)
EXPOSE 3000

# Start Vite
CMD ["npm", "run", "start"]