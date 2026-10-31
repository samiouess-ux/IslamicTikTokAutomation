"""Send a rendered review MP4 to Telegram; never publish to TikTok."""
from __future__ import annotations
import argparse, json, os, secrets, time, urllib.request, urllib.error
from pathlib import Path
MAX_VIDEO_BYTES = 50 * 1024 * 1024

def build_caption(data: dict) -> str:
    parts = [str(data.get("arabic_caption", "")).strip(), " ".join(data.get("hashtags_ar", [])), str(data.get("english_caption", "")).strip(), " ".join(data.get("hashtags_en", [])), "للمراجعة فقط — لم يتم النشر على TikTok. النشر يدوي بعد مراجعتك."]
    caption = "\n\n".join(part for part in parts if part)
    if len(caption) > 1024: raise ValueError(f"Telegram caption exceeds 1024 characters ({len(caption)}).")
    return caption

def send_video(video_path: Path, caption_path: Path, token: str, chat_id: str) -> dict:
    if not token.strip() or not chat_id.strip(): raise ValueError("Both TG_BOT_TOKEN and TELEGRAM_CHAT_ID must be configured as GitHub Secrets.")
    if not video_path.is_file() or video_path.stat().st_size == 0: raise FileNotFoundError(f"Review MP4 is missing or empty: {video_path}")
    size = video_path.stat().st_size
    if size > MAX_VIDEO_BYTES: raise ValueError(f"Review MP4 is {size / (1024 * 1024):.1f} MB; Telegram sendVideo limit is 50 MB.")
    caption = build_caption(json.loads(caption_path.read_text(encoding="utf-8")))
    boundary = "----IslamicTikTok" + secrets.token_hex(16)
    chunks = []
    for name, value in [("chat_id", chat_id), ("caption", caption), ("supports_streaming", "true")]:
        chunks.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode("utf-8"))
    chunks.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"video\"; filename=\"{video_path.name}\"\r\nContent-Type: video/mp4\r\n\r\n".encode("utf-8"))
    chunks.extend([video_path.read_bytes(), f"\r\n--{boundary}--\r\n".encode("ascii")])
    body = b"".join(chunks)
    url = f"https://api.telegram.org/bot{token.strip()}/sendVideo"
    result = None
    delays = (5, 15, 30)
    for attempt in range(len(delays) + 1):
        request = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                result = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            retryable = exc.code == 429 or 500 <= exc.code <= 599
            if not retryable or attempt == len(delays):
                raise
            retry_after = exc.headers.get("Retry-After")
            wait = max(int(retry_after), delays[attempt]) if retry_after and retry_after.isdigit() else delays[attempt]
            print(f"Telegram returned HTTP {exc.code}; retrying in {wait}s (attempt {attempt + 2}/4).")
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            if attempt == len(delays):
                raise
            wait = delays[attempt]
            print(f"Telegram network error: {exc}; retrying in {wait}s (attempt {attempt + 2}/4).")
            time.sleep(wait)
    if result is None:
        raise RuntimeError("Telegram delivery failed after four attempts.")
    if not result.get("ok") or not isinstance(result.get("result"), dict): raise RuntimeError("Telegram API did not confirm delivery.")
    message = result["result"]
    print(f"Telegram confirmed delivery: message_id={message.get('message_id')}, size_mb={size / (1024 * 1024):.1f}. TikTok publishing remains manual.")
    return message

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--video", type=Path, required=True); parser.add_argument("--caption", type=Path, required=True); args = parser.parse_args()
    send_video(args.video, args.caption, os.environ.get("TG_BOT_TOKEN", ""), os.environ.get("TELEGRAM_CHAT_ID", ""))

if __name__ == "__main__": main()
