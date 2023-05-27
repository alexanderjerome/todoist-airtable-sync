# Use official Nginx image
FROM nginx:latest

# Copy the Nginx configuration file into the container
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Replace the placeholder with the actual domain and port number
RUN sed -i 's/TODOIST_DOMAIN_PLACEHOLDER/todoist.'${DOMAIN}'/g' /etc/nginx/conf.d/default.conf
# RUN sed -i 's/__PORT__/'${PORT}'/g' /etc/nginx/conf.d/default.conf

# Make port 443 available to the world outside this container
EXPOSE 443

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
