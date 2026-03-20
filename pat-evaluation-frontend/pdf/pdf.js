const puppeteer = require('puppeteer');
const express = require('express')
const app = express()
const port = 3000

async function timeout(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

app.get('/download-pdf', (request, response) => {
  (async () => {
    const browser = await puppeteer.launch({
        ignoreHTTPSErrors: true,
        args: [
            '--no-sandbox',
            '--ignore-certificate-errors',
            '--ignore-certificate-errors-spki-list',
            '--disable-setuid-sandbox'
        ]
    });
    const page = await browser.newPage();
    url = 'http://gitlab.intelipev.com:9090/downloadReport?patentId='+request.query.patentId;
    console.log(url, request.query.patentId);
    await page.goto(url, { waitUntil: 'networkidle0' });
    //await timeout(5000);
    await page.evaluate(() => { window.scrollBy(0, window.innerHeight); })
    pdf = await page.pdf({format: 'A4'});
    await browser.close();
    response.contentType('application/pdf');
    response.end(pdf, 'binary');
  })();
})

app.listen(port, (err) => {
  if (err) {
    return console.log('something bad happened', err)
  }
  console.log(`server is listening on ${port}`)
  const addr = process.env.SERVADDR;
  console.log(`Server address is ${addr}`);
})
