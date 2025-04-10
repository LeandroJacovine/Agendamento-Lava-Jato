import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import os

# Nome do arquivo Excel
arquivo_excel = 'agenda_lava_jato.xlsx'

# Senha do administrador
senha_admin = "admin123"

# Endereço da loja
endereco_loja = "Av. José Faria da Rocha, 3772 - Eldorado - Contagem - MG"

# Função para criar o arquivo Excel se não existir
def criar_arquivo_excel():
    if not os.path.exists(arquivo_excel):
        df = pd.DataFrame(columns=["Data", "Horário", "Nome", "CPF", "Telefone", "Placa", "Modelo", "Serviço"])
        df.to_excel(arquivo_excel, index=False)

# Função para carregar a agenda
def carregar_agenda():
    if os.path.exists(arquivo_excel):
        df = pd.read_excel(arquivo_excel, dtype=str)
        if not df.empty:
            df['Data_Hora'] = pd.to_datetime(df['Data'] + ' ' + df['Horário'], format='%d/%m/%Y %H:%M')
            df = df.sort_values('Data_Hora').drop('Data_Hora', axis=1)
            colunas_ordenadas = ["Data", "Horário", "Nome", "CPF", "Telefone", "Placa", "Modelo", "Serviço"]
            df = df[colunas_ordenadas]
        return df
    else:
        return pd.DataFrame(columns=["Data", "Horário", "Nome", "CPF", "Telefone", "Placa", "Modelo", "Serviço"])

# Função para salvar agendamento
def salvar_agendamento(nome, cpf, telefone, placa, modelo, servico, data, horario):
    df = carregar_agenda()
    novo_agendamento = pd.DataFrame([[data, horario, nome, cpf, telefone, placa, modelo, servico]],
                                    columns=["Data", "Horário", "Nome", "CPF", "Telefone", "Placa", "Modelo", "Serviço"])
    df = pd.concat([df, novo_agendamento], ignore_index=True)
    df.to_excel(arquivo_excel, index=False)
    st.success(f"✅ Agendamento salvo com sucesso para {data} às {horario}!")

# Função para cancelar agendamento
def cancelar_agendamento(cpf_cliente):
    df = carregar_agenda()
    df_filtrado = df[df['CPF'] != cpf_cliente]
    if len(df) == len(df_filtrado):
        st.error("❌ Agendamento não encontrado.")
    else:
        df_filtrado.to_excel(arquivo_excel, index=False)
        st.success("✅ Agendamento cancelado com sucesso!")

# Configuração da página
st.set_page_config(page_title="LAVA JATO - AUTO TRUCK ELDORADO", layout="wide")

# Estilização personalizada
def custom_style():
    st.markdown(f"""
        <style>
            body {{
                background-color: #f5f5f5;
                font-family: Arial, sans-serif;
            }}
            header {{
                background-color: #FFD700;
                padding: 15px 0;
                text-align: center;
                margin-bottom: 30px;
            }}
            header h1 {{
                color: black;
                margin: 0;
                font-weight: bold;
                font-size: 28px;
            }}
            header h3 {{
                color: black;
                margin: 0;
                font-size: 16px;
                margin-top: 5px;
            }}
            .stApp {{
                background-color: #f5f5f5;
                max-width: 100% !important;
                padding: 0 20px;
            }}
            .block-container {{
                background-color: white;
                padding: 2rem;
                border-radius: 15px;
                margin: 1rem auto;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            .stButton button {{
                background-color: #FFD700;
                color: black;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                margin-top: 0.5rem;
                border: none;
                font-weight: bold;
                width: 100%;
            }}
            .stButton button:hover {{
                background-color: #e6c200;
                color: black;
            }}
            .form-container {{
                margin-bottom: 30px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th {{
                background-color: #FFD700 !important;
                color: black !important;
                text-align: left !important;
                padding: 8px !important;
            }}
            td {{
                padding: 8px !important;
                border-bottom: 1px solid #ddd !important;
            }}
            tr:hover {{
                background-color: #f5f5f5 !important;
            }}
        </style>
    """, unsafe_allow_html=True)

custom_style()

# Inicialização do arquivo
criar_arquivo_excel()

# Cabeçalho
st.markdown(f'<header><h1>🚗 LAVA JATO - AUTO TRUCK ELDORADO</h1><h3>{endereco_loja}</h3></header>', unsafe_allow_html=True)

# Variáveis de controle de estado
if 'horario_selecionado' not in st.session_state:
    st.session_state['horario_selecionado'] = None

# Layout em colunas
col1, col2 = st.columns([2, 3])

with col1:
    # Formulário de agendamento
    with st.form("form_agendamento"):
        st.header("📅 Novo Agendamento")

        nome = st.text_input("Nome do Associado(a)*")
        cpf = st.text_input("CPF do Associado(a)*")
        telefone = st.text_input("Telefone*")
        placa = st.text_input("Placa do Veículo*").upper()
        modelo = st.text_input("Modelo do Veículo*")
        servico = "LAVAGEM SIMPLES"
        st.text_input("Serviço", value=servico, disabled=True)

        data = st.date_input("Data do Agendamento*", format="DD/MM/YYYY")

        # Gerar horários disponíveis
        inicio = time(8, 0)
        fim = time(16, 30)
        horario_atual = datetime.combine(datetime.today(), inicio)
        todos_horarios = []
        while horario_atual.time() <= fim:
            todos_horarios.append(horario_atual.strftime("%H:%M"))
            horario_atual += timedelta(minutes=30)

        data_str = data.strftime("%d/%m/%Y")
        df_agenda = carregar_agenda()
        horarios_ocupados = df_agenda[df_agenda['Data'] == data_str]['Horário'].tolist()
        horarios_disponiveis = [h for h in todos_horarios if h not in horarios_ocupados]

        if horarios_disponiveis:
            horario = st.selectbox("Horário*", horarios_disponiveis, key=f"horario_{data_str}")
        else:
            horario = None
            st.warning("⚠️ Todos os horários estão ocupados para esta data. Por favor, escolha outra.")

        submit = st.form_submit_button("Agendar")

        if submit:
            campos_obrigatorios = {
                "Nome": nome,
                "CPF": cpf,
                "Telefone": telefone,
                "Placa": placa,
                "Modelo": modelo
            }

            campos_vazios = [campo for campo, valor in campos_obrigatorios.items() if not valor]

            if campos_vazios:
                st.error(f"❌ Por favor, preencha todos os campos obrigatórios: {', '.join(campos_vazios)}")
            elif not horario:
                st.error("❌ Por favor, selecione um horário disponível.")
            else:
                salvar_agendamento(nome, cpf, telefone, placa, modelo, servico, data_str, horario)
                # Limpar estado após agendar
                st.experimental_rerun()

    # Cancelar agendamento
    with st.form("form_cancelar"):
        st.header("❌ Cancelar Agendamento")
        cpf_cancelar = st.text_input("CPF do Cliente para Cancelar*")
        submit_cancelar = st.form_submit_button("Cancelar Agendamento")

        if submit_cancelar:
            if not cpf_cancelar:
                st.error("❌ Por favor, informe o CPF do cliente.")
            else:
                cancelar_agendamento(cpf_cancelar)

with col2:
    # Acesso do administrador
    with st.expander("🔒 Acesso do Administrador", expanded=True):
        senha_digitada = st.text_input("Digite a senha do administrador:", type="password")
        admin_logado = senha_digitada == senha_admin

        if admin_logado:
            st.success("✅ Acesso administrativo concedido")

            st.header("📖 Agenda")
            data_filtro = st.date_input("Filtrar por data:", format="DD/MM/YYYY")

            df_agenda = carregar_agenda()

            if not df_agenda.empty:
                data_filtro_str = data_filtro.strftime("%d/%m/%Y")
                df_filtrado = df_agenda[df_agenda['Data'] == data_filtro_str]

                if not df_filtrado.empty:
                    st.markdown(
                        df_filtrado.to_html(index=False, justify='left', classes='dataframe', border=0),
                        unsafe_allow_html=True
                    )

                    if st.button("Exportar Agenda para Excel"):
                        with st.spinner("Exportando..."):
                            df_filtrado.to_excel("agenda_exportada.xlsx", index=False)
                            st.success("Agenda exportada com sucesso!")
                            with open("agenda_exportada.xlsx", "rb") as file:
                                st.download_button(
                                    label="Baixar Arquivo",
                                    data=file,
                                    file_name="agenda_exportada.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                else:
                    st.info("Nenhum agendamento encontrado para a data selecionada.")
            else:
                st.info("Nenhum agendamento encontrado.")

        elif senha_digitada:
            st.error("❌ Senha incorreta")
