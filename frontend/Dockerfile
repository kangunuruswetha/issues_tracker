# Use a Node.js image with npm for building SvelteKit
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (if you have one)
# to install dependencies
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the SvelteKit application for production (if needed, though we're using dev server for now)
# RUN npm run build

# Expose the port SvelteKit's dev server runs on
EXPOSE 5173

# Command to run the SvelteKit development server
# This command is overridden by docker-compose.yml's 'command' for the frontend service
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]