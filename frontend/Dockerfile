FROM node:22-alpine

WORKDIR /frontend

COPY ./frontend/package*.json .

RUN npm install

COPY ./frontend/public /frontend/public

COPY ./frontend/src /frontend/src

COPY ./frontend/.env /frontend/.env

EXPOSE 5173

CMD ["npm", "run", "dev"]