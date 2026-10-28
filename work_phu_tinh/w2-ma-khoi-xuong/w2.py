# -*- coding: utf-8 -*-
"""W2 — Phụ tinh: Thiên Mã (+ Hoa Cái, Kiếp Sát, Đào Hoa), Thiên Khôi /
Thiên Việt, Văn Xương / Văn Khúc, Hỏa Tinh / Linh Tinh, Cô Thần,
Đào Hoa / Hồng Loan, Ân Quang / Thiên Quý, Thiên Quan / Thiên Phúc,
Tả Phù / Hữu Bật, Văn Tinh.

Pure Python, KHÔNG import lap-la-so. Mọi quy luật dưới đây đều đã đối
chiếu với 10 lá mẫu trong sample_charts/ (xem RULES.md cùng thư mục).
Lá mẫu là CHUẨN cao nhất: chỗ nào repo lasotuvi lệch mẫu thì code này
theo mẫu, và chỗ lệch được ghi rõ trong RULES.md.

Quy ước chỉ số chi: Tý=0, Sửu=1, Dần=2, Mão=3, Thìn=4, Tỵ=5, Ngọ=6,
Mùi=7, Thân=8, Dậu=9, Tuất=10, Hợi=11. Can: Giáp=0 .. Quý=9.

Tên sao trả về dùng dạng CHUẨN (vd "Tả Phù"; mẫu có khi viết "Tả Phụ").

Một ngoại lệ có chủ ý: Thiên Phúc của năm Mậu KHÔNG được đưa vào dict
vì không có nguồn đáng tin nào phủ được ô này (bảng repo đã chứng minh
sai ở 7/8 can kiểm chứng được, câu phú trong repo cũng không nhắc Mậu).
Xem RULES.md §8.
"""

CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi",
       "Thân", "Dậu", "Tuất", "Hợi"]
CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân",
       "Nhâm", "Quý"]
CHI_IDX = {c: i for i, c in enumerate(CHI)}
CAN_IDX = {c: i for i, c in enumerate(CAN)}


def _idx(value, table):
    """Nhận tên sao/chi/can hoặc chỉ số nguyên, trả về chỉ số."""
    if isinstance(value, int):
        return value % 12 if table is CHI else value % 10
    return table.index(value)


def _shift(branch_idx, delta):
    return CHI[(branch_idx + delta) % 12]


def _mirror(branch_idx):
    """Đối xứng qua trục Sửu–Mùi: chi b -> (2 - b) mod 12."""
    return CHI[(2 - branch_idx) % 12]


# --- 1. Thiên Mã (theo chi năm, tam hợp) -------------------------------
_MA = {
    # tam hợp Dần–Ngọ–Tuất -> Thân; Thân–Tý–Thìn -> Dần;
    # Tỵ–Dậu–Sửu -> Hợi; Hợi–Mão–Mùi -> Tỵ
    "Dần": "Thân", "Ngọ": "Thân", "Tuất": "Thân",
    "Thân": "Dần", "Tý": "Dần", "Thìn": "Dần",
    "Tỵ": "Hợi", "Dậu": "Hợi", "Sửu": "Hợi",
    "Hợi": "Tỵ", "Mão": "Tỵ", "Mùi": "Tỵ",
}

# --- 2. Thiên Khôi / Thiên Việt (theo can năm, 5 nhóm) ---------------
# Nhóm can: (Giáp, Mậu), (Ất, Kỷ), (Bính, Đinh), (Canh, Tân), (Nhâm, Quý).
# Bính và Mậu chưa có lá trực tiếp: giá trị của chúng là suy từ nhóm
# (Đinh đã xác nhận nhóm Bính–Đinh, Giáp đã xác nhận nhóm Giáp–Mậu).
_KHOI_VIET = {
    "Giáp": ("Sửu", "Mùi"), "Mậu": ("Sửu", "Mùi"),
    "Ất": ("Tý", "Thân"), "Kỷ": ("Tý", "Thân"),
    "Bính": ("Hợi", "Dậu"), "Đinh": ("Hợi", "Dậu"),
    "Canh": ("Ngọ", "Dần"), "Tân": ("Ngọ", "Dần"),
    "Nhâm": ("Mão", "Tỵ"), "Quý": ("Mão", "Tỵ"),
}

# --- 4. Hỏa Tinh / Linh Tinh (khởi cung theo chi năm) ----------------
# Nhóm chi năm -> (khởi Hỏa, khởi Linh). Nhóm Tỵ–Dậu–Sửu: MẪU cho
# Hỏa khởi Mão, Linh khởi Tuất — repo timHoaLinh đảo ngược hai khởi
# cung này (Hỏa Tuất, Linh Mão) và sai cả 3 lá thuộc nhóm.
_HOA_LINH_START = {
    "Dần": ("Sửu", "Mão"), "Ngọ": ("Sửu", "Mão"), "Tuất": ("Sửu", "Mão"),
    "Tý": ("Dần", "Tuất"), "Thìn": ("Dần", "Tuất"), "Thân": ("Dần", "Tuất"),
    "Tỵ": ("Mão", "Tuất"), "Dậu": ("Mão", "Tuất"), "Sửu": ("Mão", "Tuất"),
    "Hợi": ("Dậu", "Tuất"), "Mão": ("Dậu", "Tuất"), "Mùi": ("Dậu", "Tuất"),
}

# --- 5. Cô Thần (theo chi năm) -----------------------------------------
_CO_THAN = {
    "Hợi": "Dần", "Tý": "Dần", "Sửu": "Dần",
    "Dần": "Tỵ", "Mão": "Tỵ", "Thìn": "Tỵ",
    "Tỵ": "Thân", "Ngọ": "Thân", "Mùi": "Thân",
    "Thân": "Hợi", "Dậu": "Hợi", "Tuất": "Hợi",
}

# --- 8. Thiên Quan / Thiên Phúc (theo can năm) -------------------------
_THIEN_QUAN = {
    "Giáp": "Mùi", "Ất": "Thìn", "Bính": "Tỵ", "Đinh": "Dần",
    "Mậu": "Mão", "Kỷ": "Dậu", "Canh": "Hợi", "Tân": "Dậu",
    "Nhâm": "Tuất", "Quý": "Ngọ",
}
# Thiên Phúc: theo câu phú trong repo + mẫu (repo bảng sai 7/8 can).
# Bảng này khớp Tân Biên §8.24 cả 10 can. Bính (Tý) chỉ có câu phú,
# chưa có lá trực tiếp. Mậu (Mão): VERIFIED 2026-10-22 — lá
# tuviluangiai.vn sinh năm Mậu Thìn 1988 (15/08, giờ Tỵ) có Thiên Phúc
# ở Mão (cùng cung với Thiên Quan Mão), khớp sách §8.24.
_THIEN_PHUC = {
    "Giáp": "Dậu", "Ất": "Thân", "Bính": "Tý", "Đinh": "Hợi",
    "Mậu": "Mão",
    "Kỷ": "Dần", "Canh": "Ngọ", "Tân": "Tỵ",
    "Nhâm": "Ngọ", "Quý": "Tỵ",
}


def _gender_sign(gender):
    g = str(gender).strip().lower()
    if g in ("nam", "male", "m", "1", "+1"):
        return 1
    if g in ("nữ", "nu", "female", "f", "-1"):
        return -1
    raise ValueError("gender không nhận dạng được: %r" % (gender,))


def _amduong_sign(am_duong):
    a = str(am_duong).strip()
    if a in ("Dương", "duong", "yang", "1", "+1"):
        return 1
    if a in ("Âm", "am", "yin", "-1"):
        return -1
    raise ValueError("am_duong không nhận dạng được: %r" % (am_duong,))


def stars_for(inp):
    """Trả về dict {tên chi: [tên sao]} cho các hệ W2.

    inp cần các key: year_stem, year_branch, month (tháng âm, int),
    day (ngày âm, int), hour_branch, gender, am_duong, kinh_branch.
    Các key còn lại trong spec (menh_branch, than_branch, cuc, ...)
    được chấp nhận nhưng không dùng cho các hệ này.
    """
    year_stem = inp["year_stem"]
    year_branch = inp["year_branch"]
    month = int(inp["month"])
    day = int(inp["day"])
    hour_idx = _idx(inp["hour_branch"], CHI)
    year_idx = _idx(year_branch, CHI)
    kinh_idx = _idx(inp["kinh_branch"], CHI)

    out = {}

    def put(branch, star):
        out.setdefault(branch, []).append(star)

    # 1. Thiên Mã + vòng Mã (Hoa Cái = Mã+2, Kiếp Sát = Mã+3)
    ma = _MA[year_branch]
    ma_idx = CHI_IDX[ma]
    put(ma, "Thiên Mã")
    put(_shift(ma_idx, 2), "Hoa Cái")
    put(_shift(ma_idx, 3), "Kiếp Sát")

    # 2. Thiên Khôi / Thiên Việt
    khoi, viet = _KHOI_VIET[year_stem]
    put(khoi, "Thiên Khôi")
    put(viet, "Thiên Việt")

    # 3. Văn Khúc khởi Thìn giờ Tý, đếm thuận; Văn Xương đối xứng
    #    qua trục Sửu–Mùi với Văn Khúc.
    van_khuc_idx = (4 + hour_idx) % 12
    van_khuc = CHI[van_khuc_idx]
    put(van_khuc, "Văn Khúc")
    put(_mirror(van_khuc_idx), "Văn Xương")

    # 4. Hỏa Tinh / Linh Tinh. Chiều đếm phụ thuộc tích
    #    (dấu giới tính) x (dấu âm dương của can năm):
    #    tích +1: Hỏa thuận, Linh nghịch; tích -1: Hỏa nghịch, Linh thuận.
    hoa_start, linh_start = _HOA_LINH_START[year_branch]
    hs, ls = CHI_IDX[hoa_start], CHI_IDX[linh_start]
    prod = _gender_sign(inp["gender"]) * _amduong_sign(inp["am_duong"])
    if prod == 1:
        hoa = CHI[(hs + hour_idx) % 12]
        linh = CHI[(ls - hour_idx) % 12]
    else:
        hoa = CHI[(hs - hour_idx) % 12]
        linh = CHI[(ls + hour_idx) % 12]
    put(hoa, "Hỏa Tinh")
    put(linh, "Linh Tinh")

    # 5. Cô Thần (Quả Tú là cặp đối xứng, thuộc nhóm khác — không làm)
    put(_CO_THAN[year_branch], "Cô Thần")

    # 6. Đào Hoa (= Mã + 7) và Hồng Loan (theo chi năm)
    put(_shift(ma_idx, 7), "Đào Hoa")
    put(CHI[(3 - year_idx) % 12], "Hồng Loan")

    # 7. Ân Quang / Thiên Quý: Ân Quang an từ Văn Xương (lấy Văn Xương
    #    làm mồng 1, đếm thuận đến ngày sinh, lùi 1 cung); Thiên Quý
    #    đối xứng qua trục Sửu–Mùi với Ân Quang. Cách này khớp 10/10;
    #    cách Vu Thiên (Thìn + ngày + giờ) và cách Thiên Quý theo
    #    Văn Khúc nghịch trong comment repo đều KHÔNG khớp mẫu.
    van_xuong_idx = (2 - van_khuc_idx) % 12
    an_quang_idx = (van_xuong_idx + day - 2) % 12
    put(CHI[an_quang_idx], "Ân Quang")
    put(_mirror(an_quang_idx), "Thiên Quý")

    # 8. Thiên Quan / Thiên Phúc (bảng khớp Tân Biên §8.24, Mậu đã
    # kiểm chứng bằng lá mẫu 2026-10-22 nên không còn ngoại lệ).
    put(_THIEN_QUAN[year_stem], "Thiên Quan")
    put(_THIEN_PHUC[year_stem], "Thiên Phúc")

    # 9. Tả Phù khởi Thìn tháng Giêng, đếm thuận theo tháng âm;
    #    Hữu Bật đối xứng qua trục Sửu–Mùi với Tả Phù.
    ta_phu_idx = (3 + month) % 12
    put(CHI[ta_phu_idx], "Tả Phù")
    put(_mirror(ta_phu_idx), "Hữu Bật")

    # 10. Văn Tinh NATAL ĐÃ BỎ (phán user 2026-10-25, lá lá mẫu):
    # Nam Phái không có sao natal Văn Tinh — thứ các site ghi "Văn Tinh"
    # (AItuvi Dần, tvl các lá mẫu) thực chất là LN.Văn Tinh (lưu).
    # Luật cũ Kình+2 (khớp 11/12 lá mẫu) chỉ khớp vì các site ghi LN
    # trùng vị trí đó, không phải sao natal. KHÔNG đặt Văn Tinh natal
    # ở đây nữa; luật LN.Văn Tinh chưa có (chờ user dạy).

    return out
