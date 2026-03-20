FROM node:8-slim

RUN echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ stretch main contrib non-free" > /etc/apt/sources.list
RUN apt-get update && \
apt-get install -yq gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 \
libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 \
libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 \
libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst ttf-freefont \
ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget
RUN apt install -y fonts-liberation
RUN wget https://github.com/Yelp/dumb-init/releases/download/v1.2.1/dumb-init_1.2.1_amd64.deb && \
dpkg -i dumb-init_*.deb && rm -f dumb-init_*.deb

RUN yarn global add puppeteer@1.8.0
RUN yarn global add express

RUN yarn cache clean
RUN apt-get clean && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

ENV NODE_PATH="/usr/local/share/.config/yarn/global/node_modules:${NODE_PATH}"
RUN yarn config set "strict-ssl" false

ENV LANG="C.UTF-8"

WORKDIR /app

ENTRYPOINT ["dumb-init", "--"]

# CMD ["/usr/local/share/.config/yarn/global/node_modules/puppeteer/.local-chromium/linux-526987/chrome-linux/chrome"]

CMD ["node", "index.js"]
EXPOSE 3000

#docker build -t pdf-download .
#docker rm -f pdf
#docker run -d --shm-size 1G --rm -v $PWD/pdf.js:/app/index.js -e SERVADDR=http://127.0.0.1:9090 -p 3000:3000 --name pdf pdf-download
