from pathlib import Path

import streamlit as st
from	dotenv	import	load_dotenv
#	.env	파일의 내용을 환경 변수로 로드
load_dotenv(Path(__file__).resolve().parent / ".env")

page_1=st.Page("page_1.py",title='1페이지')


pages=st.navigation([page_1],position="top")

pages.run()
