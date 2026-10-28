"""Tạo file clean-format từ ENGINE (không phải chép từ site).

Dùng khi user đưa lá số mới (vd: nữ 19/5/1979).
Grades lấy từ fc['grades']; 2 sao engine không có grade (Thiên Phủ,
Lộc Tồn) thì bù bằng bảng grade trong code;
chi nào bảng cũng không có thì để trơn không suffix.

Usage:
  python3 gen_clean_from_engine.py YYYY-MM-DD HH:MM nam|nu "Tên" [xem_year] out_path
  xem_year mặc định là năm hiện tại.
"""
import datetime
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("phu", "phu_tinh.py")
phu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(phu)
spec2 = importlib.util.spec_from_file_location("laplaso", "lap-la-so.py")
lap = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(lap)
# Bảng hạng cát/hung của renderer (dùng để xếp phụ tinh natal) +
# tên nạp âm (engine chỉ có ngũ hành nạp âm, không có tên).
spec_rc = importlib.util.spec_from_file_location("rc", "render_chart.py")
rc = importlib.util.module_from_spec(spec_rc)
spec_rc.loader.exec_module(rc)
spec_rch = importlib.util.spec_from_file_location("rch", "render_chart_html.py")
rch = importlib.util.module_from_spec(spec_rch)
spec_rch.loader.exec_module(rch)

CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu",
       "Tuất", "Hợi"]
NUM = {2: "Nhị", 3: "Tam", 4: "Tứ", 5: "Ngũ", 6: "Lục"}
PALACE_SHORT = {"Mệnh": "MỆNH", "Huynh Đệ": "HUYNH", "Phu Thê": "PHU",
                "Tử Nữ": "TỬ", "Tử Tức": "TỬ", "Tài Bạch": "TÀI",
                "Tật Ách": "TẬT",
                "Thiên Di": "DI", "Nô Bộc": "NÔ", "Quan Lộc": "QUAN",
                "Điền Trạch": "ĐIỀN", "Phúc Đức": "PHÚC", "Phụ Mẫu": "PHỤ"}
PALACE_ORDER = ["Mệnh", "Huynh Đệ", "Phu Thê", "Tử Nữ", "Tài Bạch",
                "Tật Ách", "Thiên Di", "Nô Bộc", "Quan Lộc", "Điền Trạch",
                "Phúc Đức", "Phụ Mẫu"]
NGU_HANH_CHI = {"Tý": "Thủy", "Sửu": "Thổ", "Dần": "Mộc", "Mão": "Mộc",
                "Thìn": "Thổ", "Tỵ": "Hỏa", "Ngọ": "Hỏa", "Mùi": "Thổ",
                "Thân": "Kim", "Dậu": "Kim", "Tuất": "Thổ", "Hợi": "Thủy"}
NHI_HOP = {"Tý": "Sửu", "Sửu": "Tý", "Dần": "Hợi", "Hợi": "Dần",
           "Mão": "Tuất", "Tuất": "Mão", "Thìn": "Dậu", "Dậu": "Thìn",
           "Tỵ": "Thân", "Thân": "Tỵ", "Ngọ": "Mùi", "Mùi": "Ngọ"}
# Tam hợp liệt kê theo thứ tự chuẩn bắt đầu từ chi sinh của nhóm
# (Dần/Hợi/Thân/Tỵ), KHÔNG phải bắt đầu từ chi của cung.
TAM_HOP = {"Dần": "Dần-Ngọ-Tuất", "Ngọ": "Dần-Ngọ-Tuất", "Tuất": "Dần-Ngọ-Tuất",
           "Hợi": "Hợi-Mão-Mùi", "Mão": "Hợi-Mão-Mùi", "Mùi": "Hợi-Mão-Mùi",
           "Thân": "Thân-Tý-Thìn", "Tý": "Thân-Tý-Thìn", "Thìn": "Thân-Tý-Thìn",
           "Tỵ": "Tỵ-Dậu-Sửu", "Dậu": "Tỵ-Dậu-Sửu", "Sửu": "Tỵ-Dậu-Sửu"}
# Bảng grade trong code cho 2 sao engine không có hàng.
# CHƯA phải grades sách — chỉ để hiển thị đủ, cần đối chiếu sách sau.
SAMPLE_GRADES = {
    ("Thiên Phủ", "Tý"): "M", ("Thiên Phủ", "Sửu"): "B",
    ("Thiên Phủ", "Dần"): "M", ("Thiên Phủ", "Mão"): "B",
    ("Thiên Phủ", "Mùi"): "Đ", ("Thiên Phủ", "Thân"): "M",
    # Ngọ: Thiên Phủ (M) — chốt 2026-10-24 theo lá mẫu.
    ("Thiên Phủ", "Ngọ"): "M",
    # Dậu: user PHÁN 2026-10-24 — (B) mới đúng theo lá THOA. Quyết này
    # BÁC BỎ cả (H) theo sách Tam Hợp 1 (chart-033, 陷) lẫn (Đ) ở lá minh
    # (PHÚC Dậu — xung đột chưa giải: có thể là lỗi phiên âm batch 2,
    # không tự sửa). Hàng Thiên Phủ theo bảng trong code,
    # không theo bảng sách.
    ("Thiên Phủ", "Dậu"): "B",
    # 2026-10-24 (coverage check 22 lá, user duyệt "ok chốt"):
    # Thìn V + Tỵ Đ + Tuất V + Hợi Đ. Hàng Phủ đủ 12/12.
    ("Thiên Phủ", "Thìn"): "V", ("Thiên Phủ", "Tỵ"): "Đ",
    ("Thiên Phủ", "Tuất"): "V", ("Thiên Phủ", "Hợi"): "Đ",
    ("Lộc Tồn", "Dần"): "M", ("Lộc Tồn", "Dậu"): "B",
    ("Lộc Tồn", "Mão"): "M", ("Lộc Tồn", "Ngọ"): "M",
    ("Lộc Tồn", "Thân"): "B", ("Lộc Tồn", "Tý"): "M",
}


def abbrev_dv(name):
    """Viết tắt sao ĐV. theo quy ước file clean (xem diff_clean.py)."""
    if name == "Văn Xương":
        return "Xương"
    if name == "Văn Khúc":
        return "Khúc"
    if name.startswith("Hóa "):
        return "H " + name[4:]
    if name.startswith("Thiên "):
        return "T " + name[6:]
    if name == "Kình Dương":
        return "K Dương"
    return name


def main():
    date, time_, gender, name = sys.argv[1:5]
    gender = phu.canon_gender(gender)
    xem_year = int(sys.argv[5]) if len(sys.argv) > 5 else datetime.date.today().year
    out = sys.argv[6] if len(sys.argv) > 6 else "new_clean.txt"
    can_luong = sys.argv[7] if len(sys.argv) > 7 else "chưa tính"
    fc = phu.full_chart(date, time_, gender)
    eng, inp, phu_d, grades = fc["engine"], fc["inp"], fc["phu"], fc["grades"]
    xem_stem = CAN[(xem_year - 4) % 10]
    xem_branch = CHI[(xem_year - 4) % 12]
    yy, mm, dd = map(int, date.split("-"))
    _hh = int(time_.split(":")[0])
    _ys, _yb, _lm, _ld, _dgz = lap.birth_lunar(yy, mm, dd, _hh)
    # Tuổi mụ = năm xem - năm âm lịch sinh + 1 (dùng lich_vn qua S2L).
    # Sinh 23h đổi sang ngày dương hôm sau (cùng quy ước birth_lunar)
    # nên tuổi cũng tính theo năm âm của ngày đã đổi đó.
    from lich_vn import S2L
    import datetime as _dt
    _sd = _dt.date(yy, mm, dd) + (_dt.timedelta(days=1) if _hh == 23
                                 else _dt.timedelta(0))
    _d, _m, lunar_year, _leap = S2L(_sd.day, _sd.month, _sd.year)
    age = xem_year - lunar_year + 1
    luu, dv, labels, _tieu = phu.luu_for(inp, xem_stem, xem_branch, age)

    # Nguyệt hạn tháng của từng chi trong năm xem (đồng bộ công thức
    # render_chart_html.tinh_thang_th): t1 là chi tháng Giêng, tháng
    # chạy thuận từ đó. Dùng để ghi "(Tháng M)" sau mỗi chi.
    _KHOI_TIEU_HAN = {2: 4, 6: 4, 10: 4, 8: 10, 0: 10, 4: 10,
                      5: 7, 9: 7, 1: 7, 11: 1, 3: 1, 7: 1}
    _is_nam = gender.strip().lower() == "nam"
    _chi_sinh = CHI.index(inp["year_branch"])
    _chi_xem = CHI.index(xem_branch)
    _khoi = _KHOI_TIEU_HAN[_chi_sinh]
    _chieu = 1 if _is_nam else -1
    _tieu_xem = (_khoi + _chieu * (_chi_xem - _chi_sinh)) % 12
    _t1 = (_tieu_xem - (inp["month"] - 1) +
           CHI.index(inp["hour_branch"])) % 12
    _thang_cua_chi = {br: ((CHI.index(br) - _t1) % 12) + 1 for br in CHI}
    # Âm Dương (đồng bộ renderer): Âm/Dương theo can năm sinh, cộng
    # giới tính; thuận/nghịch so với Âm/Dương của chi cung Mệnh.
    _amduong_can = "dương" if CAN.index(inp["year_stem"]) % 2 == 0 else "âm"
    _amduong_txt = ("Âm " if _amduong_can == "âm" else "Dương ") + \
        ("Nam" if _is_nam else "Nữ")
    _menh_amduong = "dương" if CHI.index(eng["menh"]) % 2 == 0 else "âm"
    _amduong_line = f"{_amduong_txt}, " + \
        ("Âm dương thuận lý" if _amduong_can == _menh_amduong
         else "Âm dương nghịch lý")

    # --- Dòng tóm tắt cho AI luận (v4): CHỈ lấy từ dữ liệu engine đã
    # có, không thêm luật mới, không sửa kết quả tính toán nào. ---
    _than_txt = (f"{PALACE_SHORT[eng['cung_of_branch'][inp['than_branch']]]} "
                 f"{inp['than_branch']}")
    _starts = sorted(eng["dai_van"].items(), key=lambda kv: kv[1])
    _cur_van = None
    for _br, _st in _starts:
        if _st <= age < _st + 10:
            _cur_van = (_br, _st)
    if _cur_van:
        _dv_now = (f"{PALACE_SHORT[eng['cung_of_branch'][_cur_van[0]]]} "
                   f"{_cur_van[0]} ({_cur_van[1]}–{_cur_van[1] + 9})")
    else:
        # Tuổi tiền vận: engine (luu_for) vẫn dùng vận đầu để hiển thị
        # nhãn ĐV./LN.; dòng này nói rõ là CHƯA vào vận đó.
        _fbr, _fst = _starts[0]
        _dv_now = (f"chưa vào đại vận, vận đầu "
                   f"{PALACE_SHORT[eng['cung_of_branch'][_fbr]]} {_fbr} "
                   f"({_fst}–{_fst + 9})")
    _tieu_br = CHI[_tieu_xem]
    _tieu_txt = (f"{PALACE_SHORT[eng['cung_of_branch'][_tieu_br]]} {_tieu_br}")
    # v7 (chốt 27/10, theo hướng 3 tầng): LUU_THAI_TUE = cung chứa
    # Thái Tuế năm xem (khởi điểm, đã kiểm trực tiếp từ cột L. trên
    # dòng cung đó); LUU_NIEN_DAI_VAN = cung mang nhãn LN.MỆNH
    # hiện tại của engine. Ghi chú nội bộ (KHÔNG in ra file clean
    # từ v8, user bỏ 27/10 14:57 vì dư thừa; thông tin giữ trong
    # MEMORY.md): nguồn LN.MỆNH là quy luật LN chốt 23/10, đã kiểm
    # 4 điểm; CHƯA đồng nhất hoàn toàn với phép tính Lưu đại hạn
    # Tân Biên §10.2 — điểm lệch đã biết: Ba 75 tuổi engine Dần vs
    # Argon Tý, chỉ trùng ở 76 Sửu. Không dùng làm kết quả chắc
    # chắn cho tới khi phân xử bằng mẫu thực tế. Không chạm code
    # tính sao nào.
    _luu_thai_tue_txt = (f"{PALACE_SHORT[eng['cung_of_branch'][xem_branch]]} "
                         f"{xem_branch}")
    _ln_menh_br = None
    for _br, (_ln_lab, _dv_lab) in labels.items():
        if _ln_lab == "Mệnh":
            _ln_menh_br = _br
            break
    if _ln_menh_br is not None:
        _luu_nien_dai_van_txt = (
            f"{PALACE_SHORT[eng['cung_of_branch'][_ln_menh_br]]} {_ln_menh_br}")
    else:
        _luu_nien_dai_van_txt = "— (chưa xác định theo quy luật LN hiện tại)"
    _tuhoa_txt = ("can " + inp["year_stem"] + " — " +
                  ", ".join(f"{h}: {eng['tu_hoa'][h]}" for h in
                            ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"]))
    _nap_name, _nap_code = rc.nap_am(inp["year_stem"], inp["year_branch"])
    _nap_txt = f"{_nap_name} ({eng['nam_nap_am']})"
    _tuan_txt = (" ".join(eng["tuan"]) + " (" +
                 ", ".join(PALACE_SHORT[eng["cung_of_branch"][b]]
                           for b in eng["tuan"]) + ")")
    _triet_txt = (" ".join(eng["triet"]) + " (" +
                  ", ".join(PALACE_SHORT[eng["cung_of_branch"][b]]
                            for b in eng["triet"]) + ")")
    # Lưu Tứ Hóa theo can năm xem (cùng bảng TU_HOA của engine như
    # Tứ Hóa gốc, chỉ khác can): sao chủ nằm ở cung nào thì L. Hóa
    # đó nằm ở cung đó — agent khỏi đoán khi cung có 2 chính tinh.
    _ln_hosts = lap.TU_HOA[xem_stem]
    _lntuhoa_txt = ("can " + xem_stem + " — " +
                    ", ".join(f"L. {h}: {host}" for h, host in zip(
                        ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"],
                        _ln_hosts)))
    # Tứ Hóa + Lộc/Kình/Đà theo can của đại vận hiện tại (v6, chốt
    # 27/10): CHỈ là dòng tóm tắt header cho AI luận ba tầng, KHÔNG
    # khôi phục sao ĐV. vào dòng cung hay ảnh. Can vận = can cung của
    # cung đại vận chứa tuổi xem; tuổi tiền vận dùng vận đầu (cùng
    # quy ước luu_for và DAI_VAN_HIEN_TAI). Cùng bảng TU_HOA/LOC_TON
    # của engine, không luật mới.
    _dv_branch = _cur_van[0] if _cur_van else _starts[0][0]
    _dv_can = lap.palace_stem(_dv_branch, inp["year_stem"])
    _dv_hosts = lap.TU_HOA[_dv_can]
    _dvtuhoa_txt = ("can " + _dv_can + " — " +
                    ", ".join(f"{h}: {host}" for h, host in zip(
                        ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"],
                        _dv_hosts)))
    _dv_loc = lap.LOC_TON[_dv_can]
    _dv_kinh = CHI[(CHI.index(_dv_loc) + 1) % 12]
    _dv_da = CHI[(CHI.index(_dv_loc) - 1) % 12]
    _dvlk_txt = (f"can {_dv_can} — Lộc Tồn: {_dv_loc}, "
                 f"Kình Dương: {_dv_kinh}, Đà La: {_dv_da}")
    # Ngày giờ sinh quy ra âm lịch (đối chiếu A.txt: Tân Mão / tháng
    # 3 Nhâm Thìn / ngày 24 Kỷ Hợi / giờ Bính Dần). _dgz có thể có
    # hoặc không có khoảng trắng giữa can và chi tùy đường lịch.
    _dgz_clean = _dgz.replace(" ", "")
    # Can ngày KHÔNG lấy bằng _dgz[0]: "Kỷ"[0] là ký tự 'K', không
    # phải can "Kỷ" — tách bằng tiền tố (ký tự đầu các can đều khác
    # nhau nên không nhập nhằng).
    _day_stem = next(s for s in CAN if _dgz_clean.startswith(s))
    _day_branch = _dgz_clean[len(_day_stem):]
    _sinh_am = (f"Năm {inp['year_stem']} {inp['year_branch']}, "
                f"tháng {_lm} ({rc.month_gz(inp['year_stem'], _lm)}), "
                f"ngày {_ld} ({_day_stem} {_day_branch}), "
                f"giờ {rc.hour_gz(_day_stem, inp['hour_branch'])}")

    def _rank_base(base):
        return base[3:] if base.startswith("LN.") else base

    def _group(base):
        """0 = Cát, 1 = Hung, 2 = không có trong bảng hạng."""
        b = _rank_base(base)
        if b in rch.CAT_RANK:
            return 0
        if b in rch.HUNG_RANK:
            return 1
        return 2

    def _nkey(p):
        """Khóa xếp phụ tinh natal: Cát trước, Hung sau, mỗi nhóm từ
        hạng mạnh tới nhẹ theo bảng hạng của renderer; sao không có
        trong bảng xếp cuối cùng (giữ thứ tự gốc)."""
        idx, (_disp, base) = p
        b = _rank_base(base)
        if b in rch.CAT_RANK:
            return (0, rch.CAT_RANK[b], idx)
        if b in rch.HUNG_RANK:
            return (1, rch.HUNG_RANK[b], idx)
        return (2, 999, idx)

    # Luật hạng Hóa (quyết user 27/10, thay bảng TVN vừa áp rồi gỡ):
    # 1) Hóa lấy hạng sao chủ nó hóa (luật host-grade 25/10).
    # 2) FALLBACK (mới): sao chủ không có hạng trong bảng thì lấy hạng
    #    chính tinh trấn thủ cùng cung (sao chủ cung); cung 2 chính
    #    tinh thì lấy hạng mạnh hơn (M>V>Đ>B>H); cung VCD không có
    #    chính tinh thì vẫn để trơn (không bịa). Chỉ áp cho Hóa natal;
    #    sao lưu "L. Hóa" không qua hàm này nên vẫn để trơn.
    # Lý do gỡ bảng TVN: bảng 48 ô theo chi không phủ được trường
    # hợp hạng thay đổi theo chính tinh cung (12 lá TVN chỉ là mẫu
    # đối chiếu, không phải luật). Bảng TVN 48 ô lưu ở báo cáo
    # đối chiếu, không nằm trong code.
    _ORDER = {"M": 5, "V": 4, "Đ": 3, "B": 2, "H": 1}

    def grade_of(star, branch, lords=()):
        if star in eng["tu_hoa"]:
            host = eng["tu_hoa"][star]
            g = (grades.get((host, branch)) or
                 SAMPLE_GRADES.get((host, branch)) or
                 grades.get((phu._CANON.get(host, host), branch)) or
                 SAMPLE_GRADES.get((phu._CANON.get(host, host), branch)))
            if not g and lords:
                lg = [grades.get((s, branch)) or
                      SAMPLE_GRADES.get((s, branch)) for s in lords]
                lg = [x for x in lg if x]
                if lg:
                    g = max(lg, key=lambda x: _ORDER.get(x, 0))
            return f" ({g})" if g else ""
        g = grades.get((star, branch)) or SAMPLE_GRADES.get((star, branch))
        return f" ({g})" if g else ""

    # eng['cung_of_branch']: branch -> tên cung; đảo lại thành cung -> branch.
    branch_of = {v: k for k, v in eng["cung_of_branch"].items()}
    cuc_num = eng["dai_van"][eng["menh"]]
    cuc_full = f"{eng['cuc']} {NUM[cuc_num]} Cục"
    lines = [
        f"# ENGINE-GENERATED — {date} {time_} {gender}, "
        f"xem {xem_stem} {xem_branch} {xem_year}",
        f"# Khuôn dòng cung: SỐ. TÊN CUNG (tuổi bắt đầu đại vận) CAN CHI (Tháng nguyệt hạn): chính tinh (hạng) | phụ tinh natal (nhóm Cát ; nhóm Hung) | sao lưu (L.) | sao vòng Tràng Sinh | ĐV.cung đại vận | LN.cung lưu niên | đất (ngũ hành chi) | Tam hợp | Xung chiếu | Nhị hợp | [nhãn Tuần/Triệt nếu có]",
        f"# Thứ tự dòng theo chiều đại vận, 1 là cung Mệnh. Số trong ngoặc = tuổi bắt đầu đại vận của cung đó (mỗi vận 10 năm). Tháng = nguyệt hạn của cung đó trong năm xem. CAN là can cung theo Ngũ Hổ Độn (can năm sinh).",
        f"# Cung viết tắt: MỆNH Mệnh, HUYNH Huynh Đệ, PHU Phu Thê, TỬ Tử Nữ, TÀI Tài Bạch, TẬT Tật Ách, DI Thiên Di, NÔ Nô Bộc, QUAN Quan Lộc, ĐIỀN Điền Trạch, PHÚC Phúc Đức, PHỤ Phụ Mẫu.",
        f"# Dòng tóm tắt: THAN_CU = cung Thân cư; DAI_VAN_HIEN_TAI = cung đại vận của tuổi xem (kèm khoảng tuổi); LUU_THAI_TUE = cung chứa Thái Tuế năm xem (khởi điểm); TIEU_HAN = cung tiểu hạn năm xem (diễn biến/nguyên nhân); LUU_NIEN_DAI_VAN = cung LN.MỆNH hiện tại của engine; TU_HOA = sao chủ của 4 Hóa theo can năm sinh; LN_TU_HOA = sao chủ của 4 Lưu Hóa theo can năm xem; NAP_AM = tên nạp âm năm sinh (kèm ngũ hành); CUC_QUAN_HE = quan hệ ngũ hành giữa nạp âm và Cục; TUAN/TRIET kèm tên cung bị ảnh hưởng trong ngoặc; SINH_AM = ngày giờ sinh quy ra âm lịch (can chi năm/tháng/ngày/giờ); DAI_VAN_TU_HOA = sao chủ 4 Hóa theo can đại vận hiện tại, DAI_VAN_LOC_KINH_DA = Lộc Tồn/Kình/Đà theo can đó (tuổi tiền vận thì theo can vận đầu) — hai dòng này chỉ là tóm tắt header cho AI luận ba tầng, không phải sao ĐV. trong cung.",
        f"# Phụ tinh natal xếp Cát trước, Hung sau, mỗi nhóm từ hạng mạnh tới nhẹ theo bảng hạng của renderer; dấu ; ngăn hai nhóm, — = nhóm đó không có sao, sao không có trong bảng (nếu có) xếp sau dấu ; thứ hai. Cung bị Tuần/Triệt thì cuối dòng có thêm | [TUẦN] / | [TRIỆT] / | [TUẦN–TRIỆT]. Cột sao lưu trống ghi (không có).",
        f"# Cột sao lưu (L.) gồm: Thái Tuế, Lộc Tồn, Kình Dương, Đà La, 4 Lưu Hóa, Thiên Khôi, Thiên Việt, Thiên Mã, Đào Hoa, Hồng Loan, Văn Xương, Văn Khúc, Tang Môn, Bạch Hổ, Thiên Khốc, Thiên Hư, Kiếp Sát.",
        f"# Tam hợp/Xung chiếu/Nhị hợp ghi kèm tên cung viết tắt trước địa chi, vd MỆNH(Dần).",
        f"# Hạng: (M) Miếu, (V) Vượng, (Đ) Đắc, (B) Bình, (H) Hãm; sao không có hạng để trơn. Cung không có chính tinh ghi (Vô chính diệu).",
        f"NGUOI: {name}",
        f"SINH: {date} {time_} {gender}",
        f"SINH_AM: {_sinh_am}",
        f"XEM: {xem_stem} {xem_branch} {xem_year} {age}",
        f"MENH: {eng['menh']}",
        f"CUC: {cuc_full}",
        f"CHU_MENH: {eng['chu_menh']}",
        f"CHU_THAN: {eng['chu_than']}",
        f"AM_DUONG: {_amduong_line}",
        f"LAI_NHAN: {eng['lai_nhan']}",
        f"CAN: {can_luong}",
        f"TUAN: {_tuan_txt}",
        f"TRIET: {_triet_txt}",
        f"THAN_CU: {_than_txt}",
        f"DAI_VAN_HIEN_TAI: {_dv_now}",
        f"LUU_THAI_TUE: {_luu_thai_tue_txt}",
        f"TIEU_HAN: {_tieu_txt}",
        f"LUU_NIEN_DAI_VAN: {_luu_nien_dai_van_txt}",
        f"TU_HOA: {_tuhoa_txt}",
        f"LN_TU_HOA: {_lntuhoa_txt}",
        f"DAI_VAN_TU_HOA: {_dvtuhoa_txt}",
        f"DAI_VAN_LOC_KINH_DA: {_dvlk_txt}",
        f"NAP_AM: {_nap_txt}",
        f"CUC_QUAN_HE: {eng['menh_cuc_relation']}",
    ]
    # Thứ tự dòng theo chiều đại vận (sắp theo tuổi bắt đầu vận của
    # từng chi, 1 là cung Mệnh), không theo thứ tự cung cố định.
    _van_order = sorted(branch_of.items(), key=lambda kv: eng["dai_van"][kv[1]])
    for _ordinal, (cung, br) in enumerate(_van_order, 1):
        chinh = [s for s, b in eng["stars"].items() if b == br]
        chinh_txt = ",".join(s + grade_of(s, br, chinh) for s in chinh) \
            if chinh else "(Vô chính diệu)"
        _items = list(enumerate([(s + grade_of(s, br, chinh), s)
                                 for s in phu_d.get(br, [])]))
        _items.sort(key=_nkey)
        if not _items:
            natal = "(không có)"
        else:
            _cat = [d for _, (d, b) in _items if _group(b) == 0]
            _hung = [d for _, (d, b) in _items if _group(b) == 1]
            _unk = [d for _, (d, b) in _items if _group(b) == 2]
            natal = (",".join(_cat) or "—") + " ; " + (",".join(_hung) or "—")
            if _unk:
                natal += " ; " + ",".join(_unk)
        luu_txt = (",".join("L. " + s for s in luu.get(br, []))
                   if luu.get(br) else "(không có)")
        ln_label, dv_label = labels[br]
        _tam = "-".join(f"{PALACE_SHORT[eng['cung_of_branch'][b]]}({b})"
                        for b in TAM_HOP[br].split("-"))
        _xung_br = CHI[(CHI.index(br) + 6) % 12]
        _xung = (f"{PALACE_SHORT[eng['cung_of_branch'][_xung_br]]}({_xung_br})")
        _nhi_br = NHI_HOP[br]
        _nhi = f"{PALACE_SHORT[eng['cung_of_branch'][_nhi_br]]}({_nhi_br})"
        _stem = lap.palace_stem(br, inp["year_stem"])
        _line = (f"{_ordinal}. {PALACE_SHORT[cung]} ({eng['dai_van'][br]}) {_stem} {br} "
                 f"(Tháng {_thang_cua_chi[br]}): {chinh_txt} | {natal} | "
                 f"{luu_txt} | {eng['vong'][br]} | "
                 f"ĐV.{PALACE_SHORT[dv_label]} | LN.{PALACE_SHORT[ln_label]} | "
                 f"đất ({NGU_HANH_CHI[br]}) | Tam hợp: {_tam} | "
                 f"Xung chiếu: {_xung} | Nhị hợp: {_nhi}")
        _in_tuan = br in eng["tuan"]
        _in_triet = br in eng["triet"]
        if _in_tuan and _in_triet:
            _line += " | [TUẦN–TRIỆT]"
        elif _in_tuan:
            _line += " | [TUẦN]"
        elif _in_triet:
            _line += " | [TRIỆT]"
        lines.append(_line)
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"saved {out} — Mệnh {eng['menh']}, {cuc_full}, tuổi mụ {age}, "
          f"Tuần {' '.join(eng['tuan'])}, Triệt {' '.join(eng['triet'])}")


if __name__ == "__main__":
    main()
