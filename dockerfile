FROM python:3.11-alpine

WORKDIR /server

COPY ./requirements.txt /server/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /server/app

EXPOSE 3000

RUN mkdir /server/data

CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "3000"]