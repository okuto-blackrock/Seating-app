import streamlit as st
import random
import json

st.set_page_config(page_title="席替えアプリ", page_icon="🪑", layout="wide")


st.markdown(”””

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap');
* { font-family: 'Noto Sans JP', sans-serif; }

.seat-box {
    padding: 8px 4px;
    border-radius: 8px;
    text-align: center;
    font-size: 13px;
    font-weight: 700;
    margin: 3px;
    min-height: 52px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    line-height: 1.3;
}
.seat-boy { background: #dbeafe; border: 2px solid #3b82f6; color: #1e40af; }
.seat-girl { background: #fce7f3; border: 2px solid #ec4899; color: #9d174d; }
.seat-vision { border-width: 3px !important; border-style: dashed !important; }
.seat-empty { background: #f3f4f6; border: 2px dashed #d1d5db; color: #9ca3af; }
.blackboard {
    background: #1a3a2a;
    color: #a7f3d0;
    text-align: center;
    padding: 12px;
    border-radius: 8px;
    font-size: 18px;
    font-weight: 900;
    letter-spacing: 4px;
    margin-bottom: 16px;
}
</style>

“””, unsafe_allow_html=True)

st.title(“🪑 席替えアプリ”)

# — セッション初期化 —

if “students” not in st.session_state:
st.session_state.students = []
if “avoid_pairs” not in st.session_state:
st.session_state.avoid_pairs = []
if “prev_cols” not in st.session_state:
st.session_state.prev_cols = {}
if “result” not in st.session_state:
st.session_state.result = None

# ===== タブ =====

tab1, tab2, tab3 = st.tabs([“👥 児童登録”, “⚙️ 条件設定”, “🎲 席替え実行”])

# ===== タブ1: 児童登録 =====

with tab1:
st.subheader(“児童を登録する”)

```
col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
with col1:
    new_name = st.text_input("名前", key="new_name", placeholder="例: 田中さくら")
with col2:
    new_gender = st.selectbox("性別", ["女", "男"], key="new_gender")
with col3:
    new_vision = st.selectbox("視力", ["普通", "要前列（視力弱）"], key="new_vision")
with col4:
    st.write("")
    st.write("")
    if st.button("追加", use_container_width=True):
        name = st.session_state.new_name.strip()
        if name and not any(s["name"] == name for s in st.session_state.students):
            st.session_state.students.append({
                "name": name,
                "gender": new_gender,
                "vision": new_vision == "要前列（視力弱）"
            })
            st.rerun()

# 一括入力
with st.expander("📋 一括入力（CSV形式）"):
    st.caption("名前,性別(男/女),視力(弱/普) の形式で1行1人入力")
    bulk = st.text_area("例:\n田中さくら,女,普\n山田太郎,男,弱", height=150)
    if st.button("一括追加"):
        for line in bulk.strip().split("\n"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 1 and parts[0]:
                name = parts[0]
                gender = parts[1] if len(parts) > 1 and parts[1] in ["男", "女"] else "男"
                vision = len(parts) > 2 and parts[2] == "弱"
                if not any(s["name"] == name for s in st.session_state.students):
                    st.session_state.students.append({"name": name, "gender": gender, "vision": vision})
        st.rerun()

# 一覧表示
if st.session_state.students:
    st.write(f"**登録済み: {len(st.session_state.students)}人**")
    for i, s in enumerate(st.session_state.students):
        c1, c2, c3, c4 = st.columns([3, 1, 2, 1])
        c1.write(s["name"])
        c2.write(s["gender"])
        c3.write("👓 要前列" if s["vision"] else "普通")
        if c4.button("削除", key=f"del_{i}"):
            st.session_state.students.pop(i)
            st.rerun()

    if st.button("全員削除", type="secondary"):
        st.session_state.students = []
        st.rerun()
```

# ===== タブ2: 条件設定 =====

with tab2:
st.subheader(“条件を設定する”)

```
col_a, col_b = st.columns(2)
with col_a:
    separate_gender = st.checkbox("男女を隔列に並べる", value=True)
    avoid_same_col = st.checkbox("前回と同じ列にならないようにする", value=True)
with col_b:
    cols_count = st.number_input("列数", min_value=3, max_value=8, value=6)
    rows_count = st.number_input("行数", min_value=3, max_value=8, value=5)

st.markdown("---")
st.subheader("近づけたくない組み合わせ")

names = [s["name"] for s in st.session_state.students]
if len(names) >= 2:
    col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
    with col_p1:
        p1 = st.selectbox("児童A", names, key="p1")
    with col_p2:
        p2 = st.selectbox("児童B", [n for n in names if n != p1], key="p2")
    with col_p3:
        st.write("")
        st.write("")
        if st.button("追加", key="add_pair"):
            pair = tuple(sorted([p1, p2]))
            if pair not in [tuple(sorted(p)) for p in st.session_state.avoid_pairs]:
                st.session_state.avoid_pairs.append(list(pair))
                st.rerun()

    if st.session_state.avoid_pairs:
        st.write("**設定済みペア:**")
        for i, pair in enumerate(st.session_state.avoid_pairs):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🚫 {pair[0]} ↔ {pair[1]}")
            if c2.button("削除", key=f"pair_{i}"):
                st.session_state.avoid_pairs.pop(i)
                st.rerun()
else:
    st.info("児童を2人以上登録すると設定できます")
```

# ===== タブ3: 席替え実行 =====

with tab3:
st.subheader(“席替えを実行する”)

```
students = st.session_state.students
n = len(students)

if n == 0:
    st.warning("児童を登録してください")
else:
    total_seats = cols_count * rows_count
    st.info(f"登録人数: {n}人 ／ 席数: {total_seats}席")

    if n > total_seats:
        st.error("席数が足りません。列数・行数を増やしてください。")
    else:
        if st.button("🎲 席替え実行！", type="primary", use_container_width=True):

            boys = [s for s in students if s["gender"] == "男"]
            girls = [s for s in students if s["gender"] == "女"]
            vision_students = [s["name"] for s in students if s["vision"]]

            # --- 列割り当て ---
            # 男女隔列: 偶数列=女、奇数列=男（0始まり）
            col_assignments = {}  # name -> col index

            if separate_gender:
                boy_cols = [c for c in range(cols_count) if c % 2 == 1]
                girl_cols = [c for c in range(cols_count) if c % 2 == 0]
            else:
                all_cols = list(range(cols_count))
                boy_cols = all_cols[:cols_count//2]
                girl_cols = all_cols[cols_count//2:]

            def assign_to_cols(group, available_cols, prev_cols, avoid_same):
                """グループをシャッフルして列に割り当てる"""
                random.shuffle(group)
                seats = []
                for col in available_cols:
                    for row in range(rows_count):
                        seats.append((col, row))
                random.shuffle(seats)

                assigned = []
                for s in group:
                    candidates = [seat for seat in seats if seat not in [a[1] for a in assigned]]
                    if avoid_same and s["name"] in prev_cols:
                        prev_c = prev_cols[s["name"]]
                        preferred = [seat for seat in candidates if seat[0] != prev_c]
                        if preferred:
                            candidates = preferred
                    if candidates:
                        chosen = candidates[0]
                        assigned.append((s, chosen))
                return assigned

            prev_cols = st.session_state.prev_cols
            boy_assigned = assign_to_cols(boys, boy_cols, prev_cols, avoid_same_col)
            girl_assigned = assign_to_cols(girls, girl_cols, prev_cols, avoid_same_col)
            all_assigned = boy_assigned + girl_assigned

            # 視力考慮: 前列（row=0,1）に移動
            grid = {pos: s for s, pos in all_assigned}
            pos_map = {s["name"]: pos for s, pos in all_assigned}

            front_rows = [0, 1]
            for vname in vision_students:
                if vname in pos_map:
                    cur_pos = pos_map[vname]
                    if cur_pos[1] not in front_rows:
                        # 前列の空き席を探す
                        front_seats = [(c, r) for c in range(cols_count) for r in front_rows if (c, r) not in grid or grid.get((c, r), {}).get("name") == vname]
                        if front_seats:
                            new_pos = random.choice(front_seats)
                            # swap
                            if new_pos in grid:
                                other = grid[new_pos]
                                grid[cur_pos] = other
                                pos_map[other["name"]] = cur_pos
                            else:
                                del grid[cur_pos]
                            cur_s = next(s for s in students if s["name"] == vname)
                            grid[new_pos] = cur_s
                            pos_map[vname] = new_pos

            # 近接ペアチェック・再配置（簡易: 隣接=上下左右）
            avoid_pairs = [tuple(sorted(p)) for p in st.session_state.avoid_pairs]
            for _ in range(50):
                bad = False
                for pair in avoid_pairs:
                    pos_a = pos_map.get(pair[0])
                    pos_b = pos_map.get(pair[1])
                    if pos_a and pos_b:
                        if abs(pos_a[0]-pos_b[0]) <= 1 and abs(pos_a[1]-pos_b[1]) <= 1:
                            # swap Bをランダムな他の席と交換
                            other_names = [s["name"] for s in students if s["name"] not in [pair[0], pair[1]]]
                            if other_names:
                                swap_name = random.choice(other_names)
                                pos_c = pos_map[swap_name]
                                s_b = grid[pos_b]
                                s_c = grid[pos_c]
                                grid[pos_b] = s_c
                                grid[pos_c] = s_b
                                pos_map[pair[1]] = pos_c
                                pos_map[swap_name] = pos_b
                            bad = True
                if not bad:
                    break

            # 前回列を保存
            new_prev = {s["name"]: pos_map[s["name"]][0] for s in students if s["name"] in pos_map}
            st.session_state.prev_cols = new_prev
            st.session_state.result = grid

        # --- 結果表示 ---
        if st.session_state.result:
            grid = st.session_state.result
            st.markdown('<div class="blackboard">黒 板</div>', unsafe_allow_html=True)

            for row in range(rows_count):
                cols_display = st.columns(cols_count)
                for col_idx, col_display in enumerate(cols_display):
                    student = grid.get((col_idx, row))
                    if student:
                        gender_class = "seat-boy" if student["gender"] == "男" else "seat-girl"
                        vision_class = " seat-vision" if student["vision"] else ""
                        icon = "👓 " if student["vision"] else ""
                        col_display.markdown(
                            f'<div class="seat-box {gender_class}{vision_class}">{icon}{student["name"]}<br><small>{"男" if student["gender"]=="男" else "女"}</small></div>',
                            unsafe_allow_html=True
                        )
                    else:
                        col_display.markdown('<div class="seat-box seat-empty">空席</div>', unsafe_allow_html=True)

            st.caption("👓 = 視力配慮　🟦 = 男子　🟪 = 女子")

            # テキスト出力
            with st.expander("📄 テキストで確認・コピー"):
                lines = ["【席替え結果】", "（黒板側）"]
                for row in range(rows_count):
                    row_names = []
                    for col_idx in range(cols_count):
                        s = grid.get((col_idx, row))
                        row_names.append(s["name"] if s else "　空席　")
                    lines.append("　".join(row_names))
                st.text("\n".join(lines))
```
