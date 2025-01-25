# Use the official Node.js image
FROM node:16

# Set the working directory
WORKDIR /app/dealership-app/server/cloudant

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY server/cloudant/ .

# Expose the port
EXPOSE 5500

# Start the application
CMD ["node", "app.js"]
