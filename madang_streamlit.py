import streamlit as st
import pandas as pd
import psycopg2

st.title("마당서점 주문 조회")

with st.form("search"):
    name = st.text_input("고객 이름", value="박지성")
    search = st.form_submit_button("조회")

if search:
    name = name.strip()
    if not name:
        st.warning("고객 이름을 입력하세요.")
    else:
        dbConn = None
        try:
            dbConn = psycopg2.connect(
                st.secrets["DATABASE_URL"],
                sslmode="require",
                connect_timeout=15
            )
            with dbConn.cursor() as cursor:
                sql = """
                    SELECT o.orderid, c.name, b.bookname,
                           o.saleprice, o.orderdate
                    FROM Customer c, Orders o, Book b
                    WHERE c.name = %s
                      AND c.custid = o.custid
                      AND b.bookid = o.bookid
                    ORDER BY o.orderid
                """
                cursor.execute(sql, (name,))
                result = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                result = pd.DataFrame(result, columns=columns)
            if result.empty:
                st.info("해당 고객의 주문 내역이 없습니다.")
            else:
                st.dataframe(result, hide_index=True)
        except (KeyError, FileNotFoundError):
            st.error("Streamlit 앱의 Secrets에 DATABASE_URL을 설정하세요.")
        except psycopg2.Error:
            st.error("DB 조회에 실패했습니다. Neon 연결 정보와 테이블을 확인하세요.")
        finally:
            if dbConn is not None:
                dbConn.close()
