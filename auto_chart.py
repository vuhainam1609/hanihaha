#!/usr/bin/env python3
"""Lập lá số TỰ ĐỘNG, 1 lệnh từ ngày/giờ/giới -> clean + HTML + PNG.

Mục đích (user 2026-10-26): 100 hay 1000 lá cũng chạy 1 đường duy
nhất, KHÔNG sửa tay từng lá. Muốn sửa gì thì sửa LUẬT trong code
(engine / renderer), chạy lại batch là 1000 lá cùng đổi — không bao
giờ mở từng file clean ra sửa tay nữa.

Dùng:
  Lẻ:   python3 auto_chart.py 2000-06-15 12:00 nam "lá mẫu" [2026] [out_dir]
  Batch: python3 auto_chart.py --csv danh_sach.csv [--xem 2026] [--out out_dir]
    CSV có header: date,time,gender,name[,xem_year]
    vd: 2000-06-15,13:30,nữ,lá mẫu,2026

Mỗi lá xuất 3 file vào out_dir (mặc định là thư mục hiện tại):
  <slug>_clean.txt, la-so-<slug>.html, la-so-<slug>.png
PNG cần gói playwright (`pip install playwright --break-system-packages`
+ browser đã có sẵn); thiếu gói thì vẫn xuất clean + HTML và báo rõ,
không làm hỏng cả batch.

Báo cáo batch: ghi batch_report.txt trong out_dir, mỗi lá 1 dòng
gồm các điểm ĐẶC BIỆT phát hiện tự động (không phải lỗi, chỉ để
soát nhanh): sinh 23h (âm lịch tính sang ngày hôm sau), Tuần =
Triệt cùng cặp, tuổi xem còn trước đại vận đầu. Lá không có điểm
đặc biệt thì ghi "—".

Quy tắc lấy từ code hiện có, không viết lại luật:
  - An sao: phu_tinh.full_chart (đã gồm LN.Văn Tinh theo can).
  - Cân lượng: render_chart_html.tinh_can_luong (renderer cũng dùng
    đúng hàm này, nên clean và HTML không bao giờ lệch nhau).
  - Grade Thiên Phủ/Lộc Tồn thiếu trong bảng engine: gen_clean đã
    bù bằng bảng trong code (SAMPLE_GRADES), không phải
    sửa tay từng lá.
"""
import csv
import datetime
import importlib.util
import os
import re
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def slugify(name):
    s = unicodedata.normalize("NFD", name)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "D").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "la-so"


def export_png(html_path, png_path, pg=None):
    """Chụp #horoscope-comp bằng Playwright headless. Trả về (ok, msg).
    Batch truyền pg sẵn để dùng chung 1 browser (1000 lá không mở
    1000 lần browser); lẻ thì tự mở/đóng."""
    own = pg is None
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False, "thiếu gói playwright (pip install playwright --break-system-packages)"
    pw = None
    if own:
        pw = sync_playwright().start()
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 900, "height": 1400},
                        device_scale_factor=2)
    # HTML tham chiếu tương đối assets/Trongdong.webp (watermark trống
    # đồng). Chụp từ thư mục khác (vd tmp) mà ở đó không có assets/ thì
    # ảnh mất watermark mà không báo lỗi — đúng lỗi PNG v5 ngày 26/10.
    # Tự copy assets/ từ thư mục chứa script sang thư mục chứa HTML khi
    # thiếu, trước khi chụp.
    html_dir = os.path.dirname(os.path.abspath(html_path))
    script_assets = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "assets")
    if (not os.path.exists(os.path.join(html_dir, "assets", "Trongdong.webp"))
            and os.path.exists(os.path.join(script_assets, "Trongdong.webp"))):
        import shutil
        shutil.copytree(script_assets, os.path.join(html_dir, "assets"),
                        dirs_exist_ok=True)
    pg.goto("file://" + os.path.abspath(html_path))
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready.then(()=>{})")
    pg.wait_for_timeout(500)
    pg.locator("#horoscope-comp").screenshot(path=png_path)
    if own:
        b.close()
        pw.stop()
    return True, ""


def run_one(date, time_, gender, name, xem_year, out_dir, pg=None):
    """Chạy 1 lá. Trả về dict {slug, files..., anomalies, error}."""
    slug = slugify(name)
    os.makedirs(out_dir, exist_ok=True)
    clean = os.path.join(out_dir, f"{slug}_clean.txt")
    html = os.path.join(out_dir, f"la-so-{slug}.html")
    png = os.path.join(out_dir, f"la-so-{slug}.png")

    # Cân lượng + điểm đặc biệt: tính thẳng từ engine, không đọc tay.
    phu = _load("phu_tinh_auto", os.path.join(HERE, "phu_tinh.py"))
    rch = _load("rch_auto", os.path.join(HERE, "render_chart_html.py"))
    fc = phu.full_chart(date, time_, gender)
    eng, inp = fc["engine"], fc["inp"]
    can_luong = rch.tinh_can_luong(
        f"{inp['year_stem']} {inp['year_branch']}",
        inp["month"], inp["day"], inp["hour_branch"])
    anomalies = []
    if int(time_.split(":")[0]) == 23:
        anomalies.append("sinh 23h: âm lịch tính sang ngày hôm sau")
    if set(eng["tuan"]) == set(eng["triet"]):
        anomalies.append("Tuần = Triệt cùng cặp "
                         f"({'–'.join(sorted(eng['tuan']))})")
    dv_start = eng["dai_van"][eng["menh"]]
    # Tuổi mụ theo cách gen_clean tính (năm xem - năm âm + 1).
    from lich_vn import S2L
    import datetime as _dt
    yy, mm, dd = map(int, date.split("-"))
    _hh = int(time_.split(":")[0])
    _sd = _dt.date(yy, mm, dd) + (_dt.timedelta(days=1) if _hh == 23
                                  else _dt.timedelta(0))
    age = xem_year - S2L(_sd.day, _sd.month, _sd.year)[2] + 1
    if age < dv_start:
        anomalies.append(f"tuổi {age} còn trước đại vận đầu ({dv_start})")

    r = subprocess.run([sys.executable,
                        os.path.join(HERE, "gen_clean_from_engine.py"),
                        date, time_, gender, name, str(xem_year),
                        clean, can_luong],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return {"slug": slug, "error": f"gen_clean lỗi: {r.stderr.strip()}"}
    r = subprocess.run([sys.executable,
                        os.path.join(HERE, "render_chart_html.py"),
                        clean, html], capture_output=True, text=True)
    if r.returncode != 0:
        return {"slug": slug, "error": f"render lỗi: {r.stderr.strip()}"}
    ok, msg = export_png(html, png, pg=pg)
    res = {"slug": slug, "clean": clean, "html": html,
           "png": png if ok else None,
           "anomalies": anomalies, "error": None if ok else f"PNG: {msg}"}
    return res


def main():
    args = sys.argv[1:]
    xem_default, out_dir, csv_path = datetime.date.today().year, ".", None
    pos = []
    i = 0
    while i < len(args):
        if args[i] == "--csv":
            csv_path = args[i + 1]
            i += 2
        elif args[i] == "--xem":
            xem_default = int(args[i + 1])
            i += 2
        elif args[i] == "--out":
            out_dir = args[i + 1]
            i += 2
        else:
            pos.append(args[i])
            i += 1
    rows = []
    if csv_path:
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append((row["date"].strip(), row["time"].strip(),
                             row["gender"].strip(), row["name"].strip(),
                             int((row.get("xem_year") or xem_default))))
    else:
        if len(pos) < 4:
            print("Dùng: auto_chart.py <date> <time> <gender> <name> "
                  "[xem_year] [out_dir]  hoặc  --csv file.csv", file=sys.stderr)
            return 2
        xem = int(pos[4]) if len(pos) > 4 else xem_default
        out_dir = pos[5] if len(pos) > 5 else out_dir
        rows = [(pos[0], pos[1], pos[2], pos[3], xem)]
    results = []
    pg = None
    pw = br = None
    if len(rows) > 1:
        try:
            from playwright.sync_api import sync_playwright
            pw = sync_playwright().start()
            br = pw.chromium.launch()
            pg = br.new_page(viewport={"width": 900, "height": 1400},
                             device_scale_factor=2)
        except ImportError:
            pg = None  # run_one sẽ báo thiếu gói ở từng lá
    for date, time_, gender, name, xem in rows:
        res = run_one(date, time_, gender, name, xem, out_dir, pg=pg)
        results.append((name, res))
        status = f"OK {res['slug']}" if not res["error"] else f"LỖI {res['error']}"
        ano = "; ".join(res.get("anomalies") or []) or "—"
        print(f"{name}: {status} | đặc biệt: {ano}")
    if csv_path or len(rows) > 1:
        report = os.path.join(out_dir, "batch_report.txt")
        with open(report, "w", encoding="utf-8") as f:
            for name, res in results:
                ano = "; ".join(res.get("anomalies") or []) or "—"
                err = f" | LỖI: {res['error']}" if res["error"] else ""
                f.write(f"{name} ({res['slug']}): {ano}{err}\n")
        print(f"Đã ghi {report}")
    return 0 if all(not r["error"] for _, r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
