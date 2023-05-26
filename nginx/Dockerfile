# Use official Nginx image
FROM nginx:latest

# Copy the SSL certificates into the Docker image
COPY ./ssl/domain.crt /etc/nginx/nginx-config/ssl_certs/
COPY ./ssl/domain.key /etc/nginx/nginx-config/ssl_certs/
COPY ./ssl/domain.ca-bundle /etc/nginx/nginx-config/ssl_certs/

# Copy the Nginx configuration file into the container
COPY nginx.conf /etc/nginx/nginx.conf

# Replace the placeholder with the actual domain and port number
RUN sed -i 's/TODOIST_DOMAIN_PLACEHOLDER/todoist.'${DOMAIN}'/g' /etc/nginx/nginx.conf
RUN sed -i 's/__PORT__/'${PORT}'/g' /etc/nginx/nginx.conf

# Make port 80 and 443 available to the world outside this container
EXPOSE 80
EXPOSE 443

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
