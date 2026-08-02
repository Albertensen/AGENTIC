"""
image_tools.py — Tool pencarian gambar nyata untuk CrewAI ebook.

Menggunakan Wikimedia Commons API (gratis, tanpa API key).
Tool otomatis mencoba beberapa variasi kata kunci agar selalu menemukan gambar.
Return tautan Markdown siap semat: ![Judul](url)
"""

import json
import time
import urllib.parse
import urllib.request

from crewai.tools import BaseTool

API_URL = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "CrewAI-Ebook/1.0 (ebook image search; contact: local project)"


class WikimediaImageSearchTool(BaseTool):
    name: str = "wikimedia_image_search_tool"
    description: str = (
        "Cari gambar ASLI (foto/ilustrasi nyata) di Wikimedia Commons berdasarkan "
        "kata kunci dan kembalikan daftar tautan Markdown siap semat untuk ebook. "
        "Tool ini otomatis mencoba beberapa variasi kata kunci (termasuk tanpa kata 'game', "
        "nama umum, dan istilah bahasa Inggris). Gunakan tool ini di SETIAP bab untuk "
        "menyematkan gambar nyata, bukan placeholder."
    )
    args: dict = {
        "query": {"type": str, "required": True, "description": "Kata kunci pencarian gambar (bahasa Inggris lebih baik hasilnya)"},
        "limit": {"type": int, "default": 6, "description": "Jumlah gambar maksimal per query (default 6)"},
        "width": {"type": int, "default": 800, "description": "Lebar thumbnail dalam piksel (default 800)"},
    }

    def _fetch(self, url: str) -> dict:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _search(self, query: str, limit: int, width: int) -> list:
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": f"{query} filetype:bitmap",
            "gsrnamespace": "6",
            "gsrlimit": str(limit * 3),  # ambil lebih banyak, filter di bawah
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": str(width),
            "format": "json",
        }
        url = f"{API_URL}?{urllib.parse.urlencode(params)}"
        data = self._fetch(url)
        pages = (data.get("query") or {}).get("pages") or {}
        results = []
        # kata kunci untuk filter relevansi
        keywords = [w for w in query.lower().split() if len(w) > 3]
        for page in pages.values():
            info = (page.get("imageinfo") or [{}])[0]
            thumb = info.get("thumburl") or info.get("url")
            if not thumb:
                continue
            meta = info.get("extmetadata") or {}
            title = (meta.get("ImageDescription") or {}).get("value") or page.get("title", "")
            title = title.replace("<p>", "").replace("</p>", "").strip()
            # filter: title harus mengandung salah satu kata kunci (relevan)
            title_low = title.lower()
            if keywords and not any(k in title_low for k in keywords):
                continue
            results.append({"title": title, "url": thumb})
            if len(results) >= limit:
                break
        return results

    def _build_variants(self, query: str) -> list:
        """Buat variasi kata kunci agar pencarian lebih mungkin menemukan gambar."""
        q = query.strip()
        variants = [q]
        # hilangkan kata 'game'/'games' karena sering bikin hasil kosong di Wikimedia
        for word in ("game ", "games ", "the game ", "video game "):
            if q.lower().startswith(word):
                variants.append(q[len(word):].strip())
        # kata tunggal terakhir sebagai fallback
        words = [w for w in q.split() if w.lower() not in ("game", "games", "the", "a", "an", "of", "and")]
        if len(words) > 1:
            variants.append(" ".join(words[-2:]))
            variants.append(words[-1])
        # fallback relevan untuk topik populer (bukan kata generik)
        topic = q.lower()
        if "palworld" in topic:
            variants.extend(["pocketpair", "palworld entertainment", "palworld logo", "palworld official art"])
        elif "corgi" in topic:
            variants.extend(["pembroke welsh corgi", "welsh corgi", "corgi dog"])
        return [v for v in variants if v]

    async def _run(self, query: str, limit: int = 6, width: int = 800):
        try:
            variants = self._build_variants(query)
            last_error = None
            for v in variants:
                try:
                    results = self._search(v, limit, width)
                    if results:
                        lines = [f"Ditemukan {len(results)} gambar untuk query '{v}':"]
                        for i, r in enumerate(results, 1):
                            caption = r["title"][:120] if r["title"] else f"Gambar {i}"
                            lines.append(f"{i}. ![Gambar {i}: {caption}]({r['url']})")
                        return "\n".join(lines)
                    last_error = f"Tidak ada hasil untuk '{v}'"
                except Exception as e:
                    last_error = f"Error query '{v}': {e}"
                    if "429" in str(e):
                        # rate limited — tunggu lalu lanjut ke variasi berikutnya
                        time.sleep(5)
                        continue
                time.sleep(3)  # jeda antar query anti-rate-limit (Wikimedia ketat)
            return f"ERROR: Gagal menemukan gambar untuk '{query}' (dicoba: {', '.join(variants)}). {last_error}"
        except Exception as e:
            return f"ERROR: Gagal mencari gambar Wikimedia: {e}"
