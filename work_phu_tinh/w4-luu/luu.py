# -*- coding: utf-8 -*-
"""Sao lưu niên (L.) và sao đại vận (ĐV.) — nhóm W4, hệ sao lưu.

Pure Python, KHÔNG import lap-la-so.py. Mọi bảng tra cứu đều chép trị số
từ engine/bảng đã chốt và từ 10 lá mẫu (xem RULES.md để biết mức bằng
chứng của từng quy luật — không phải quy luật nào cũng được mẫu kiểm
chứng đầy đủ 12 can/chi).

Hàm chính:
    luu_stars_for(inp) -> (luu, dv, labels, tieu_han_branch)

inp (dict) — các key bắt buộc:
    birth_stem: can năm sinh, vd "Quý".
    birth_branch: chi năm sinh, vd "Hợi".
    xem_stem: can năm xem, vd "Bính".
    xem_branch: chi năm xem, vd "Ngọ".
    dv_branch: chi của cung đại vận hiện tại, vd "Sửu".
    dv_can: can của cung đại vận hiện tại (theo Ngũ Hổ Độn; lấy từ engine
        palace_stem hoặc từ can cung ghi trong lá mẫu).
    star_branch: dict {tên sao: chi} — vị trí sinh của các sao dùng cho
        Tứ Hóa (14 chính tinh + Văn Xương, Văn Khúc, Tả Phụ, Hữu Bật).
        Chính tinh lấy từ engine (chart["stars"]); phụ tinh lấy từ lá mẫu
        hoặc nhóm phụ tinh tương ứng. Sao nào không có trong dict thì
        Tứ Hóa của nó bị bỏ qua (không crash).
inp (dict) — các key tùy chọn:
    xem_age_mu: tuổi mụ năm xem. Hiện KHÔNG có quy luật nào dùng tuổi
        (tiểu hạn tính theo chi, không theo tuổi), key này chỉ giữ để
        tương thích interface với các nhóm khác.
    gender: giới ("nam"/"nữ") — quyết chiều tiểu hạn (nam thuận,
        nữ nghịch). Không truyền thì tieu_han_branch = None.
    ln_origin_branch: chi mang nhãn LN.Mệnh (gốc của bản đồ nhãn LN).
        Quy luật đặt gốc LN này CHƯA suy ra được từ 10 lá (UNVERIFIED,
        xem RULES.md). Nếu không truyền, nhãn LN trả về None cho mọi cung.

Trả về:
    luu: dict {chi: [tên sao L.]} — tên KHÔNG có tiền tố "L.".
        Đủ 12 chi (chi không có sao thì list rỗng).
        CHÚ Ý: luu KHÔNG có "Đà La" — 10/10 lá mẫu đều không có L.Đà La
        (dù sách Tân Biên ghi có lưu Đà; theo lá mẫu, xem RULES.md).
    dv: dict {chi: [tên sao ĐV.]} — tên theo dạng chuẩn:
        "Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ", "Lộc Tồn",
        "Kình Dương", "Đà La", "Thiên Khôi", "Thiên Việt", "Thiên Mã",
        "Văn Xương", "Văn Khúc". Đủ 12 chi.
    labels: dict {chi: (nhãn LN, nhãn ĐV)} — nhãn là tên cung đầy đủ
        ("Mệnh", "Huynh Đệ", "Phu Thê", "Tử Tức", "Tài Bạch", "Tật Ách",
        "Thiên Di", "Nô Bộc", "Quan Lộc", "Điền Trạch", "Phúc Đức",
        "Phụ Mẫu"). Nhãn ĐV đếm NGƯỢC từ cung đại vận (xem RULES.md).
        Nhãn LN đếm NGƯỢC từ ln_origin_branch nếu được truyền, ngược lại
        là None (quy luật gốc LN chưa xác định; lá lá mẫu đếm thuận và lá
        dieu-huong không khớp phép đếm xoay nào — xem RULES.md).
    tieu_han_branch: chi của cung tiểu hạn năm xem (quy luật user
        chốt 2026-10-25, sau khi tự xác nhận từ nhiều nguồn): khởi
        lưu niên chỉ ở tứ mộ theo tam hợp tuổi sinh (Dần/Ngọ/Tuất
        → Thìn; Thân/Tý/Thìn → Tuất; Tỵ/Dậu/Sửu → Mùi; Hợi/Mão/Mùi
        → Sửu); viết chi tuổi sinh vào cung khởi, rồi +1 chi mỗi
        bước theo chiều NAM THUẬN / NỮ NGHỊCH (chỉ theo giới, KHÔNG
        theo âm/dương can năm — khác chiều đại vận). Kiểm chứng:
        lá tao 2026 → Thân (khớp header tvl "Tiểu hạn năm xem: Cung
        Quan Lộc (Thân)"). Lưu ý: 2 trang sách chụp + 2 hình ví dụ
        user gửi trước đó dùng chiều âm/dương (Âm Nam nghịch, Âm Nữ
        thuận) — luật đó SAI cho tiểu hạn, đã bị thay bằng luật này;
        Nghiệm Lý Toàn Thư cũng nêu câu hỏi tương tự và trích luật
        "nam đi thuận nữ đi nghịch", dù cùng đoạn đó nó trưng 2 lá
        theo chiều âm/dương nên không coi là bằng chứng chốt — quyết
        này theo user + header tvl lá tao.

Thứ tự sao trong mỗi list là thứ tự chuẩn cố định (không phải thứ tự
trong lá mẫu, vì thứ tự mẫu không nhất quán). So sánh kết quả với mẫu
nên so theo tập hợp (set), không so theo thứ tự.
"""

CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi",
       "Thân", "Dậu", "Tuất", "Hợi"]
CHI_IDX = {c: i for i, c in enumerate(CHI)}

CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân",
       "Nhâm", "Quý"]

CUNG_ORDER = ["Mệnh", "Huynh Đệ", "Phu Thê", "Tử Tức", "Tài Bạch",
              "Tật Ách", "Thiên Di", "Nô Bộc", "Quan Lộc", "Điền Trạch",
              "Phúc Đức", "Phụ Mẫu"]

# Bảng Tứ Hóa đã chốt theo user (giống engine lap-la-so.py TU_HOA):
# Tân Quyền = Thái Dương (theo app phổ biến, không theo Tân Biên ghi
# Thiên Lương); Mậu Khoa = Hữu Bật; Canh Khoa = Thái Âm;
# Nhâm Khoa = Tả Phụ. Thứ tự: Lộc, Quyền, Khoa, Kỵ.
TU_HOA = {
    "Giáp": ("Liêm Trinh", "Phá Quân", "Vũ Khúc", "Thái Dương"),
    "Ất": ("Thiên Cơ", "Thiên Lương", "Tử Vi", "Thái Âm"),
    "Bính": ("Thiên Đồng", "Thiên Cơ", "Văn Xương", "Liêm Trinh"),
    "Đinh": ("Thái Âm", "Thiên Đồng", "Thiên Cơ", "Cự Môn"),
    "Mậu": ("Tham Lang", "Thái Âm", "Hữu Bật", "Thiên Cơ"),
    "Kỷ": ("Vũ Khúc", "Tham Lang", "Thiên Lương", "Văn Khúc"),
    "Canh": ("Thái Dương", "Vũ Khúc", "Thái Âm", "Thiên Đồng"),
    "Tân": ("Cự Môn", "Thái Dương", "Văn Khúc", "Văn Xương"),
    "Nhâm": ("Thiên Lương", "Tử Vi", "Tả Phụ", "Vũ Khúc"),
    "Quý": ("Phá Quân", "Cự Môn", "Thái Âm", "Tham Lang"),
}

# Lộc Tồn theo can (giống engine LOC_TON; sách Tân Biên tinh hoa §4
# ghi cùng bảng này).
LOC_TON = {"Giáp": "Dần", "Ất": "Mão", "Bính": "Tỵ", "Đinh": "Ngọ",
           "Mậu": "Tỵ", "Kỷ": "Ngọ", "Canh": "Thân", "Tân": "Dậu",
           "Nhâm": "Hợi", "Quý": "Tý"}

# Thiên Khôi / Thiên Việt theo can — bảng theo CẶP can (cặp can cùng
# Tên sao có 2 cách viết giữa các module: engine ghi "Tả Phụ",
# worker W2 ghi "Tả Phù" (star_branch dùng dạng W2). Khi tra vị trí
# của sao Tứ Hóa phải thử cả 2 dạng, nếu không Hóa sẽ bị rơi mất
# (đã xảy ra với DV. Hóa Khoa của vận Nhâm trước 2026-10-22).
_CANON = {"Tả Phụ": "Tả Phù", "Tả Phù": "Tả Phụ"}

# một giá trị): Giáp/Mậu, Ất/Kỷ, Bính/Đinh, Canh/Tân, Nhâm/Quý.
# Bằng chứng: sao sinh (8 can) + ĐV (6 can, gồm Mậu, Bính) + L. can Bính
# đều khớp bảng này (xem RULES.md). Không dùng bảng "hoán đổi" (swap)
# cho can chẵn: lá dieu-huong (Đinh) khớp bảng cặp, không khớp bảng swap.
# NGOẠI LỆ 2026-10-22: Nhâm/Quý KHÔNG theo cặp (Tỵ, Mão) cũ — 2 site
# độc lập (tuviluangiai.vn + AItuvi), mỗi site 1 lá Nhâm + 1 lá Quý,
# đều cho Khôi Mão + Việt Tỵ. Đã sửa bảng theo bằng chứng 2 site.
KHOI_VIET = {
    "Giáp": ("Sửu", "Mùi"), "Mậu": ("Sửu", "Mùi"),
    "Ất": ("Tý", "Thân"), "Kỷ": ("Tý", "Thân"),
    "Bính": ("Hợi", "Dậu"), "Đinh": ("Hợi", "Dậu"),
    "Canh": ("Ngọ", "Dần"), "Tân": ("Ngọ", "Dần"),
    "Nhâm": ("Mão", "Tỵ"), "Quý": ("Mão", "Tỵ"),
}

# Tam hợp -> sao (theo chi; sách Tân Biên tinh hoa §4 ghi bảng Mã này).
# Thiên Mã: Dần-Ngọ-Tuất -> Thân; Thân-Tý-Thìn -> Dần;
# Tỵ-Dậu-Sửu -> Hợi; Hợi-Mão-Mùi -> Tỵ.
_TAM_HOP_MA = {}
for _grp, _ma in [(("Dần", "Ngọ", "Tuất"), "Thân"),
                  (("Thân", "Tý", "Thìn"), "Dần"),
                  (("Tỵ", "Dậu", "Sửu"), "Hợi"),
                  (("Hợi", "Mão", "Mùi"), "Tỵ")]:
    for _b in _grp:
        _TAM_HOP_MA[_b] = _ma
# Đào Hoa: Thân-Tý-Thìn -> Dậu; Dần-Ngọ-Tuất -> Mão;
# Tỵ-Dậu-Sửu -> Ngọ; Hợi-Mão-Mùi -> Tý.
_TAM_HOP_DAO = {}
for _grp, _dao in [(("Thân", "Tý", "Thìn"), "Dậu"),
                   (("Dần", "Ngọ", "Tuất"), "Mão"),
                   (("Tỵ", "Dậu", "Sửu"), "Ngọ"),
                   (("Hợi", "Mão", "Mùi"), "Tý")]:
    for _b in _grp:
        _TAM_HOP_DAO[_b] = _dao
# Kiếp Sát: Thân-Tý-Thìn -> Tỵ; Dần-Ngọ-Tuất -> Hợi;
# Tỵ-Dậu-Sửu -> Dần; Hợi-Mão-Mùi -> Thân.
_TAM_HOP_KIEP = {}
for _grp, _kiep in [(("Thân", "Tý", "Thìn"), "Tỵ"),
                    (("Dần", "Ngọ", "Tuất"), "Hợi"),
                    (("Tỵ", "Dậu", "Sửu"), "Dần"),
                    (("Hợi", "Mão", "Mùi"), "Thân")]:
    for _b in _grp:
        _TAM_HOP_KIEP[_b] = _kiep

_L_ORDER = ["Thái Tuế", "Lộc Tồn", "Kình Dương",
            "Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ",
            "Thiên Khôi", "Thiên Việt", "Thiên Mã",
            "Đào Hoa", "Hồng Loan", "Văn Xương", "Văn Khúc",
            "Thiên Đức", "Nguyệt Đức", "Tang Môn", "Bạch Hổ",
            "Thiên Khốc", "Thiên Hư", "Kiếp Sát",
            "Long Đức", "Phúc Đức"]
_DV_ORDER = ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ",
             "Lộc Tồn", "Kình Dương", "Đà La",
             "Thiên Khôi", "Thiên Việt", "Thiên Mã",
             "Văn Xương", "Văn Khúc"]


def _at(mapping, branch, name):
    mapping.setdefault(branch, [])
    if name not in mapping[branch]:
        mapping[branch].append(name)


def _sorted_by(mapping, order):
    rank = {n: i for i, n in enumerate(order)}
    return {c: sorted(mapping.get(c, []), key=lambda n: rank.get(n, 99))
            for c in CHI}


def _loc_ton_group(can):
    """Lộc Tồn / Kình / Đà của một can, và Văn Xương / Văn Khúc của
    cùng can đó (Xương = Lộc + 3, Khúc = 11 − Lộc, theo chỉ số chi).
    Công thức Xương/Khúc khớp 4/4 can có dữ liệu ĐV (Giáp/Ất/Bính/Kỷ)
    và L. can Bính; các can còn lại là ngoại suy từ công thức, xem
    RULES.md — không phải 10/10 lá nào cũng kiểm chứng trực tiếp."""
    loc = LOC_TON[can]
    li = CHI_IDX[loc]
    kinh = CHI[(li + 1) % 12]
    da = CHI[(li - 1) % 12]
    xuong = CHI[(li + 3) % 12]
    khuc = CHI[(11 - li) % 12]
    return loc, kinh, da, xuong, khuc


def luu_stars_for(inp):
    for key in ("birth_stem", "birth_branch", "xem_stem", "xem_branch",
                "dv_branch", "dv_can", "star_branch"):
        if key not in inp:
            raise KeyError(f"luu_stars_for: thiếu key bắt buộc {key!r}")
    birth_branch = inp["birth_branch"]
    xem_stem = inp["xem_stem"]
    xem_branch = inp["xem_branch"]
    dv_branch = inp["dv_branch"]
    dv_can = inp["dv_can"]
    star_branch = inp["star_branch"]
    ln_origin = inp.get("ln_origin_branch")

    xi = CHI_IDX[xem_branch]
    bi = CHI_IDX[birth_branch]

    # ---- (a) Sao lưu niên L. ----
    luu = {}
    _at(luu, xem_branch, "Thái Tuế")
    loc, kinh, da, xuong, khuc = _loc_ton_group(xem_stem)
    _at(luu, loc, "Lộc Tồn")
    _at(luu, kinh, "Kình Dương")
    # PHÁT L.Đà La theo quyết định của user (2026-10-22 23:28, chọn phe
    # AItuvi): AItuvi 3/3 lá (lá mẫu, Nhâm 08/01/1975, Quý
    # 23/02/1975) đều có L. Đà La đúng vị trí Đà của can năm xem
    # (năm Bính -> Thìn), dù text-app 0/10 và tuviluangiai.vn không
    # hiện. Hệ quả: đối chiếu L. với text-app sẽ thừa 1 marker/lá
    # (có chủ đích, theo quyết định trên, không phải lỗi).
    _at(luu, da, "Đà La")
    for hoa, star in zip(("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"),
                         TU_HOA[xem_stem]):
        # Thử tên gốc rồi tên biến thể (vd Tả Phụ -> Tả Phù) trước khi
        # tra vị trí, nếu không Hóa của sao có 2 cách viết sẽ rơi mất.
        br = star_branch.get(star) or star_branch.get(_CANON.get(star, star))
        if br is not None:
            _at(luu, br, hoa)
    khoi, viet = KHOI_VIET[xem_stem]
    _at(luu, khoi, "Thiên Khôi")
    _at(luu, viet, "Thiên Việt")
    _at(luu, _TAM_HOP_MA[xem_branch], "Thiên Mã")
    _at(luu, _TAM_HOP_DAO[xem_branch], "Đào Hoa")
    _at(luu, CHI[(3 - xi) % 12], "Hồng Loan")
    _at(luu, xuong, "Văn Xương")
    _at(luu, khuc, "Văn Khúc")

    _at(luu, CHI[(xi + 2) % 12], "Tang Môn")
    _at(luu, CHI[(xi + 8) % 12], "Bạch Hổ")
    _at(luu, CHI[(6 - xi) % 12], "Thiên Khốc")
    _at(luu, CHI[(xi + 6) % 12], "Thiên Hư")
    _at(luu, _TAM_HOP_KIEP[xem_branch], "Kiếp Sát")
    # L. Tứ Đức (Thiên/Nguyệt/Long/Phúc Đức) ĐÃ BỎ theo quyết Admin
    # 25/10 + Tân Biên (Tứ Đức chỉ natal theo năm sinh: §8.14 +
    # vòng Thái Tuế; sách không có lưu Tứ Đức). Sao Tứ Đức natal
    # vẫn giữ nguyên ở tầng Natal; chỉ bỏ 4 dòng L. trùng lặp
    # (Long/Phúc Đức lưu trước đây trùng y hệt natal vì cùng tính
    # theo chi năm sinh; Thiên/Nguyệt Đức lưu tính lại theo năm xem
    # cũng không có trong sách).
    luu = _sorted_by(luu, _L_ORDER)

    # ---- (b) Sao đại vận ĐV. ----
    dv = {}
    for hoa, star in zip(("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"),
                         TU_HOA[dv_can]):
        # Thử tên gốc rồi tên biến thể (xem chú thích ở khối L.):
        # trước 2026-10-22, DV. Hóa Khoa của vận Nhâm bị rơi vì Tả Phụ
        # (bảng Tứ Hóa) không khớp Tả Phù (worker W2) — lá AItuvi Nhâm
        # 08/01/1975 21:30 hiện rõ DV. H Khoa ở Dần nên phải phát.
        br = star_branch.get(star) or star_branch.get(_CANON.get(star, star))
        if br is not None:
            _at(dv, br, hoa)
    dloc, dkinh, dda, dxuong, dkhuc = _loc_ton_group(dv_can)
    _at(dv, dloc, "Lộc Tồn")
    _at(dv, dkinh, "Kình Dương")
    _at(dv, dda, "Đà La")
    dkhoi, dviet = KHOI_VIET[dv_can]
    _at(dv, dkhoi, "Thiên Khôi")
    _at(dv, dviet, "Thiên Việt")
    _at(dv, _TAM_HOP_MA[dv_branch], "Thiên Mã")
    # ĐV. Văn Xương/Văn Khúc CHỈ phát cho can đã kiểm chứng trực tiếp
    # (Giáp/Ất/Bính/Kỷ — 7 lá mẫu có đủ 2 sao này đúng công thức).
    # Các can còn lại đã kiểm chứng là KHÔNG phát (lá sạch có đủ hệ
    # ĐV. nhưng không có 2 sao này): Đinh×3, Mậu×1 (AItuvi), Canh/Tân
    # (AItuvi + tuviluangiai.vn), Nhâm/Quý (AItuvi + tuviluangiai.vn,
    # 2026-10-22). Vậy cả 10 can đều đã có bằng chứng, không còn can
    # nào ở trạng thái chưa kiểm chứng. Phía L. giữ nguyên (L. Bính
    # đã kiểm chứng).
    if dv_can in ("Giáp", "Ất", "Bính", "Kỷ"):
        _at(dv, dxuong, "Văn Xương")
        _at(dv, dkhuc, "Văn Khúc")
    dv = _sorted_by(dv, _DV_ORDER)

    # ---- (c) Nhãn LN / ĐV ----
    dv_idx = CHI_IDX[dv_branch]
    ln_idx = CHI_IDX[ln_origin] if ln_origin is not None else None
    labels = {}
    for br in CHI:
        bi2 = CHI_IDX[br]
        dv_label = CUNG_ORDER[(dv_idx - bi2) % 12]
        ln_label = (CUNG_ORDER[(ln_idx - bi2) % 12]
                    if ln_idx is not None else None)
        labels[br] = (ln_label, dv_label)

    # ---- (d) Tiểu hạn (user chốt 2026-10-25: Nam thuận, Nữ nghịch) ----
    # Khởi ở tứ mộ theo tam hợp tuổi sinh; viết chi tuổi vào cung khởi,
    # rồi +1 chi mỗi bước theo chiều giới (không theo âm/dương can).
    TIEU_HAN_KHOI = {"Dần": "Thìn", "Ngọ": "Thìn", "Tuất": "Thìn",
                     "Thân": "Tuất", "Tý": "Tuất", "Thìn": "Tuất",
                     "Tỵ": "Mùi", "Dậu": "Mùi", "Sửu": "Mùi",
                     "Hợi": "Sửu", "Mão": "Sửu", "Mùi": "Sửu"}
    _gender = inp.get("gender")
    if _gender in ("nam", "nữ") and birth_branch in TIEU_HAN_KHOI:
        _direction = 1 if _gender == "nam" else -1
        _steps = (CHI_IDX[xem_branch] - CHI_IDX[birth_branch]) % 12
        tieu_han_branch = CHI[(CHI_IDX[TIEU_HAN_KHOI[birth_branch]]
                               + _steps * _direction) % 12]
    else:
        tieu_han_branch = None
    # 2026-10-25 (quyết Admin: bỏ hệ sao ĐV. trong phụ tinh, rối rắm
    # thêm): trả dv rỗng — không còn sao ĐV. trong data + render.
    # Code tính dv ở trên giữ nguyên để khôi phục khi cần (bỏ dòng
    # này là dv hiện lại). Nhãn ĐV. ở dải cuối (labels) không phải
    # sao nên giữ nguyên; tiểu hạn cũng không bị ảnh hưởng.
    dv = {}
    return luu, dv, labels, tieu_han_branch
