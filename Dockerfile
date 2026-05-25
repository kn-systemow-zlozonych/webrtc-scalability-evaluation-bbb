FROM mcr.microsoft.com/playwright:v1.50.0-noble

USER root

WORKDIR /app

RUN npm init -y && \
    npm install playwright@1.50.0

COPY bot.js .

CMD ["node", "bot.js"]