FROM python:3
WORKDIR /app
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 3001
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]
