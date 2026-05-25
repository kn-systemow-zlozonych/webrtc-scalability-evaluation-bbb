const { chromium } = require('playwright');
const crypto = require('crypto');
const os = require('os');

const BBB_URL = process.env.BBB_URL;
const BBB_SECRET = process.env.BBB_SECRET;
const BOT_COUNT = parseInt(process.env.BOTS || "1");
const DURATION = parseInt(process.env.DURATION || "60");

if (!BBB_URL || !BBB_SECRET) {
    console.error("ERROR: Missing BBB_URL or BBB_SECRET environment variables!");
    process.exit(1);
}

function getJoinUrl(username) {
    const params = `meetingID=test-docker&fullName=${username}&password=ap&joinViaHtml5=true`;
    const checksum = crypto.createHash('sha1').update(`join${params}${BBB_SECRET}`).digest('hex');
    let baseUrl = BBB_URL.endsWith('/') ? BBB_URL : BBB_URL + '/';
    if (!baseUrl.endsWith('api/')) baseUrl += 'api/';
    baseUrl = baseUrl.replace(/([^:])\/\/+/g, "$1/");
    return `${baseUrl}join?${params}&checksum=${checksum}`;
}

async function startBot(id) {
    const username = `DockerBot-${id}`;
    const isSpeaker = false;

    const browser = await chromium.launch({
        headless: true,
        args: [
            '--use-fake-ui-for-media-stream',
            '--use-fake-device-for-media-stream',
            '--use-file-for-fake-video-capture=/app/media/video.y4m',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--blink-settings=imagesEnabled=false',
            '--disable-extensions'
        ]
    });

    const context = await browser.newContext({ permissions: ['microphone', 'camera'] });
    const page = await context.newPage();

    await page.exposeFunction('getSystemStats', () => {
        return {
            load: os.loadavg()[0].toFixed(2),
            mem: ((os.totalmem() - os.freemem()) / 1024 / 1024 / 1024).toFixed(2) + "GB",
            uptime: Math.floor(os.uptime() / 60) + "m"
        };
    });

    try {
        console.log(`[${username}] 🚪 Joining...`);
        await page.goto(getJoinUrl(username), { waitUntil: 'networkidle' });

        await page.waitForSelector('[data-test="listenOnlyBtn"]', { timeout: 30000 });
        await page.click('[data-test="listenOnlyBtn"]');

        const closeBtn = '[data-test="sessionDetailsModal"] [data-test="closeModal"]';
        try {
            await page.waitForSelector(closeBtn, { timeout: 20000 });
            await page.click(closeBtn);
        } catch (e) {}

        console.log(`[${username}]  Starting webcam...`);
        await page.waitForSelector('[data-test="joinVideo"]', { timeout: 20000 });
        await page.click('[data-test="joinVideo"]');

        const startSharing = '[data-test="startSharingWebcam"]';
        await page.waitForSelector(startSharing, { timeout: 20000 });
        await page.click(startSharing);
        console.log(`[${username}]  STREAMING ACTIVE!`);

        await page.waitForTimeout(DURATION * 1000);
    } catch (e) {
        console.error(`[${username}] ERROR: ${e.message}`);
        await page.screenshot({ path: `/app/media/error-${username}.png` });
    } finally {
        await browser.close();
    }
}

(async () => {
    console.log(`🚀 Starting stress test. Bot count: ${BOT_COUNT}`);
    for(let i=0; i<BOT_COUNT; i++) {
        startBot(i);
        await new Promise(r => setTimeout(r, 20000));
    }
})();