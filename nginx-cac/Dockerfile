FROM nginx:latest

# Remove the default NGINX configuration file
RUN rm /etc/nginx/conf.d/default.conf

# New nginx configuration file into the container
COPY default.conf /etc/nginx/conf.d/

# Copy server SSL certificates and Root CA + CA chain certificate (combined) certificate into the container
COPY server_cert.pem server_privkey.pem combined.pem /etc/nginx/

# Drectory for demo website
RUN mkdir -p /www/data && chown -R nginx:nginx /www/data

# Expose port 443 for SSL traffic
EXPOSE 443