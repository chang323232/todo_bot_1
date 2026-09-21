import streamlit as st
import json
import time
from google import genai
from google.genai import types

# ⭐️ 보안 100%: 웹 서버의 비밀금고에서 API 키를 꺼내옴
# 코랩의 userdata.get()과 완벽하게 똑같은 원리다!
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

def generate_morning_brief(todo_list):
    prompt = f"""
    너는 내 업무 효율을 극대화해 줄 수석 비서다.
    사용자가 쉼표나 띄어쓰기 없이 의식의 흐름대로 할 일들을 막 적어놨다.
    네가 문맥을 파악해서 '개별 할 일(Task)' 단위로 똑똑하게 쪼갠 다음, '아이젠하워 매트릭스'로 분류해라.
    추가로, 각 일정의 성격을 파악해서 오늘 언제 하면 좋을지 '최적의 추천 시간대(예: 14:00~16:00, 퇴근 직후 등)'도 함께 제안해라.
    
    [사용자가 막 던진 할 일 메모]
    {todo_list}
    
    [출력 형식 (반드시 아래 JSON 스키마를 엄격하게 따를 것. 배열 안에는 객체(dict)가 들어가야 함)]
    {{
        "1_urgent_important": [{{"task": "항목1", "time": "추천 시간대"}}, {{"task": "항목2", "time": "추천 시간대"}}],
        "2_not_urgent_important": [{{"task": "항목1", "time": "추천 시간대"}}],
        "3_urgent_not_important": [{{"task": "항목1", "time": "추천 시간대"}}],
        "4_not_urgent_not_important": [{{"task": "항목1", "time": "추천 시간대"}}],
        "briefing": "오늘 일정과 시간 배분에 대한 수석 비서의 냉철한 3줄 요약"
    }}
    """
    
    max_retries = 3 
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text) 
            
        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg:
                time.sleep(3)
            else:
                st.error(f"❌ 에러 발생: {e}")
                return None
    st.error("❌ 구글 서버가 응답하지 않습니다. 나중에 다시 시도해주세요.")
    return None

def print_tasks(task_list):
    if not task_list:
        st.write("   - 없음")
    for item in task_list:
        st.write(f"   - ⏰ **[{item['time']}]** {item['task']}")

# ==========================================
# 🎨 웹사이트 화면(UI) 구성 부분
# ==========================================
st.set_page_config(page_title="수석 비서 시스템", page_icon="🤖")

st.title("🤖 창삣삐 전용 수석 비서")
st.markdown("의식의 흐름대로 할 일을 적어주시면, **아이젠하워 매트릭스** 기반으로 최적의 스케줄을 짜드립니다.")

# 웹사이트의 텍스트 입력창
my_todos = st.text_area("📝 오늘 할 일 (생각나는 대로 막 적으세요):", height=100)

# '분석 시작' 버튼을 눌렀을 때만 아래 로직 실행
if st.button("🚀 분석 시작"):
    if not my_todos.strip():
        st.warning("할 일이 입력되지 않았습니다. 빈둥거릴 계획이라도 적어보세요!")
    else:
        with st.spinner('수석 비서가 일정을 쪼개고 시간을 배분하는 중입니다...'):
            brief_result = generate_morning_brief(my_todos)
            
        if brief_result:
            st.success("분석 완료!")
            
            st.divider() # 구분선
            st.subheader("📋 맞춤형 모닝 브리프 & 스케줄링")
            
            # 웹 화면에 예쁘게 출력
            st.markdown("#### 🔥 [1순위: 긴급/중요]")
            print_tasks(brief_result.get("1_urgent_important", []))
            
            st.markdown("#### 🌱 [2순위: 안긴급/중요]")
            print_tasks(brief_result.get("2_not_urgent_important", []))
            
            st.markdown("#### 📞 [3순위: 긴급/안중요]")
            print_tasks(brief_result.get("3_urgent_not_important", []))
            
            st.markdown("#### 🗑️ [4순위: 안긴급/안중요]")
            print_tasks(brief_result.get("4_not_urgent_not_important", []))
            
            st.divider()
            st.markdown("#### 💡 [수석 비서의 3줄 요약]")
            st.info(brief_result.get("briefing", "요약 없음"))