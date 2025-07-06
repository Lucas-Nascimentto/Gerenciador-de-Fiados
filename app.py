import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import altair as alt

# Configurações iniciais
st.set_page_config(layout="centered", page_title="Gerenciador de Fiados", page_icon='none', initial_sidebar_state='auto')

# Função para verificar login
def check_login(username, password):
    return username == "admin" and password == "admin"

# Função para carregar ou criar o arquivo Excel
def load_or_create_excel():
    if not os.path.exists("vendasFiado.xlsx"):
        df = pd.DataFrame(columns=["Fiador", "Valor", "Data"])
        df.to_excel("vendasFiado.xlsx", index=False)
        return df
    return pd.read_excel("vendasFiado.xlsx")

# Função para quitar a dívida de um fiador
def pay_debt(fiador):
    df = load_or_create_excel()
    df = df[df["Fiador"] != fiador]  # Remove as entradas do fiador
    df.to_excel("vendasFiado.xlsx", index=False)  # Salva as alterações
    return df

# Main app flow
def main():
    if not hasattr(st.session_state, "logged_in"):
        st.session_state.logged_in = False
    
    if st.session_state.logged_in:
        # Sidebar menu
        selected = st.sidebar.selectbox("Menu de Ações:", ["Adicionar Venda", "Relatórios", "Quitar Dívida"])
        
        if selected == "Adicionar Venda":
            df = load_or_create_excel()
            
            with st.form("nova_venda_form"):
                st.header("Nova Venda Fiada")
                fiador = st.text_input("Nome do Fiador")
                valor = st.number_input("Valor da Venda", min_value=0.01, step=0.01)
                data = st.date_input("Data da Venda")
                
                submitted = st.form_submit_button("Adicionar Venda")
                
                if submitted:
                    if fiador and valor and data:
                        new_row = pd.DataFrame({"Fiador": [fiador], "Valor": [valor], "Data": [data.strftime("%Y-%m-%d")]})
                        df = pd.concat([df, new_row], ignore_index=True)
                        df.to_excel("vendasFiado.xlsx", index=False)
                        st.success("Venda adicionada com sucesso!")
                        time.sleep(1)
                        st.rerun()

            st.header("Histórico de Vendas Fiadas")
            st.dataframe(df)

        elif selected == "Relatórios":
            df = pd.read_excel("vendasFiado.xlsx") if os.path.exists("vendasFiado.xlsx") else pd.DataFrame()
            
            if not df.empty:
                st.header("Relatório de Saldos Devedores")
                saldos = df.groupby("Fiador")["Valor"].sum().reset_index()
                saldos = saldos.sort_values("Valor", ascending=False)
                
                st.subheader("Saldos Devedores por Fiador")

                # Criação do gráfico com Altair
                chart = alt.Chart(saldos).mark_bar(
                    cornerRadiusTopLeft=5,
                    cornerRadiusTopRight=5
                ).encode(
                    y=alt.Y('Valor:Q', title='Valor Total (R$)', axis=alt.Axis(grid=False)),
                    x=alt.X('Fiador:N', sort='-x', title='Fiador'),
                    tooltip=['Fiador', 'Valor']
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

                # Tabela abaixo do gráfico
                st.dataframe(saldos)
            else:
                st.header("Relatório de Saldos Devedores")
                st.info("Nenhuma venda fiada registrada ainda.")

        elif selected == "Quitar Dívida":
            st.title("Quitar Dívida do Fiador")
            df = load_or_create_excel()
            
            if not df.empty:
                fiador_selecionado = st.selectbox("Selecione o Fiador", df["Fiador"].unique())
                
                if st.button("Quitar Dívida"):
                    pay_debt(fiador_selecionado)
                    st.success(f"Dívida do fiador '{fiador_selecionado}' quitada com sucesso!")
                    time.sleep(1) 
                    st.rerun()
            else:
                st.info("Nenhuma venda fiada registrada para quitar.")

    else:
        login_page()

# Login page
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
