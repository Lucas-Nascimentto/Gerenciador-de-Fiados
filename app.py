import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import altair as alt
from conexao import get_connection
from dotenv import load_dotenv


load_dotenv()  # carrega as variáveis do .env para o ambiente

# Configurações iniciais
st.set_page_config(layout="centered", page_title="Gerenciador de Fiados", page_icon='none', initial_sidebar_state='auto')

# Verifica login fixo
def check_login(username, password):
    return username == "admin" and password == "admin"

# Carrega todas as vendas
def load_vendas():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM vendas", conn)
    conn.close()
    return df

# Adiciona nova venda
def adicionar_venda(fiador, valor, data):
    conn = get_connection()
    cursor = conn.cursor()
    query = "INSERT INTO vendas (fiador, valor, data) VALUES (%s, %s, %s)"
    cursor.execute(query, (fiador, valor, data))
    conn.commit()
    cursor.close()
    conn.close()

# Quita a dívida de um fiador (remove todos os registros dele)
def pay_debt(fiador):
    conn = get_connection()
    cursor = conn.cursor()
    query = "DELETE FROM vendas WHERE fiador = %s"
    cursor.execute(query, (fiador,))
    conn.commit()
    cursor.close()
    conn.close()

# Página principal
def main():
    if not hasattr(st.session_state, "logged_in"):
        st.session_state.logged_in = False
    
    if st.session_state.logged_in:
        selected = st.sidebar.selectbox("Menu de Ações:", ["Adicionar Venda", "Relatórios", "Quitar Dívida"])
        
        if selected == "Adicionar Venda":
            with st.form("nova_venda_form"):
                st.header("Nova Venda Fiada")
                fiador = st.text_input("Nome do Fiador")
                valor = st.number_input("Valor da Venda", min_value=0.01, step=0.01)
                data = st.date_input("Data da Venda")
                
                submitted = st.form_submit_button("Adicionar Venda")
                
                if submitted:
                    if fiador and valor and data:
                        adicionar_venda(fiador, valor, data)
                        st.success("Venda adicionada com sucesso!")
                        time.sleep(1)
                        st.rerun()

            st.header("Histórico de Vendas Fiadas")
            df = load_vendas()
            st.dataframe(df)

        elif selected == "Relatórios":
            df = load_vendas()
            
            if not df.empty:
                st.header("Relatório de Saldos Devedores")
                saldos = df.groupby("fiador")["valor"].sum().reset_index()
                saldos = saldos.sort_values("valor", ascending=False)
                
                st.subheader("Saldos Devedores por Fiador")

                chart = alt.Chart(saldos).mark_bar(
                    cornerRadiusTopLeft=5,
                    cornerRadiusTopRight=5
                ).encode(
                    y=alt.Y('valor:Q', title='Valor Total (R$)', axis=alt.Axis(grid=False)),
                    x=alt.X('fiador:N', sort='-x', title='Fiador'),
                    tooltip=['fiador', 'valor']
                ).properties(
                    width=700,
                    height=400,
                ).configure_view(
                    stroke=None 
                ).configure_axis(
                    labelFontSize=12,
                    titleFontSize=14
                ).configure_mark(
                    color='#4E79A7' 
                )

                st.altair_chart(chart, use_container_width=True)
                st.dataframe(saldos)
            else:
                st.header("Relatório de Saldos Devedores")
                st.info("Nenhuma venda fiada registrada ainda.")

        elif selected == "Quitar Dívida":
            st.title("Quitar Dívida do Fiador")
            df = load_vendas()
            
            if not df.empty:
                fiador_selecionado = st.selectbox("Selecione o Fiador", df["fiador"].unique())
                
                if st.button("Quitar Dívida"):
                    pay_debt(fiador_selecionado)
                    st.success(f"Dívida do fiador '{fiador_selecionado}' quitada com sucesso!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.info("Nenhuma venda fiada registrada para quitar.")

    else:
        login_page()

# Página de login
def login_page():
    st.title("Login")
    username = st.text_input(label="Usuário", placeholder="admin")
    password = st.text_input(label="Senha", placeholder="admin", type="password")
    
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Credenciais incorretas")

if __name__ == "__main__":
    main()