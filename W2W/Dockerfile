FROM python:3.9-slim

# Install dependencies
RUN pip install streamlit

# Copy the Python application
COPY single_page_app.py /app/single_page_app.py

# Set the working directory
WORKDIR /app

# Expose the Streamlit default port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "single_page_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
