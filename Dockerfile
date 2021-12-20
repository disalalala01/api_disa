FROM python:3.9
COPY amp-production-cost /app
EXPOSE 5000
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--log-level", "info", "manage:app"]
