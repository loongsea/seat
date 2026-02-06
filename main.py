import streamlit as st
import pandas as pd
import random
from datetime import datetime
import numpy as np

# 页面配置
st.set_page_config(
    page_title="班级座位编排系统",
    page_icon="🎓",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
    .seat-card {
        padding: 10px;
        margin: 5px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        min-height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #ddd;
        transition: all 0.3s;
    }
    .seat-card.occupied {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #764ba2;
    }
    .seat-card.empty {
        background-color: #f0f2f6;
        color: #666;
        border-style: dashed;
    }
    .student-item {
        padding: 10px;
        margin: 5px 0;
        border-radius: 6px;
        background-color: #f8f9fa;
        border-left: 4px solid #667eea;
    }
    .classroom-container {
        padding: 20px;
        background-color: #f9f9f9;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    .teacher-area {
        background-color: #4a6fa5;
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 30px;
        border: 3px solid #2c5282;
    }
    .blackboard {
        background-color: #2d3748;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 20px;
        border: 5px solid #1a202c;
    }
    .desk-number {
        font-size: 12px;
        color: #666;
        position: absolute;
        top: -15px;
        left: 50%;
        transform: translateX(-50%);
    }
    .desk-container {
        position: relative;
        margin: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
def init_session_state():
    if 'students' not in st.session_state:
        st.session_state.students = []
    if 'seat_arrangement' not in st.session_state:
        st.session_state.seat_arrangement = {}
    if 'selected_student' not in st.session_state:
        st.session_state.selected_student = None
    if 'selected_seat' not in st.session_state:
        st.session_state.selected_seat = None
    if 'classroom_layout' not in st.session_state:
        st.session_state.classroom_layout = {'rows': 4, 'cols': 6}

init_session_state()

def main():
    st.title("🎓 班级座位编排系统")
    st.markdown("---")
    
    # 侧边栏
    with st.sidebar:
        st.header("📋 控制面板")
        
        # 导入学生
        st.subheader("1. 导入学生名单")
        import_option = st.radio(
            "选择导入方式",
            ["手动输入", "上传文件", "示例数据"],
            index=2,
            label_visibility="collapsed"
        )
        
        if import_option == "手动输入":
            student_text = st.text_area(
                "输入学生姓名（每行一个）",
                height=150,
                placeholder="例如：\n张三\n李四\n王五\n..."
            )
            if st.button("导入名单", use_container_width=True) and student_text:
                names = [name.strip() for name in student_text.split('\n') if name.strip()]
                st.session_state.students = list(set(names))  # 去重
                st.success(f"成功导入 {len(names)} 名学生")
                st.rerun()
                
        elif import_option == "上传文件":
            uploaded_file = st.file_uploader("选择文件", type=['txt', 'csv', 'xlsx'])
            if uploaded_file:
                try:
                    if uploaded_file.name.endswith('.txt'):
                        content = uploaded_file.read().decode('utf-8')
                        names = [name.strip() for name in content.split('\n') if name.strip()]
                    elif uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                        if '姓名' in df.columns:
                            names = df['姓名'].dropna().tolist()
                        else:
                            names = df.iloc[:, 0].dropna().tolist()
                    else:  # Excel
                        df = pd.read_excel(uploaded_file)
                        if '姓名' in df.columns:
                            names = df['姓名'].dropna().tolist()
                        else:
                            names = df.iloc[:, 0].dropna().tolist()
                    
                    st.session_state.students = list(set(names))
                    st.success(f"成功导入 {len(names)} 名学生")
                    st.rerun()
                except Exception as e:
                    st.error(f"读取文件出错: {str(e)}")
        else:  # 示例数据
            if st.button("加载示例数据", use_container_width=True):
                example_names = [
                    "张三", "李四", "王五", "赵六", "钱七", "孙八",
                    "周九", "吴十", "郑十一", "王十二", "李十三", "张十四",
                    "刘十五", "陈十六", "杨十七", "黄十八", "赵十九", "周二十",
                    "吴二十一", "郑二十二", "王二十三", "李二十四", "林二十五", "谢二十六"
                ]
                st.session_state.students = example_names
                st.session_state.seat_arrangement = {}
                st.success(f"加载了 {len(example_names)} 名示例学生")
                st.rerun()
        
        st.markdown("---")
        
        # 教室布局设置
        st.subheader("2. 教室布局设置")
        col1, col2 = st.columns(2)
        with col1:
            rows = st.number_input("行数", 1, 10, 4)
        with col2:
            cols = st.number_input("每行座位", 1, 10, 6)
        
        if st.button("更新布局", use_container_width=True):
            st.session_state.classroom_layout = {'rows': rows, 'cols': cols}
            st.rerun()
        
        st.markdown("---")
        
        # 操作按钮
        st.subheader("3. 座位操作")
        
        if st.button("🎲 随机排座", use_container_width=True):
            random_arrange_seats()
            
        if st.button("🗑️ 清空所有座位", use_container_width=True):
            st.session_state.seat_arrangement = {}
            st.session_state.selected_student = None
            st.session_state.selected_seat = None
            st.rerun()
            
        if st.button("📊 导出座位表", use_container_width=True, type="secondary"):
            export_seating_chart()
    
    # 主界面 - 两列布局
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🏫 教室座位图")
        display_classroom()
    
    with col2:
        st.subheader("👥 学生管理")
        display_student_list()
        
        st.subheader("🎯 手动安排")
        if st.session_state.students:
            manual_seat_assignment()
        else:
            st.info("请先导入学生名单")
    
    # 显示座位表
    if st.session_state.seat_arrangement:
        st.markdown("---")
        st.subheader("📋 座位安排表")
        display_seating_table()

def display_classroom():
    """显示教室座位图"""
    rows = st.session_state.classroom_layout['rows']
    cols = st.session_state.classroom_layout['cols']
    row_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    # 教室装饰
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown('<div class="teacher-area">👨‍🏫 讲台</div>', unsafe_allow_html=True)
            st.markdown('<div class="blackboard">📚 黑 板</div>', unsafe_allow_html=True)
    
    # 创建座位网格
    st.markdown('<div class="classroom-container">', unsafe_allow_html=True)
    
    for row in range(rows):
        # 创建一行座位
        cols_list = st.columns(cols)
        for col_idx, col in enumerate(cols_list):
            seat_id = f"{row_letters[row]}{col_idx+1}"
            with col:
                # 检查座位是否有学生
                student = st.session_state.seat_arrangement.get(seat_id)
                
                # 座位卡片
                if student:
                    # 如果这个座位被选中，显示不同颜色
                    is_selected = st.session_state.selected_seat == seat_id
                    border_color = "#ff4444" if is_selected else "#764ba2"
                    
                    st.markdown(f"""
                    <div class="desk-container">
                        <div class="desk-number">{seat_id}</div>
                        <div class="seat-card occupied" style="border-color: {border_color};">
                            {student}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 移除按钮
                    if st.button(f"移除", key=f"remove_{seat_id}", use_container_width=True):
                        del st.session_state.seat_arrangement[seat_id]
                        st.rerun()
                else:
                    # 空座位
                    st.markdown(f"""
                    <div class="desk-container">
                        <div class="desk-number">{seat_id}</div>
                        <div class="seat-card empty">
                            空位
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 安排按钮
                    if st.button(f"安排", key=f"assign_{seat_id}", use_container_width=True):
                        st.session_state.selected_seat = seat_id
                        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 显示统计信息
    total_seats = rows * cols
    occupied_seats = len(st.session_state.seat_arrangement)
    empty_seats = total_seats - occupied_seats
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总座位数", total_seats)
    with col2:
        st.metric("已安排", occupied_seats)
    with col3:
        st.metric("空座位", empty_seats)

def display_student_list():
    """显示学生列表"""
    if not st.session_state.students:
        st.info("暂无学生名单")
        return
    
    # 搜索框
    search_term = st.text_input("🔍 搜索学生", "")
    
    # 显示学生列表
    for student in st.session_state.students:
        if search_term and search_term not in student:
            continue
            
        # 检查是否已安排座位
        assigned_seat = None
        for seat, s in st.session_state.seat_arrangement.items():
            if s == student:
                assigned_seat = seat
                break
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if assigned_seat:
                st.markdown(f'<div class="student-item">✅ {student} <span style="color: #666; font-size: 0.9em;">(座位: {assigned_seat})</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="student-item">👤 {student}</div>', unsafe_allow_html=True)
        
        with col2:
            if assigned_seat:
                if st.button("移除", key=f"remove_stu_{student}", use_container_width=True):
                    del st.session_state.seat_arrangement[assigned_seat]
                    st.rerun()
            else:
                if st.button("选择", key=f"select_{student}", use_container_width=True):
                    st.session_state.selected_student = student
                    st.rerun()
    
    # 显示统计
    total_students = len(st.session_state.students)
    unassigned = [s for s in st.session_state.students 
                  if s not in st.session_state.seat_arrangement.values()]
    
    st.info(f"共 {total_students} 名学生，{len(unassigned)} 名未安排座位")

def manual_seat_assignment():
    """手动安排座位"""
    col1, col2 = st.columns(2)
    
    with col1:
        # 选择学生
        student_options = [""] + [s for s in st.session_state.students 
                                 if s not in st.session_state.seat_arrangement.values()]
        selected_student = st.selectbox(
            "选择学生",
            student_options,
            index=0 if st.session_state.selected_student is None else 
                  student_options.index(st.session_state.selected_student),
            key="manual_select_student"
        )
        
        if selected_student:
            st.session_state.selected_student = selected_student
    
    with col2:
        # 选择座位
        rows = st.session_state.classroom_layout['rows']
        cols = st.session_state.classroom_layout['cols']
        row_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        
        # 获取空座位列表
        empty_seats = []
        for row in range(rows):
            for col in range(1, cols+1):
                seat_id = f"{row_letters[row]}{col}"
                if seat_id not in st.session_state.seat_arrangement:
                    empty_seats.append(seat_id)
        
        seat_options = [""] + empty_seats
        selected_seat = st.selectbox(
            "选择座位",
            seat_options,
            index=0 if st.session_state.selected_seat is None else 
                  (seat_options.index(st.session_state.selected_seat) if st.session_state.selected_seat in seat_options else 0),
            key="manual_select_seat"
        )
        
        if selected_seat:
            st.session_state.selected_seat = selected_seat
    
    # 安排按钮
    if st.session_state.selected_student and st.session_state.selected_seat:
        if st.button("✅ 安排到选中座位", use_container_width=True, type="primary"):
            # 检查学生是否已被安排
            for seat, student in st.session_state.seat_arrangement.items():
                if student == st.session_state.selected_student:
                    st.warning(f"{student} 已在座位 {seat}，请先移除")
                    return
            
            # 安排座位
            st.session_state.seat_arrangement[st.session_state.selected_seat] = st.session_state.selected_student
            st.session_state.selected_student = None
            st.session_state.selected_seat = None
            st.rerun()
    
    # 快速安排按钮
    if st.session_state.selected_student and not st.session_state.selected_seat:
        if st.button("🎲 随机安排空座位", use_container_width=True):
            random_assign_student(st.session_state.selected_student)

def random_arrange_seats():
    """随机安排所有座位"""
    if not st.session_state.students:
        st.error("请先导入学生名单")
        return
    
    rows = st.session_state.classroom_layout['rows']
    cols = st.session_state.classroom_layout['cols']
    row_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    # 生成所有座位
    all_seats = [f"{row_letters[row]}{col+1}" for row in range(rows) for col in range(cols)]
    
    # 打乱学生和座位
    shuffled_students = st.session_state.students.copy()
    random.shuffle(shuffled_students)
    random.shuffle(all_seats)
    
    # 安排座位
    st.session_state.seat_arrangement = {}
    for i in range(min(len(shuffled_students), len(all_seats))):
        st.session_state.seat_arrangement[all_seats[i]] = shuffled_students[i]
    
    st.success(f"已随机安排 {len(st.session_state.seat_arrangement)} 个座位")
    st.rerun()

def random_assign_student(student):
    """随机安排一个学生到空座位"""
    rows = st.session_state.classroom_layout['rows']
    cols = st.session_state.classroom_layout['cols']
    row_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    # 找到所有空座位
    empty_seats = []
    for row in range(rows):
        for col in range(1, cols+1):
            seat_id = f"{row_letters[row]}{col}"
            if seat_id not in st.session_state.seat_arrangement:
                empty_seats.append(seat_id)
    
    if not empty_seats:
        st.error("没有空座位了")
        return
    
    # 随机选择一个空座位
    random_seat = random.choice(empty_seats)
    st.session_state.seat_arrangement[random_seat] = student
    st.session_state.selected_student = None
    st.rerun()

def display_seating_table():
    """显示座位安排表格"""
    rows = st.session_state.classroom_layout['rows']
    cols = st.session_state.classroom_layout['cols']
    row_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    # 创建座位表数据
    table_data = []
    for row in range(rows):
        row_data = []
        for col in range(1, cols+1):
            seat_id = f"{row_letters[row]}{col}"
            student = st.session_state.seat_arrangement.get(seat_id, "")
            row_data.append(student if student else "空")
        table_data.append(row_data)
    
    # 创建DataFrame
    df = pd.DataFrame(
        table_data,
        columns=[f"第{col}列" for col in range(1, cols+1)],
        index=[f"{row_letters[row]}排" for row in range(rows)]
    )
    
    # 显示表格
    st.dataframe(
        df,
        use_container_width=True,
        height=400
    )

def export_seating_chart():
    """导出座位表"""
    if not st.session_state.seat_arrangement:
        st.warning("没有座位安排可以导出")
        return
    
    # 创建详细的座位表
    rows = st.session_state.classroom_layout['rows']
    cols = st.session_state.classroom_layout['cols']
    row_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    # 创建DataFrame
    data = []
    for row in range(rows):
        for col in range(1, cols+1):
            seat_id = f"{row_letters[row]}{col}"
            student = st.session_state.seat_arrangement.get(seat_id, "")
            data.append({
                "座位号": seat_id,
                "学生姓名": student if student else "空",
                "排": row_letters[row],
                "列": col
            })
    
    df = pd.DataFrame(data)
    
    # 创建Excel文件
    excel_file = "座位安排表.xlsx"
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='座位表', index=False)
        
        # 添加汇总表
        summary_data = {
            "统计项": ["总座位数", "已安排座位", "空座位", "总学生数", "未安排学生"],
            "数量": [
                rows * cols,
                len(st.session_state.seat_arrangement),
                rows * cols - len(st.session_state.seat_arrangement),
                len(st.session_state.students),
                len([s for s in st.session_state.students if s not in st.session_state.seat_arrangement.values()])
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='统计', index=False)
    
    # 提供下载
    with open(excel_file, "rb") as f:
        excel_data = f.read()
    
    st.download_button(
        label="📥 下载座位表(Excel)",
        data=excel_data,
        file_name=f"班级座位表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    # 显示预览
    with st.expander("📄 预览座位表"):
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
