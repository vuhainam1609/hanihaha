#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lắp ráp lá số đầy đủ: khung chính tinh (lap-la-so.py) + phụ tinh
(W1/W2/W3a/W3b trong work_phu_tinh/) + Tứ Hóa + độ sáng + (khi có
W4) sao lưu L./ĐV.

Luật chuẩn: lá số mẫu của user = CHUẨN cao nhất. Các module worker
đã được kiểm chứng trên 10 lá mẫu (xem phu_tinh_diff_report.md);
module này chỉ LẮP RÁP, không tự đặt thêm quy luật nào.
KHÔNG sửa lap-la-so.py hay test_family_charts.py.

Cách dùng:
  from phu_tinh import full_chart
  chart = full_chart("1983-09-16", "09:30", "nam")
  # chart: dict với 'engine' (dict của lap.build_chart),
  # 'phu' {chi: [sao]}, 'hoa' {Hóa: (sao, chi)},
  # 'grades' {(sao, chi): độ sáng}, 'inp' (dict đầu vào worker).
  # Sao lưu (cần work_phu_tinh/w4-luu/luu.py):
  from phu_tinh import luu_for
  luu, dv, labels, tieu_han = luu_for(chart['inp'], 'Bính', 'Ngọ', 44)
"""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.join(HERE, "work_phu_tinh")

CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
       "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# Chuẩn hoá tên sao khi tra cứu (engine ghi 'Tả Phụ', worker W2
# ghi 'Tả Phù' — cùng một sao; xem diff report §8 về Phủ/Phù).
# LƯU Ý 25/10: KHÔNG gộp "Quan Phù" -> "Quan Phủ" nữa — đó là
# 2 sao riêng (Thái Tuế: Quan Phù; Lộc Tồn: Quan Phủ), gộp sẽ
# làm mất 1 sao khi hai vòng trùng cung (lá test Nhâm 1992).
_CANON = {"Tả Phụ": "Tả Phù",
          # Repo gọi "Thiên Riêu", mẫu/engine gọi "Thiên Diêu" (cùng 1 sao);
          # thiếu ánh xạ này làm grades Thiên Diêu luôn MISSING (lộ 2026-10-24 lá THOA).
          "Thiên Riêu": "Thiên Diêu"}


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _lap():
    return _load("lap_la_so", os.path.join(HERE, "lap-la-so.py"))


def _worker_mods():
    mods = []
    for wname, rel in [
            ("W1", os.path.join("w1-loc-thai-tue", "w1.py")),
            ("W2", os.path.join("w2-ma-khoi-xuong", "w2.py")),
            ("W3a", os.path.join("w3a-giai-phuc", "w3a.py")),
            ("W3b", os.path.join("w3b-sat-tinh", "w3b.py"))]:
        path = os.path.join(WORK_DIR, rel)
        if os.path.exists(path):
            mods.append((wname, _load(wname, path)))
    return mods


def canon_gender(g):
    """Chuẩn hóa giới tính về 'nam'/'nữ'.

    BẮT BUỘC vì mọi chỗ quyết chiều vận đều so chuỗi chính xác
    (gender == 'nữ'): CSV/web ghi 'nu' không dấu trước đây lọt qua
    thành chiều nghịch sai lặng, không báo lỗi (phát hiện 27/10 khi
    lá lá mẫu chạy 'nu' ra vận ngược + sao lệch so với 'nữ').
    Giá trị lạ không thuộc bảng thì giữ nguyên để lỗi lộ ra, không
    đoán mò thành một giới."""
    import unicodedata
    s = unicodedata.normalize("NFD", str(g).strip().lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d")
    if s in ("nam", "male", "m"):
        return "nam"
    if s in ("nu", "female", "f"):
        return "nữ"
    return str(g).strip()


def build_inp(lap, solar, time, gender):
    """Từ ngày dương + giờ + giới -> (inp cho worker, chart engine)."""
    gender = canon_gender(gender)
    y, m, d = map(int, solar.split("-"))
    hh, mm = map(int, time.split(":"))
    ys, yb, lm, ld, _day_gz = lap.birth_lunar(y, m, d, hh)
    hb = lap.hour_branch(hh, mm)
    chart = lap.build_chart(ys, yb, lm, ld, hb, gender)
    thuan = (chart["am_duong"] == "Dương" and gender == "nam") or \
            (chart["am_duong"] == "Âm" and gender == "nữ")
    inp = {"year_stem": ys, "year_branch": yb, "month": lm, "day": ld,
           "hour_branch": hb, "gender": gender,
           "menh_branch": chart["menh"], "than_branch": chart["than"],
           "cuc": chart["cuc"], "cuc_num": chart["cuc_num"],
           "tu_vi_branch": chart["tu_vi_used"],
           "thien_phu_branch": chart["thien_phu"],
           "loc_ton_branch": chart["loc_ton"],
           "kinh_branch": chart["kinh"], "da_branch": chart["da"],
           "vong": chart["vong"], "dai_van": chart["dai_van"],
           "cung_of_branch": chart["cung_of_branch"],
           "tu_hoa": chart["tu_hoa"], "tuan": chart["tuan"],
           "triet": chart["triet"], "direction": 1 if thuan else -1,
           "am_duong": chart["am_duong"]}
    return inp, chart


def phu_for(inp, worker_mods=None):
    """Trả về ({chi: [phụ tinh]}, {Hóa: (sao, chi)}).
    Phụ tinh gồm: worker W1/W2/W3a/W3b + Lộc Tồn/Kình/Đà (engine)
    + Tứ Hóa đặt tại cung của sao được hóa."""
    if worker_mods is None:
        worker_mods = _worker_mods()
    phu = {b: [] for b in CHI}

    def put(branch, star):
        if star not in phu[branch]:
            phu[branch].append(star)

    for _wname, mod in worker_mods:
        for b, stars in mod.stars_for(inp).items():
            for s in stars:
                put(b, _CANON.get(s, s))
    chart = inp.get("chart")
    if chart is None:
        raise ValueError("inp thiếu 'chart' (dict của lap.build_chart)")
    put(chart["loc_ton"], "Lộc Tồn")
    put(chart["kinh"], "Kình Dương")
    put(chart["da"], "Đà La")
    # Bản đồ sao -> cung (chính + phụ) để đặt Hóa.
    star_to_branch = {}
    for s, b in chart["stars"].items():
        star_to_branch.setdefault(s, b)
    for b in CHI:
        for s in phu[b]:
            star_to_branch.setdefault(s, b)
    hoa = {}
    for hname, star in chart["tu_hoa"].items():
        star_c = _CANON.get(star, star)
        b = star_to_branch.get(star_c)
        hoa[hname] = (star_c, b)
        if b:
            put(b, hname)
    # LN.Văn Tinh — sao CỐ ĐỊNH theo can năm sinh (Tân Biên §8.33),
    # KHÔNG phải sao lưu năm xem (quyết Admin 25/10, Argon xác nhận):
    # đặt ở tầng Natal (không phải tầng lưu); renderer xếp cột Cát +
    # màu Hỏa nhờ tiền tố LN.; không độ sáng.
    _LN_VAN_TINH = {"Giáp": "Tỵ", "Ất": "Ngọ", "Bính": "Thân",
                    "Đinh": "Dậu", "Mậu": "Thân", "Kỷ": "Dậu",
                    "Canh": "Hợi", "Tân": "Tý", "Nhâm": "Dần",
                    "Quý": "Mão"}
    _ln_branch = _LN_VAN_TINH.get(inp.get("year_stem"))
    if _ln_branch:
        put(_ln_branch, "LN.Văn Tinh")
    return phu, hoa


def do_sang_all(worker_mods=None):
    """{(sao, chi): độ sáng} — bảng repo do W3a chép nguyên.
    Sao repo 'Thiên Riêu' được chuẩn hoá thành 'Thiên Diêu'
    (tên mẫu dùng). Thiên Phủ và Lộc Tồn không có hàng trong
    bảng repo nên vắng mặt (xem diff report)."""
    if worker_mods is None:
        worker_mods = _worker_mods()
    out = {}
    for _wname, mod in worker_mods:
        if hasattr(mod, "do_sang"):
            for (star, b), g in mod.do_sang().items():
                out[(_CANON.get(star, star), b)] = g
    return out


def full_chart(solar, time, gender):
    """Lập lá số đầy đủ từ ngày dương + giờ + giới tính."""
    lap = _lap()
    inp, chart = build_inp(lap, solar, time, gender)
    inp["chart"] = chart
    phu, hoa = phu_for(inp)
    return {"engine": chart, "inp": inp, "phu": phu, "hoa": hoa,
            "grades": do_sang_all()}


def _palace_stem(branch, year_stem):
    """Can cung theo Ngũ Hổ Độn (cùng quy tắc engine palace_stem):
    Giáp/Kỷ -> Bính Dần, Ất/Canh -> Mậu Dần, Bính/Tân -> Canh Dần,
    Đinh/Nhâm -> Nhâm Dần, Mậu/Quý -> Giáp Dần; rồi đếm thuận."""
    dan_stem = {"Giáp": "Bính", "Kỷ": "Bính", "Ất": "Mậu",
                "Canh": "Mậu", "Bính": "Canh", "Tân": "Canh",
                "Đinh": "Nhâm", "Nhâm": "Nhâm", "Mậu": "Giáp",
                "Quý": "Giáp"}[year_stem]
    can_idx = CAN_IDX[dan_stem]
    diff = (CHI.index(branch) - CHI.index("Dần")) % 12
    return CAN_LIST[(can_idx + diff) % 10]


CAN_LIST = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ",
            "Canh", "Tân", "Nhâm", "Quý"]
CAN_IDX = {c: i for i, c in enumerate(CAN_LIST)}


def ln_origin_for(dv_branch, direction, k):
    """Cung gốc LN (cung mang nhãn LN.MỆNH) theo quy luật user mô tả
    2026-10-23 (kèm hình minh họa đường đi LN.Mệnh trong đại vận):
    năm thứ 1 của đại vận: gốc = cung đại vận; năm thứ 2: cung xung
    chiếu (+6); từ năm thứ 3 trở đi: mỗi năm tiến 1 cung theo chiều
    đại vận, bắt đầu bằng 1 bước lùi (ngược chiều đại vận) từ cung
    xung chiếu — tức năm k>=3: gốc = V+6+(k-4)*D (D = +1 thuận,
    -1 nghịch, theo chỉ số chi). Kiểm chứng 2026-10-23: khớp cả 4
    điểm đã biết (user 2026 k=10 -> Sửu, user 2027 k=1 -> Tý, Nhâm
    2026 k=2 -> Dần, Quý 2026 k=8 -> Dậu); chiều thuận (+1) chưa có
    lá trực tiếp, chỉ suy theo đối xứng. Quy luật này khác luật
    tiểu hạn theo prompt (khởi tam hợp) — LN. và tiểu hạn là 2
    khái niệm khác nhau, không dùng chung quy luật."""
    vi = CHI.index(dv_branch)
    if k == 1:
        return dv_branch
    if k == 2:
        return CHI[(vi + 6) % 12]
    return CHI[(vi + 6 + (k - 4) * direction) % 12]


def luu_for(inp, xem_stem, xem_branch, xem_age_mu,
            ln_origin_branch=None):
    """Sao lưu cho một năm xem. Cần work_phu_tinh/w4-luu/luu.py
    (W4); chưa có thì báo lỗi rõ ràng thay vì tính bừa.
    Dịch inp của assembly sang key W4 cần: birth_*, dv_branch/can
    (cung đại vận chứa tuổi xem), star_branch (chính + phụ đã
    tính, đã chuẩn hoá tên). ln_origin_branch: nếu không truyền,
    tự tính theo quy luật LN. của user (ln_origin_for); truyền
    tường minh sẽ ghi đè (dùng khi muốn kiểm tra giả thuyết khác)."""
    path = os.path.join(WORK_DIR, "w4-luu", "luu.py")
    if not os.path.exists(path):
        raise FileNotFoundError(
            "Chưa có module W4 (sao lưu): %s" % path)
    mod = _load("luu", path)
    chart = inp["chart"]
    dv_branch = None
    for br, start in chart["dai_van"].items():
        if start <= xem_age_mu < start + 10:
            dv_branch = br
            break
    if dv_branch is None:
        # Tuổi tiền vận (chưa tới vận đầu): dùng vận đầu cho hiển
        # thị bình thường (quyết Admin 25/10: đừng khắt khe, rối code).
        # Chỉ fallback khi tuổi < vận đầu; tuổi ngoài khoảng khác vẫn lỗi.
        first_start = min(chart["dai_van"].values())
        if xem_age_mu < first_start:
            dv_branch = min(chart["dai_van"],
                            key=lambda br: chart["dai_van"][br])
        else:
            raise ValueError("Không tìm được cung đại vận chứa tuổi %s"
                             % xem_age_mu)
    if ln_origin_branch is None:
        k = xem_age_mu - chart["dai_van"][dv_branch] + 1
        ln_origin_branch = ln_origin_for(dv_branch, inp["direction"], k)
    phu, _hoa = phu_for(inp)
    star_branch = {}
    for s, b in chart["stars"].items():
        star_branch.setdefault(_CANON.get(s, s), b)
    for b in CHI:
        for s in phu[b]:
            star_branch.setdefault(_CANON.get(s, s), b)
    full_inp = {"birth_stem": inp["year_stem"],
                "birth_branch": inp["year_branch"],
                "gender": inp.get("gender"),
                "xem_stem": xem_stem, "xem_branch": xem_branch,
                "dv_branch": dv_branch,
                "dv_can": _palace_stem(dv_branch, inp["year_stem"]),
                "star_branch": star_branch,
                "xem_age_mu": xem_age_mu,
                "ln_origin_branch": ln_origin_branch}
    return mod.luu_stars_for(full_inp)


if __name__ == "__main__":
    import sys
    solar = sys.argv[1] if len(sys.argv) > 1 else "1983-09-16"
    time = sys.argv[2] if len(sys.argv) > 2 else "09:30"
    gender = sys.argv[3] if len(sys.argv) > 3 else "nam"
    fc = full_chart(solar, time, gender)
    ch = fc["engine"]
    print("Mệnh %s%s | Thân cư %s | %s %s cục | Lai nhân %s" % (
        ch["menh_stem"], ch["menh"], ch["than"], ch["cuc"],
        ch["cuc_num"], ch["lai_nhan"]))
    inv = {}
    for s, b in ch["stars"].items():
        inv.setdefault(b, []).append(s)
    for b in CHI:
        cung = {"Tử Nữ": "Tử Tức"}.get(ch["cung_of_branch"][b],
                                         ch["cung_of_branch"][b])
        print("  %s (%s): chính %s | phụ %s | %s | ĐV %s%s%s" % (
            cung, b, ", ".join(inv.get(b, ["(VCD)"])),
            ", ".join(fc["phu"][b]), ch["vong"][b],
            ch["dai_van"][b],
            " Tuần" if b in ch["tuan"] else "",
            " Triệt" if b in ch["triet"] else ""))
    print("Tứ Hóa:", fc["hoa"])
