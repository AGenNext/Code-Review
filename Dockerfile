FROM nginx:alpine

# Security: Run as non-root user
RUN addgroup -g 101 -S appgroup && \
    adduser -u 101 -S appuser -G appgroup

# Copy custom nginx config with security headers
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy website files with proper permissions
COPY --chown=appuser:appgroup index.html /usr/share/nginx/html/index.html

# Set ownership
RUN chown -R appuser:appgroup /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]