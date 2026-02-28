FROM nginx:alpine

# Delete the default config to be absolutely sure
RUN rm /etc/nginx/conf.d/default.conf

# Copy your perfect config as the new default
COPY nginx.conf /etc/nginx/conf.d/default.conf