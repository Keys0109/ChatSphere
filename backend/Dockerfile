FROM python:3.13

WORKDIR /backend

COPY ./backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./backend/app /backend/app

COPY ./backend/main.py /backend/main.py

COPY ./backend/.env /backend/.env

EXPOSE 8000

CMD ["python", "main.py"]