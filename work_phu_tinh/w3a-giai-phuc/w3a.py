# -*- coding: utf-8 -*-
"""Port phụ tinh Tử Vi — nhóm W3a (Giải / Phúc).

Pure Python, KHÔNG import lap-la-so.py. Mọi quy luật dưới đây đều đã
đối chiếu với 10 lá mẫu trong sample_charts/ (xem RULES.md cùng thư
mục). Nguyên tắc: lá mẫu là chuẩn cao nhất; chỗ nào repo lasotuvi
khác lá mẫu thì theo lá mẫu, và chỗ vênh được ghi rõ trong RULES.md.

Quy ước chỉ số: CHI = [Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân,
Dậu, Tuất, Hợi] (0-11); CAN = [Giáp, Ất, Bính, Đinh, Mậu, Kỷ, Canh,
Tân, Nhâm, Quý] (0-9). Các hàm chấp nhận cả tên và chỉ số cho
year_stem / year_branch / hour_branch / menh_branch / than_branch /
loc_ton_branch, và cả dict cung_of_branch keyed by tên chi hoặc chỉ số.

Hai hàm xuất:
    stars_for(inp) -> {tên chi: [tên sao]}
    do_sang()      -> {(tên sao, tên chi): độ sáng trong {M, V, Đ, H, B}}

Lưu ý về các sao KHÔNG có trong stars_for (xem RULES.md):
  - Lưu Hà: CÓ trong dict, nhưng theo bảng ĐÃ ĐIỀU CHỈNH THEO MẪU
    (Đinh -> Thân, Canh -> Thìn; repo ghi ngược lại). Hai can này mỗi
    can chỉ có 1 lá mẫu, và Bính/Mậu chưa có lá nào (giữ giá trị repo,
    chưa được mẫu xác nhận) — cần thêm lá kiểm chứng trước khi coi
    bảng Lưu Hà là chốt hoàn toàn.
  - Không có sao nào khác trong nhóm W3a bị loại hoàn toàn: mọi hệ
    còn lại đều khớp mẫu 10/10 với quy luật đưa vào đây (kể cả các hệ
    mà repo sai — Thiên Giải, Phá Toái — vì quy luật trong code là
    quy luật suy từ mẫu, không phải quy luật repo).
"""

CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi",
       "Thân", "Dậu", "Tuất", "Hợi"]
CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân",
       "Nhâm", "Quý"]


def _idx(value, table):
    """Tên -> chỉ số; chỉ số -> chính nó (mod len)."""
    if isinstance(value, int):
        return value % len(table)
    return table.index(value)


def _branch_idx(value):
    return _idx(value, CHI)


def _stem_idx(value):
    return _idx(value, CAN)


def _palace_branch(inp, palace_name, fallback_offset):
    """Chi của một cung: ưu tiên cung_of_branch, fallback đếm từ Mệnh.

    Thứ tự cung từ Mệnh đếm nghịch (như engine): Mệnh, Huynh Đệ,
    Phu Thê, Tử Nữ/Tử Tức, Tài Bạch, Tật Ách, Thiên Di, Nô Bộc,
    Quan Lộc, Điền Trạch, Phúc Đức, Phụ Mẫu. Do đó Nô Bộc = Mệnh - 7,
    Tật Ách = Mệnh - 5.
    """
    cung = inp.get("cung_of_branch") or {}
    for key, name in cung.items():
        if name == palace_name:
            return _branch_idx(key)
    menh = _branch_idx(inp["menh_branch"])
    return (menh + fallback_offset) % 12


# --- Bảng tra theo can năm ------------------------------------------------
# Lưu Hà: bảng ĐÃ điều chỉnh theo mẫu (xem module docstring + RULES.md).
#   Repo (timLuuTru): Đinh -> Thìn, Canh -> Thân.
#   Mẫu (lá mẫu Đinh -> Thân, lá mẫu Canh -> Thìn): Đinh -> Thân, Canh -> Thìn.
#   Bính, Mậu: chưa có lá mẫu, giữ giá trị repo, CHƯA được mẫu xác nhận.
LUU_HA = {
    "Giáp": "Dậu", "Ất": "Tuất", "Bính": "Mùi", "Đinh": "Thân",
    "Mậu": "Tỵ", "Kỷ": "Ngọ", "Canh": "Thìn", "Tân": "Mão",
    "Nhâm": "Hợi", "Quý": "Dần",
}

# Thiên Trù: khớp mẫu 10/10. Bính, Mậu chưa có lá mẫu (giữ giá trị repo).
THIEN_TRU = {
    "Giáp": "Tỵ", "Ất": "Ngọ", "Bính": "Tý", "Đinh": "Tỵ",
    "Mậu": "Ngọ", "Kỷ": "Thân", "Canh": "Dần", "Tân": "Ngọ",
    "Nhâm": "Dậu", "Quý": "Tuất",
}


def stars_for(inp):
    """Trả về {tên chi: [tên sao]} cho các hệ W3a đã được mẫu xác nhận.

    inp cần tối thiểu: year_stem, year_branch, month (âm lịch, 1-12),
    hour_branch, menh_branch, than_branch, loc_ton_branch.
    cung_of_branch (nếu có) dùng để xác định Nô Bộc / Tật Ách; nếu
    thiếu thì suy từ menh_branch (Nô = Mệnh - 7, Tật = Mệnh - 5).
    Các key còn lại trong spec (day, gender, cuc, cuc_num,
    tu_vi_branch, thien_phu_branch, kinh_branch, da_branch, vong,
    dai_van, tu_hoa, tuan, triet, direction, am_duong) không ảnh
    hưởng các hệ này nên được chấp nhận nhưng không dùng.
    """
    year_stem = CAN[_stem_idx(inp["year_stem"])]
    yb = _branch_idx(inp["year_branch"])
    month = int(inp["month"])          # tháng âm lịch, 1-12
    hour = _branch_idx(inp["hour_branch"])
    menh = _branch_idx(inp["menh_branch"])
    than = _branch_idx(inp["than_branch"])
    loc_ton = _branch_idx(inp["loc_ton_branch"])

    # Trung gian (theo repo, đã kiểm chứng gián tiếp qua các hệ dưới):
    #   Văn Khúc = (Thìn + giờ) theo App.py: dichCung(5, giờ - 1)
    #     (repo 1-based) -> 0-based: (4 + hour) % 12.
    #   Tả Phụ = (Thìn + tháng - 1) theo App.py: dichCung(5, tt - 1)
    #     -> 0-based: (4 + month - 1) % 12.
    van_khuc = (4 + hour) % 12
    ta_phu = (4 + month - 1) % 12

    placed = []  # (branch_idx, star_name), theo thứ tự hệ 1-13

    # 1. Thai Phụ / Phong Cáo: Văn Khúc +2 / -2 (App.py).
    placed.append(((van_khuc + 2) % 12, "Thai Phụ"))
    placed.append(((van_khuc - 2) % 12, "Phong Cáo"))

    # 2. Thiên Giải / Địa Giải.
    #   Thiên Giải theo MẪU: Thân làm tháng Giêng, thuận đếm KHÔNG
    #   nhảy cung: Thân + (tháng - 1). Repo đếm nhảy (Thân + 2*tháng - 2)
    #   chỉ khớp 1/10 (tháng 1, hai cách trùng nhau).
    placed.append(((8 + month - 1) % 12, "Thiên Giải"))
    #   Địa Giải: Tả Phụ + 3 (App.py).
    placed.append(((ta_phu + 3) % 12, "Địa Giải"))

    # 3. Thiên La / Địa Võng: cố định Thìn / Tuất (App.py gán cứng).
    placed.append((4, "Thiên La"))    # Thìn
    placed.append((10, "Địa Võng"))   # Tuất

    # 4. Thiên Thương / Thiên Sứ: cung Nô Bộc / cung Tật Ách (App.py).
    placed.append((_palace_branch(inp, "Nô Bộc", -7), "Thiên Thương"))
    placed.append((_palace_branch(inp, "Tật Ách", -5), "Thiên Sứ"))

    # 5. Phá Toái: theo MẪU, không theo repo.
    #   Repo (timPhaToai): chi_năm % 3 == 0 -> Tỵ, == 1 -> Dậu,
    #   == 2 -> Sửu (chi_năm tính 1-based) — chỉ khớp 2/10.
    #   Mẫu: cùng nhóm chi % 3 nhưng hoán đổi Tỵ <-> Dậu:
    #   == 0 -> Dậu, == 1 -> Tỵ, == 2 -> Sửu — khớp 10/10, mỗi nhóm
    #   đều có nhiều lá (nhóm 0: 5 lá, nhóm 1: 3 lá, nhóm 2: 2 lá).
    dem = (yb + 1) % 3
    placed.append(({0: 9, 1: 5, 2: 1}[dem], "Phá Toái"))

    # 6. Đẩu Quân: chi_năm - tháng + giờ + 1 (App.py:
    #   dichCung(chiNam, -tt + gioSinh), repo 1-based -> 0-based
    #   tương đương công thức này). Mẫu viết lẫn "Đầu Quân".
    placed.append(((yb - month + hour + 1) % 12, "Đẩu Quân"))

    # 7. Lưu Hà / Thiên Trù: theo can năm (timLuuTru, bảng ở trên).
    placed.append((_branch_idx(LUU_HA[year_stem]), "Lưu Hà"))
    placed.append((_branch_idx(THIEN_TRU[year_stem]), "Thiên Trù"))

    # 8. Thiên Y: cùng cung với Thiên Riêu = Thiên Hình + 4, mà
    #   Thiên Hình = Dậu + (tháng - 1) -> Thiên Y = (9 + tháng - 1 + 4)
    #   % 12 = tháng % 12 (tháng 12 -> Tý, tháng 1 -> Sửu).
    placed.append((month % 12, "Thiên Y"))

    # 9. Thiên Tài: Mệnh + chi_năm (App.py: dichCung(cungMệnh, chiNam-1)).
    placed.append(((menh + yb) % 12, "Thiên Tài"))

    # 10. Thiên Thọ: Thân + chi_năm (App.py: dichCung(cungThân, chiNam-1)).
    placed.append(((than + yb) % 12, "Thiên Thọ"))

    # 11-12. Quốc Ấn / Đường Phù: chuỗi từ Lộc Tồn qua Kình Dương (+1),
    #   Văn Tinh (+2), Đường Phù (+2), Quốc Ấn (+3) (App.py) ->
    #   Đường Phù = Lộc Tồn + 5, Quốc Ấn = Lộc Tồn + 8.
    placed.append(((loc_ton + 5) % 12, "Đường Phù"))
    placed.append(((loc_ton + 8) % 12, "Quốc Ấn"))

    # 13. Long Trì: Thìn + chi_năm (App.py: dichCung(5, chiNam - 1)
    #    repo 1-based -> 0-based: (4 + yb) % 12).
    placed.append(((4 + yb) % 12, "Long Trì"))

    out = {}
    for branch_idx, star in placed:
        out.setdefault(CHI[branch_idx], []).append(star)
    # Trả về theo thứ tự chi Tý -> Hợi cho ổn định.
    return {branch: out[branch] for branch in CHI if branch in out}


# --- Bảng độ sáng: chép nguyên DiaBan.dacTinhSao ---------------------------
# Mỗi hàng: 12 giá trị theo thứ tự Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ,
# Mùi, Thân, Dậu, Tuất, Hợi. Repo để trống (None) ở một số ô: những ô
# đó KHÔNG có trong dict trả về (do_sang chỉ chứa M/V/Đ/H/B).
# Chú ý các khoảng trống của repo:
#   - ID 7 (Thiên Phủ): KHÔNG CÓ HÀNG trong bảng repo -> Thiên Phủ
#     không có trong do_sang(), dù mẫu nào cũng ghi độ sáng cho nó
#     (xem RULES.md: mẫu Thiên Phủ Tý M, Sửu B, Dần M, Mão B, Mùi Đ,
#     Thân M — chỉ là quan sát mẫu, không đưa vào đây vì không phải
#     bảng repo).
#   - Lộc Tồn cũng không có hàng trong bảng repo (mẫu ghi M/B).
# Tên sao chuẩn hoá: repo viết "Tử vi", "Liêm trinh", "Thiên riêu"...
# -> chuẩn hoá thành "Tử Vi", "Liêm Trinh", "Thiên Riêu" (mẫu viết
# "Thiên Diêu" cho sao này).
_BRIGHTNESS_ROWS = {
    # id: (tên chuẩn, [Tý..Hợi])
    # 2026-10-24 (coverage check 22 lá, user duyệt "ok chốt"): fills sau —
    # Kỵ H tại Tý/Dần/Mão/Tỵ/Ngọ/Thân/Dậu/Hợi (Đ Sửu/Thìn/Mùi/Tuất đã có);
    # Đại/Tiểu Hao H tại Tý/Tỵ/Ngọ/Hợi (Đ Dần/Mão/Thân/Dậu đã có);
    # Khốc H tại Dần/Thìn; Mã H tại Hợi; Tang đủ 12 (Đ Dần/Mão/Thân/Dậu,
    # H còn lại, Tý đã có); Hình H tại Sửu/Tỵ/Mùi; Diêu H tại Tỵ/Ngọ/Hợi
    # (Hợi phân xử bằng tvl: H, thắng Argon Đ; Tuất giữ Đ, AItuvi ca6
    # là outlier); Bạch Hổ thêm hàng đủ 12 (Đ Dần/Mão/Thân/Dậu, H còn lại).
    # Thiên Hư KHÔNG đổi (user chốt giữ hàng tvl).
    1: ("Tử Vi",     ["B", "Đ", "M", "B", "V", "M", "M", "Đ", "M", "B", "V", "B"]),
    2: ("Liêm Trinh", ["V", "Đ", "V", "H", "M", "H", "V", "Đ", "V", "H", "M", "H"]),
    3: ("Thiên Đồng", ["V", "H", "M", "Đ", "H", "Đ", "H", "H", "M", "H", "H", "Đ"]),
    4: ("Vũ Khúc",   ["V", "M", "V", "Đ", "M", "H", "V", "M", "V", "Đ", "M", "H"]),
    5: ("Thái Dương", ["H", "Đ", "V", "V", "V", "M", "M", "Đ", "H", "H", "H", "H"]),
    6: ("Thiên Cơ",   ["Đ", "Đ", "H", "M", "M", "V", "Đ", "Đ", "V", "M", "M", "H"]),
    8: ("Thái Âm",    ["V", "Đ", "H", "H", "H", "H", "H", "Đ", "V", "M", "M", "M"]),
    9: ("Tham Lang",  ["H", "M", "Đ", "H", "V", "H", "H", "M", "Đ", "H", "V", "H"]),
    10: ("Cự Môn",    ["V", "H", "V", "M", "H", "H", "V", "H", "Đ", "M", "H", "Đ"]),
    11: ("Thiên Tướng", ["V", "Đ", "M", "H", "V", "Đ", "V", "Đ", "M", "H", "V", "Đ"]),
    12: ("Thiên Lương", ["V", "Đ", "V", "V", "M", "H", "M", "Đ", "V", "H", "M", "H"]),
    13: ("Thất Sát",  ["M", "Đ", "M", "H", "H", "V", "M", "Đ", "M", "H", "H", "V"]),
    14: ("Phá Quân",  ["M", "V", "H", "H", "Đ", "H", "M", "V", "H", "H", "Đ", "H"]),
    51: ("Đà La",     ["H", "Đ", "H", "H", "Đ", "H", "H", "Đ", "H", "H", "Đ", "H"]),
    52: ("Kình Dương", ["H", "Đ", "H", "H", "Đ", "H", "H", "Đ", "H", "H", "Đ", "H"]),
    55: ("Linh Tinh", ["H", "H", "Đ", "Đ", "Đ", "Đ", "Đ", "H", "H", "H", "H", "H"]),
    56: ("Hỏa Tinh",  ["H", "H", "Đ", "Đ", "Đ", "Đ", "Đ", "H", "H", "H", "H", "H"]),
    # Sửa 2026-10-22 (user duyệt): Thìn H->Đ theo mẫu nguyen (sách ghi
    # Vượng ở Thìn, cùng phe mạnh với Đắc của phụ tinh; repo ghi H là sai).
    57: ("Văn Xương", ["H", "Đ", "H", "Đ", "Đ", "Đ", "H", "Đ", "H", "H", "Đ", "Đ"]),
    # Sửa 2026-10-24 (lá mẫu): Thìn H->Đ theo 2 site (tvl + AItuvi đều
    # ghi Văn Khúc (Đ) ở Di Thìn); repo ghi H ở ô này là sai.
    58: ("Văn Khúc",  ["H", "Đ", "H", "Đ", "Đ", "Đ", "H", "Đ", "H", "H", "Đ", "Đ"]),
    53: ("Địa Không", ["H", "H", "Đ", "H", "H", "Đ", "H", "H", "Đ", "H", "H", "Đ"]),
    54: ("Địa Kiếp",  ["H", "H", "Đ", "H", "H", "Đ", "H", "H", "Đ", "H", "H", "Đ"]),
    95: ("Hóa Kỵ",    ["H", "Đ", "H", "H", "Đ", "H", "H", "Đ", "H", "H", "Đ", "H"]),
    36: ("Đại Hao",   ["H", None, "Đ", "Đ", None, "H", "H", None, "Đ", "Đ", None, "H"]),
    30: ("Tiểu Hao",  ["H", None, "Đ", "Đ", None, "H", "H", None, "Đ", "Đ", None, "H"]),
    # 2026-10-24 (lá THOA + §14.3): các ô repo trống sau đã có mẫu ghi H
    # nhất quán nên điền H (kiểu "mở rộng nhất quán", chỉ điền ô đã quan sát):
    # Khốc Tỵ/Thân/Tuất/Hợi, Hình Tý/Thìn/Ngọ/Tuất/Hợi, Riêu Tý/Sửu/Thìn/Mùi/Thân.
    69: ("Thiên Khốc", ["Đ", "Đ", "H", "Đ", "H", "H", "Đ", "Đ", "H", "Đ", "H", "H"]),
    # Sửa 2026-10-22 (user duyệt): bỏ hàng repo, theo quy luật mẫu —
    # H ở mọi cung trừ Tỵ/Hợi = Đ (mẫu: H tại Tý/Mão/Mùi/Dậu/Thìn/Dần,
    # Đ tại Tỵ x2 + Hợi x1; Sửu/Ngọ/Thân/Tuất suy theo quy luật).
    # Sửa 2026-10-27 (user chốt, sau check TEST04 Phúc Mùi vs các site):
    # ô Mùi H->Đ theo các site, bất chấp lá mẫu Long ghi H tại Mùi —
    # quyết này ưu tiên site ở ô Mùi, các ô còn lại giữ nguyên quy luật mẫu.
    70: ("Thiên Hư",  ["H", "H", "H", "H", "H", "Đ", "H", "Đ", "H", "H", "H", "Đ"]),
    # 2026-10-24 (lá mẫu + 2 mẫu tvl Nguyễn/Thảo): Thân None->H
    # (tvl + AItuvi đều ghi Thiên Mã (H) ở Thân; repo trống ô này).
    98: ("Thiên Mã",  [None, None, "Đ", None, None, "Đ", None, None, "H", None, None, "H"]),
    # 2026-10-24 (lá mẫu): Tang Môn chưa có hàng repo — thêm hàng
    # riêng chỉ ô đã quan sát: Tý=H theo tvl + AItuvi. Lưu ý xung đột:
    # mẫu Nguyễn (tvl) ghi Tang Môn@Tý trơn — có thể là sót phiên âm
    # (Nguyễn chỉ có tvl, không đối chiếu); giữ (H) theo 2 site lá mẫu.
    76: ("Tang Môn",  ["H", "H", "Đ", "Đ", "H", "H", "H", "H", "Đ", "Đ", "H", "H"]),
    # 2026-10-24 (coverage, user duyệt): Bạch Hổ chưa có hàng repo —
    # thêm hàng đủ 12 ô theo AItuvi + tuvivietnam + Argon.
    77: ("Bạch Hổ",   ["H", "H", "Đ", "Đ", "H", "H", "H", "H", "Đ", "Đ", "H", "H"]),
    73: ("Thiên Hình", ["H", "H", "Đ", "Đ", "H", "H", "H", "H", "Đ", "Đ", "H", "H"]),
    74: ("Thiên Riêu", ["H", "H", "Đ", "Đ", "H", "H", "H", "H", "H", "Đ", "Đ", "H"]),
}


def do_sang():
    """{(tên sao, tên chi): độ sáng} — chép nguyên bảng repo.

    Chỉ chứa các ô repo ghi M/V/Đ/H/B; các ô repo để trống (None)
    bị bỏ qua, kể cả khi mẫu ghi chữ ở ô đó (xem RULES.md §14).
    Thiên Phủ và Lộc Tồn không có hàng trong bảng repo nên vắng mặt.
    """
    out = {}
    for _sid, (name, row) in _BRIGHTNESS_ROWS.items():
        for branch, value in zip(CHI, row):
            if value in ("M", "V", "Đ", "H", "B"):
                out[(name, branch)] = value
    return out
