FROM python:3.7
COPY . /app
WORKDIR /app
RUN pip install -r /app/requirements.txt
ENTRYPOINT ["python","/app/manage.py"]
CMD ["runserver","0.0.0.0:8000"]
