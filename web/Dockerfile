FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ENV VITE_API_URL=http://api:8000/api

RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "dev"]
