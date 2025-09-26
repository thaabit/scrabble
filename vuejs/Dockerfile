FROM node:lts-alpine

# make the 'app' folder the current working directory
WORKDIR /vuejs

# copy both 'package.json' and 'package-lock.json' (if available)
COPY package*.json ./

# install project dependencies
RUN npm install

# copy project files and folders to the current working directory (i.e. 'app' folder)
COPY vite-project .

RUN npm run serve

EXPOSE 8080

CMD ["npm", "run", "serve"]
