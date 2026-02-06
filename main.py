import streamlit as st
import pandas as pd
import json
from datetime import datetime
import base64
from io import StringIO

# 页面配置
st.set_page_config(
    page_title="班级座位编排系统",
    page_icon="🎓",
    layout="wide"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    
    .seat-grid {
        display: grid;
        gap: 10px;
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        min-height: 500px;
        border: 2px dashed #ccc;
    }
    
    .student-card {
        padding: 10px 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        cursor: move;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        text-align: center;
        font-weight: bold;
        user-select: none;
        position: relative;
        z-index: 1000;
    }
    
    .student-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .desk {
        width: 100px;
        height: 60px;
        background-color: #8B7355;
        border: 2px solid #654321;
        border-radius: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        position: relative;
    }
    
    .desk.empty {
        background-color: #e0e0e0;
        border: 2px dashed #999;
        color: #666;
    }
    
    .desk-number {
        position: absolute;
        top: -20px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 12px;
        color: #666;
    }
    
    .classroom {
        position: relative;
        width: 100%;
        height: 600px;
        border: 2px solid #333;
        background-color: #f9f9f9;
        margin: 20px 0;
    }
    
    .teacher-desk {
        position: absolute;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 200px;
        height: 80px;
        background-color: #4a6fa5;
        border: 3px solid #2c5282;
        border-radius: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    }
    
    .blackboard {
        position: absolute;
        top: 120px;
        left: 50%;
        transform: translateX(-50%);
        width: 80%;
        height: 100px;
        background-color: #2d3748;
        border: 5px solid #1a202c;
        border-radius: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 20px;
        font-weight: bold;
    }
    
    .row {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 40px;
    }
    
    .control-panel {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .export-btn {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%) !important;
    }
    
    .drag-container {
        min-height: 200px;
        border: 2px dashed #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'students' not in st.session_state:
    st.session_state.students = []
if 'seat_arrangement' not in st.session_state:
    st.session_state.seat_arrangement = {}
if 'classroom_layout' not in st.session_state:
    st.session_state.classroom_layout = {
        'rows': 4,
        'cols': 6,
        'desks_per_row': 6
    }

def main():
    st.title("🎓 班级座位编排系统")
    st.markdown("---")
    
    # 侧边栏控制面板
    with st.sidebar:
        st.header("📋 控制面板")
        
        # 导入学生姓名
        st.subheader("1. 导入学生名单")
        
        import_method = st.radio(
            "选择导入方式",
            ["手动输入", "上传文件", "示例数据"],
            horizontal=True
        )
        
        if import_method == "手动输入":
            student_text = st.text_area(
                "输入学生姓名（每行一个）",
                height=150,
                help="每个学生姓名占一行"
            )
            if student_text:
                students_list = [name.strip() for name in student_text.split('\n') if name.strip()]
                if st.button("导入学生名单"):
                    st.session_state.students = students_list
                    st.success(f"成功导入 {len(students_list)} 名学生")
                    
        elif import_method == "上传文件":
            uploaded_file = st.file_uploader("上传学生名单文件", type=['txt', 'csv', 'xlsx'])
            if uploaded_file:
                try:
                    if uploaded_file.name.endswith('.txt'):
                        content = uploaded_file.read().decode('utf-8')
                        students_list = [name.strip() for name in content.split('\n') if name.strip()]
                    elif uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                        if '姓名' in df.columns:
                            students_list = df['姓名'].dropna().tolist()
                        else:
                            students_list = df.iloc[:, 0].dropna().tolist()
                    else:  # Excel文件
                        df = pd.read_excel(uploaded_file)
                        if '姓名' in df.columns:
                            students_list = df['姓名'].dropna().tolist()
                        else:
                            students_list = df.iloc[:, 0].dropna().tolist()
                    
                    if st.button("导入学生名单"):
                        st.session_state.students = students_list
                        st.success(f"成功导入 {len(students_list)} 名学生")
                except Exception as e:
                    st.error(f"文件读取失败: {str(e)}")
        else:  # 示例数据
            if st.button("加载示例数据"):
                example_students = [
                    "张三", "李四", "王五", "赵六", "钱七", "孙八",
                    "周九", "吴十", "郑十一", "王十二", "李十三", "张十四",
                    "刘十五", "陈十六", "杨十七", "黄十八", "赵十九", "周二十",
                    "吴二十一", "郑二十二", "王二十三", "李二十四"
                ]
                st.session_state.students = example_students
                st.success(f"加载了 {len(example_students)} 名示例学生")
        
        st.markdown("---")
        
        # 教室布局设置
        st.subheader("2. 教室布局设置")
        
        col1, col2 = st.columns(2)
        with col1:
            rows = st.number_input("行数", min_value=1, max_value=10, value=4)
        with col2:
            cols = st.number_input("每行座位数", min_value=1, max_value=10, value=6)
        
        if st.button("更新教室布局"):
            st.session_state.classroom_layout = {
                'rows': rows,
                'cols': cols,
                'desks_per_row': cols
            }
            st.success("教室布局已更新")
        
        st.markdown("---")
        
        # 操作按钮
        st.subheader("3. 操作")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 随机排座", use_container_width=True):
                random_arrange_seats()
        with col2:
            if st.button("🗑️ 清空座位", use_container_width=True):
                st.session_state.seat_arrangement = {}
                st.success("座位已清空")
        
        if st.button("📤 导出座位表", use_container_width=True, type="secondary"):
            export_seating_chart()
    
    # 主内容区
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🏫 教室座位图")
        display_classroom()
        
        # 显示座位安排表格
        if st.session_state.seat_arrangement:
            st.subheader("📊 座位安排表")
            display_seating_table()
    
    with col2:
        st.subheader("👥 学生名单")
        display_student_list()
        
        st.subheader("📝 座位安排")
        if st.session_state.seat_arrangement:
            for seat, student in st.session_state.seat_arrangement.items():
                st.info(f"💺 {seat}: {student}")
        else:
            st.warning("暂无座位安排")
        
        # 拖拽说明
        with st.expander("💡 使用说明"):
            st.markdown("""
            1. **导入学生**: 在左侧导入学生名单
            2. **设置布局**: 调整教室座位布局
            3. **安排座位**:
               - 点击"随机排座"自动安排
               - 或手动输入座位号安排
            4. **导出**: 导出座位表为图片或Excel
            
            **座位编号规则**:
            - A1: 第一排第一个
            - B3: 第二排第三个
            - 以此类推
            """)
    
    # 手动安排座位
    st.markdown("---")
    st.subheader("🎯 手动安排座位")
    
    if st.session_state.students:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            student = st.selectbox("选择学生", st.session_state.students)
        
        with col2:
            row_letter = st.selectbox("排", ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'])
        
        with col3:
            col_num = st.number_input("列", min_value=1, max_value=st.session_state.classroom_layout['cols'], value=1)
        
        seat_id = f"{row_letter}{col_num}"
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("安排到此座位", use_container_width=True):
                assign_seat(student, seat_id)
        with col_btn2:
            if st.button("随机安排", use_container_width=True):
                random_assign_student(student)
        with col_btn3:
            if st.button("移除座位", use_container_width=True):
                remove_student_from_seat(student)

def random_arrange_seats():
    """随机安排座位"""
    if not st.session_state.students:
        st.error("请先导入学生名单")
        return
    
    rows = st.session_state.classroom_layout['rows']
    cols = st.session_state.classroom_layout['cols']
    
    import random
    students = st.session_state.students.copy()
    random.shuffle(students)
    
    seat_arrangement = {}
    row_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    seat_index = 0
    for i in range(rows):
        for j in range(1, cols + 1):
            if seat_index < len(students):
                seat_id = f"{row_letters[i]}{j}"
                seat_arrangement[seat_id] = students[seat_index]
                seat_index += 1
    
    st.session_state.seat_arrangement = seat_arrangement
    st.success(f"已随机安排 {seat_index} 名学生的座位")

def assign_seat(student, seat_id):
    """将学生安排到指定座位"""
    # 检查座位是否已被占用
    for existing_seat, existing_student in st.session_state.seat_arrangement.items():
        if existing_student == student:
            st.warning(f"{student} 已经在座位 {existing_seat} 上")
            return
    
    st.session_state.seat_arrangement[seat_id] = student
    st.success(f"已将 {student} 安排到座位 {seat_id}")

def random_assign_student(student):
    """将学生随机安排到空座位"""
    if not st.session_state.students:
        st.error("请先导入学生名单")
        return
    
    rows = st.session_state.classroom_layout['rows']
    cols = st.session_state.classroom_layout['cols']
    row_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    # 找到所有空座位
    empty_seats = []
    for i in range(rows):
        for j in range(1, cols + 1):
            seat_id = f"{row_letters[i]}{j}"
            if seat_id not in st.session_state.seat_arrangement:
                empty_seats.append(seat_id)
    
    if not empty_seats:
        st.error("没有空座位了")
        return
    
    import random
    random_seat = random.choice(empty_seats)
    assign_seat(student, random_seat)

def remove_student_from_seat(student):
    """从座位中移除学生"""
    seats_to_remove = []
    for seat, s in st.session_state.seat_arrangement.items():
        if s == student:
            seats_to_remove.append(seat)
    
    for seat in seats_to_remove:
        del st.session_state.seat_arrangement[seat]
    
    if seats_to_remove:
        st.success(f"已从座位中移除 {student}")
    else:
        st.warning(f"{student} 没有座位安排")

def display_classroom():
    """显示教室座位图"""
    rows = st.session_state.classroom_layout['rows']
    cols = st.session_state.classroom_layout['cols']
    row_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    # 创建教室布局HTML
    html_content = """
    <div class="classroom">
        <div class="teacher-desk">👨‍🏫 讲台</div>
        <div class="blackboard">📚 黑板</div>
    """
    
    # 添加座位
    for i in range(rows):
        html_content += f'<div class="row" id="row-{row_letters[i]}">'
        for j in range(1, cols + 1):
            seat_id = f"{row_letters[i]}{j}"
            student = st.session_state.seat_arrangement.get(seat_id, "")
            
            if student:
                html_content += f'''
                <div class="desk" id="desk-{seat_id}" draggable="true" ondragstart="drag(event)">
                    <div class="desk-number">{seat_id}</div>
                    <div class="student-card" id="student-{seat_id}">
                        {student}
                    </div>
                </div>
                '''
            else:
                html_content += f'''
                <div class="desk empty" id="desk-{seat_id}" ondrop="drop(event)" ondragover="allowDrop(event)">
                    <div class="desk-number">{seat_id}</div>
                    空位
                </div>
                '''
        html_content += '</div>'
    
    html_content += "</div>"
    
    # 添加JavaScript实现拖拽功能
    html_content += """
    <script>
    function allowDrop(ev) {
        ev.preventDefault();
    }
    
    function drag(ev) {
        ev.dataTransfer.setData("text", ev.target.closest('.desk').id);
    }
    
    function drop(ev) {
        ev.preventDefault();
        var data = ev.dataTransfer.getData("text");
        var draggedElement = document.getElementById(data);
        var studentName = draggedElement.querySelector('.student-card').textContent;
        var seatId = ev.target.id.replace('desk-', '');
        
        // 发送数据到Streamlit
        window.parent.postMessage({
            type: 'seat_change',
            student: studentName,
            seat: seatId
        }, '*');
        
        // 更新UI
        ev.target.innerHTML = '<div class="desk-number">' + seatId + '</div>' +
                             '<div class="student-card">' + studentName + '</div>';
        ev.target.classList.remove('empty');
        ev.target.setAttribute('draggable', 'true');
        ev.target.setAttribute('ondragstart', 'drag(event)');
        
        // 清空原来的座位
        draggedElement.innerHTML = '<div class="desk-number">' + data.replace('desk-', '') + '</div>空位';
        draggedElement.classList.add('empty');
        draggedElement.removeAttribute('draggable');
        draggedElement.removeAttribute('ondragstart');
        draggedElement.setAttribute('ondrop', 'drop(event)');
        draggedElement.setAttribute('ondragover', 'allowDrop(event)');
    }
    
    // 监听来自Streamlit的消息
    window.addEventListener('message', function(event) {
        if (event.data.type === 'update_seats') {
            // 可以在这里更新座位
        }
    });
    </script>
    """
    
    st.components.v1.html(html_content, height=650)
    
    # 处理拖拽事件
    if 'seat_change' in st.query_params:
        student = st.query_params['student']
        seat = st.query_params['seat']
        st.session_state.seat_arrangement[seat] = student
        st.experimental_rerun()

def display_student_list():
    """显示学生名单"""
    if not st.session_state.students:
        st.info("请先导入学生名单")
        return
    
    st.markdown(f"**学生总数**: {len(st.session_state.students)} 人")
    
    # 显示未安排座位的学生
    unseated_students = [s for s in st.session_state.students 
                         if s not in st.session_state.seat_arrangement.values()]
    
    if unseated_students:
        st.warning(f"⚠️ {len(unseated_students)} 名学生尚未安排座位:")
        for student in unseated_students:
            st.write(f"👤 {student}")
    
    # 显示所有学生
    st.markdown("---")
    st.markdown("**全部学生名单:**")
    
    cols = 3
    students_per_col = (len(st.session_state.students) + cols - 1) // cols
    
    col_list = st.columns(cols)
    for idx, student in enumerate(st.session_state.students):
        col_idx = idx // students_per_col
        with col_list[col_idx]:
            if student in st.session_state.seat_arrangement.values():
                seat = [k for k, v in st.session_state.seat_arrangement.items() if v == student][0]
                st.success(f"✅ {student} (座位: {seat})")
            else:
                st.write(f"👤 {student}")

def display_seating_table():
    """显示座位安排表格"""
    rows = st.session_state.classroom_layout['rows']
    cols = st.session_state.classroom_layout['cols']
    row_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    # 创建座位表
    seating_data = []
    for i in range(rows):
        row_data = []
        for j in range(1, cols + 1):
            seat_id = f"{row_letters[i]}{j}"
            student = st.session_state.seat_arrangement.get(seat_id, "")
            row_data.append(student)
        seating_data.append(row_data)
    
    # 创建DataFrame
    df = pd.DataFrame(
        seating_data,
        columns=[f"第{i}列" for i in range(1, cols + 1)],
        index=[f"{row_letters[i]}排" for i in range(rows)]
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
        st.error("没有座位安排可以导出")
        return
    
    # 创建DataFrame
    rows = st.session_state.classroom_layout['rows']
    cols = st.session_state.classroom_layout['cols']
    row_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    seating_data = []
    for i in range(rows):
        row_data = []
        for j in range(1, cols + 1):
            seat_id = f"{row_letters[i]}{j}"
            student = st.session_state.seat_arrangement.get(seat_id, "")
            row_data.append(f"{seat_id}: {student}" if student else f"{seat_id}: 空")
        seating_data.append(row_data)
    
    df = pd.DataFrame(
        seating_data,
        columns=[f"第{i}列" for i in range(1, cols + 1)],
        index=[f"{row_letters[i]}排" for i in range(rows)]
    )
    
    # 导出为Excel
    @st.cache_data
    def convert_df_to_excel(df):
        output = pd.ExcelWriter('座位安排表.xlsx', engine='openpyxl')
        df.to_excel(output, sheet_name='座位表')
        output.close()
        return open('座位安排表.xlsx', 'rb').read()
    
    excel_data = convert_df_to_excel(df)
    
    # 下载按钮
    st.download_button(
        label="📥 下载Excel座位表",
        data=excel_data,
        file_name=f"座位安排表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # 显示导出信息
    st.info(f"共导出 {len(st.session_state.seat_arrangement)} 个座位安排")

if __name__ == "__main__":
    main()
