import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO = os.environ["GITHUB_REPO"]  # owner/repo
WORKFLOW_FILE = os.getenv("WORKFLOW_FILE", "rdp.yml")

API = "https://api.github.com"

def gh_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "RDP Bot\n\n"
        "/create - jalankan workflow RDP\n"
        "/status - cek workflow terakhir\n"
        "/help - bantuan"
    )

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Restrict the bot to an optional allowlist.
    allowed = os.getenv("ALLOWED_CHAT_IDS", "").strip()
    if allowed:
        ids = {x.strip() for x in allowed.split(",") if x.strip()}
        if str(update.effective_chat.id) not in ids:
            await update.message.reply_text("Chat ID ini tidak diizinkan.")
            return

    url = f"{API}/repos/{GITHUB_REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    payload = {"ref": "main"}

    r = requests.post(url, headers=gh_headers(), json=payload, timeout=20)

    if r.status_code == 204:
        await update.message.reply_text(
            "Workflow RDP berhasil dijalankan.\n"
            "Tunggu sampai Windows runner dan Tailscale siap. "
            "Gunakan /status untuk melihat status."
        )
    else:
        await update.message.reply_text(
            f"Gagal menjalankan workflow.\nHTTP {r.status_code}\n{r.text[:500]}"
        )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"{API}/repos/{GITHUB_REPO}/actions/workflows/{WORKFLOW_FILE}/runs"
    r = requests.get(
        url,
        headers=gh_headers(),
        params={"per_page": 1},
        timeout=20,
    )

    if r.status_code != 200:
        await update.message.reply_text(
            f"Gagal mengambil status.\nHTTP {r.status_code}\n{r.text[:500]}"
        )
        return

    runs = r.json().get("workflow_runs", [])
    if not runs:
        await update.message.reply_text("Belum ada workflow yang dijalankan.")
        return

    run = runs[0]
    await update.message.reply_text(
        f"Workflow terakhir:\n"
        f"Status: {run.get('status')}\n"
        f"Kesimpulan: {run.get('conclusion') or '-'}\n"
        f"Run ID: {run.get('id')}\n"
        f"URL: {run.get('html_url')}"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_cmd))
    app.run_polling()

if __name__ == "__main__":
    main()
