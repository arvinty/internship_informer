import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import hashlib

import psycopg2
from psycopg2.extras import RealDictCursor
import aiohttp
from telegram import Bot
from telegram.error import TelegramError
from playwright.async_api import async_playwright, Browser, Page

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InternJobBot:
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.db_url = os.getenv('DATABASE_URL')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '300'))  # 5 minutes default

        if not all([self.telegram_token, self.chat_id, self.db_url]):
            raise ValueError("Missing required environment variables: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DATABASE_URL")

        self.bot = Bot(token=self.telegram_token)
        self.jobs_url = "https://www.internsg.com/jobs/?f_0=1&f_p=107&f_i=&filter_s=intern"
        self.db_conn = None

    def get_db_connection(self):
        """Create database connection from DATABASE_URL"""
        try:
            self.db_conn = psycopg2.connect(self.db_url)
            logger.info("Database connection established")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def close_db_connection(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()
            logger.info("Database connection closed")

    def init_database(self):
        """Initialize database tables if they don't exist"""
        try:
            with self.db_conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        id SERIAL PRIMARY KEY,
                        job_hash VARCHAR(255) UNIQUE NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        company VARCHAR(255) NOT NULL,
                        description TEXT,
                        url VARCHAR(500) NOT NULL,
                        seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notified BOOLEAN DEFAULT FALSE,
                        notified_at TIMESTAMP
                    )
                """)
                self.db_conn.commit()
                logger.info("Database tables initialized")
        except psycopg2.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def scrape_jobs(self) -> List[Dict]:
        """Scrape jobs from internsg.com using Playwright"""
        jobs = []
        browser = None

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                logger.info(f"Fetching jobs from {self.jobs_url}")
                await page.goto(self.jobs_url, wait_until='networkidle')

                # Wait for job listings to load
                try:
                    await page.wait_for_selector('[class*="job"]', timeout=10000)
                except Exception as e:
                    logger.warning(f"Job selector not found: {e}")

                # Extract job listings - adjust selectors based on actual website structure
                job_elements = await page.query_selector_all('article, [class*="job-card"], [class*="listing"]')

                if not job_elements:
                    logger.warning("No job elements found. Trying alternative selectors...")
                    job_elements = await page.query_selector_all('div[class*="item"], li[class*="job"]')

                logger.info(f"Found {len(job_elements)} job elements")

                for idx, element in enumerate(job_elements):
                    try:
                        # Try to extract common job posting fields
                        title = await element.query_selector('h2, h3, [class*="title"]')
                        company = await element.query_selector('[class*="company"], [class*="employer"]')
                        link = await element.query_selector('a')

                        title_text = await title.text_content() if title else f"Job {idx}"
                        company_text = await company.text_content() if company else "Unknown Company"
                        url = await link.get_attribute('href') if link else ""

                        if not url.startswith('http'):
                            url = f"https://www.internsg.com{url}" if url.startswith('/') else ""

                        if title_text and url:
                            job = {
                                'title': title_text.strip(),
                                'company': company_text.strip(),
                                'url': url,
                                'description': f"{company_text} - {title_text}"
                            }
                            jobs.append(job)

                    except Exception as e:
                        logger.debug(f"Error extracting job {idx}: {e}")
                        continue

                await browser.close()
                logger.info(f"Successfully scraped {len(jobs)} jobs")

        except Exception as e:
            logger.error(f"Error scraping jobs: {e}")
            if browser:
                await browser.close()

        return jobs

    def get_job_hash(self, job: Dict) -> str:
        """Generate hash for job to detect duplicates"""
        job_str = f"{job['title']}{job['company']}{job['url']}"
        return hashlib.md5(job_str.encode()).hexdigest()

    def is_job_new(self, job: Dict) -> bool:
        """Check if job is new in database"""
        job_hash = self.get_job_hash(job)

        try:
            with self.db_conn.cursor() as cur:
                cur.execute("SELECT id FROM jobs WHERE job_hash = %s", (job_hash,))
                result = cur.fetchone()
                return result is None
        except psycopg2.Error as e:
            logger.error(f"Error checking if job is new: {e}")
            return True

    def add_job_to_db(self, job: Dict) -> bool:
        """Add new job to database"""
        job_hash = self.get_job_hash(job)

        try:
            with self.db_conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO jobs (job_hash, title, company, description, url, notified)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (job_hash) DO NOTHING
                """, (job_hash, job['title'], job['company'], job['description'], job['url'], False))
                self.db_conn.commit()
                return cur.rowcount > 0
        except psycopg2.Error as e:
            logger.error(f"Error adding job to database: {e}")
            return False

    def mark_job_notified(self, job: Dict):
        """Mark job as notified"""
        job_hash = self.get_job_hash(job)

        try:
            with self.db_conn.cursor() as cur:
                cur.execute("""
                    UPDATE jobs SET notified = TRUE, notified_at = CURRENT_TIMESTAMP
                    WHERE job_hash = %s
                """, (job_hash,))
                self.db_conn.commit()
        except psycopg2.Error as e:
            logger.error(f"Error marking job as notified: {e}")

    async def send_notification(self, job: Dict) -> bool:
        """Send Telegram notification for new job"""
        try:
            message = f"""
🎯 **New Internship Posted!**

**Title:** {job['title']}
**Company:** {job['company']}

🔗 [View Job]({job['url']})
"""
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
            logger.info(f"Notification sent for job: {job['title']}")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False

    async def check_for_new_jobs(self):
        """Main job checking loop"""
        while True:
            try:
                logger.info(f"Checking for new jobs at {datetime.now()}")

                # Scrape jobs
                jobs = await self.scrape_jobs()

                if not jobs:
                    logger.warning("No jobs found in scrape")
                    await asyncio.sleep(self.check_interval)
                    continue

                # Process each job
                new_jobs_count = 0
                for job in jobs:
                    if self.is_job_new(job):
                        if self.add_job_to_db(job):
                            new_jobs_count += 1
                            notified = await self.send_notification(job)
                            if notified:
                                self.mark_job_notified(job)

                            # Small delay between notifications to avoid rate limiting
                            await asyncio.sleep(1)

                logger.info(f"Check complete. Found {new_jobs_count} new jobs")

            except Exception as e:
                logger.error(f"Error in check loop: {e}")

            # Wait before next check
            await asyncio.sleep(self.check_interval)

    async def run(self):
        """Start the bot"""
        logger.info("Starting Intern Job Bot")
        self.get_db_connection()
        self.init_database()

        try:
            await self.check_for_new_jobs()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            self.close_db_connection()


async def main():
    bot = InternJobBot()
    await bot.run()


if __name__ == '__main__':
    asyncio.run(main())
