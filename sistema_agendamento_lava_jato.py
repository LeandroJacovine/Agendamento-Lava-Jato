import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import os

# === CONFIGURAÇÕES FIXAS ===
arquivo_excel = 'agenda_lava_jato.xlsx'
senha_admin = "admin123"
endereco_loja = "Av. José Faria da Rocha, 3772 - Eldorado - Contagem - MG"
servico = "LAVAGEM SIMPLES"

# === PALETA DE CORES ===
COR_PRIMARIA = "#2E86AB"
COR_SECUNDARIA = "#F18F01"
COR_TERCIARIA = "#C73E1D"
COR_FUNDO = "#F5F5F5"
COR_TEXTO = "#333333"

# === FUNÇÕES ===
def criar_arquivo_excel():
    if not os.path.exists(arquivo_excel):
        df = pd.DataFrame(columns=["Data", "Horário", "Nome", "CPF", "Telefone", "Placa", "Modelo", "Serviço"])
        df.to_excel(arquivo_excel, index=False)

def carregar_agenda():
    if os.path.exists(arquivo_excel):
        df = pd.read_excel(arquivo_excel, dtype=str)
        if not df.empty:
            df['Data_Hora'] = pd.to_datetime(df['Data'] + ' ' + df['Horário'], format='%d/%m/%Y %H:%M')
            df = df.sort_values('Data_Hora').drop('Data_Hora', axis=1)
            df = df[["Data", "Horário", "Nome", "CPF", "Telefone", "Placa", "Modelo", "Serviço"]]
        return df
    else:
        return pd.DataFrame(columns=["Data", "Horário", "Nome", "CPF", "Telefone", "Placa", "Modelo", "Serviço"])

def salvar_agendamento(nome, cpf, telefone, placa, modelo, servico, data, horario):
    df = carregar_agenda()
    novo = pd.DataFrame([[data, horario, nome, cpf, telefone, placa, modelo, servico]],
                        columns=["Data", "Horário", "Nome", "CPF", "Telefone", "Placa", "Modelo", "Serviço"])
    df = pd.concat([df, novo], ignore_index=True)
    df.to_excel(arquivo_excel, index=False)
    st.success(f"✅ Agendamento salvo com sucesso para {data} às {horario}!")

# === CANCELAMENTO ===
def cancelar_agendamento(cpf_cliente):
    df = carregar_agenda()
    df_filtrado = df[df['CPF'] != cpf_cliente]
    if len(df) == len(df_filtrado):
        st.error("❌ Agendamento não encontrado.")
    else:
        df_filtrado.to_excel(arquivo_excel, index=False)
        st.success("✅ Agendamento cancelado com sucesso!")

# === ESTILO PERSONALIZADO ===
def custom_style():
    st.markdown(f"""
        <style>
            body {{
                background-color: {COR_FUNDO};
                color: {COR_TEXTO};
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .header {{
                background-color: #FFD700;
                color: black;
                padding: 1.5rem;
                border-radius: 0 0 15px 15px;
                margin-bottom: 2rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .card-title {{
                color: {COR_PRIMARIA};
                font-size: 1.3rem;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            .stButton>button {{
                background-color: {COR_PRIMARIA};
                color: white;
                border-radius: 8px;
                padding: 0.7rem 1.5rem;
                border: none;
                font-weight: 600;
                width: 100%;
            }}
            .stButton>button:hover {{
                background-color: {COR_SECUNDARIA};
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
        </style>
    """, unsafe_allow_html=True)

# === CONFIG INICIAL ===
st.set_page_config("LAVA JATO - AUTO TRUCK ELDORADO", layout="wide", page_icon="🚗")
custom_style()
criar_arquivo_excel()

# === CABEÇALHO ===
st.markdown(f"""
    <div class="header">
        <h1>🚗 LAVA JATO - AUTO TRUCK ELDORADO</h1>
        <h3>{endereco_loja}</h3>
    </div>
""", unsafe_allow_html=True)

# === INTERFACE PRINCIPAL ===
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    with st.container():
        st.markdown('<div class="card-title">📅 Novo Agendamento</div>', unsafe_allow_html=True)
        with st.form("form_agendamento", clear_on_submit=True):
            nome = st.text_input("Nome do Associado(a)*")
            cpf = st.text_input("CPF do Associado(a)*")
            telefone = st.text_input("Telefone*")
            placa = st.text_input("Placa do Veículo*").upper()
            modelo = st.text_input("Modelo do Veículo*")
            st.markdown(f"**Serviço:** {servico}")
            data = st.date_input("Data do Agendamento*", min_value=datetime.today())

            # Geração de horários disponíveis
            inicio, fim = time(8, 0), time(16, 30)
            horario_atual = datetime.combine(datetime.today(), inicio)
            todos_horarios = []
            while horario_atual.time() <= fim:
                todos_horarios.append(horario_atual.strftime("%H:%M"))
                horario_atual += timedelta(minutes=30)

            data_str = data.strftime("%d/%m/%Y")
            df_agenda = carregar_agenda()
            ocupados = df_agenda[df_agenda['Data'] == data_str]['Horário'].tolist()
            disponiveis = [h for h in todos_horarios if h not in ocupados]

            if disponiveis:
                horario = st.selectbox("Horário*", disponiveis, key=f"horario_{data_str}")
            else:
                horario = None
                st.warning("⚠️ Todos os horários estão ocupados para esta data. Por favor, escolha outra.")
                if st.button("Escolher outro dia"):
                    st.rerun()

            submit = st.form_submit_button("Agendar")

            if submit:
                campos = {"Nome": nome, "CPF": cpf, "Telefone": telefone, "Placa": placa, "Modelo": modelo}
                vazios = [campo for campo, valor in campos.items() if not valor]
                if vazios:
                    st.error(f"❌ Preencha todos os campos obrigatórios: {', '.join(vazios)}")
                elif not horario:
                    st.error("❌ Selecione um horário disponível.")
                else:
                    salvar_agendamento(nome, cpf, telefone, placa, modelo, servico, data_str, horario)
                    st.balloons()

                    # ✅ MENSAGEM DE CONFIRMAÇÃO
                    st.info(f"""
📝 **Confirmação do Agendamento**
- 📅 Data: `{data_str}`
- 🕒 Horário: `{horario}`
- 🙍‍♂️ Nome: `{nome}`
- 📞 Telefone: `{telefone}`
- 🚗 Placa: `{placa}`
- 🛠️ Serviço: `{servico}`

Se precisar cancelar ou alterar, entre em contato com a nossa equipe.
""")

    with st.container():
        st.markdown('<div class="card-title">❌ Cancelar Agendamento</div>', unsafe_allow_html=True)
        with st.form("form_cancelar"):
            cpf_cancelar = st.text_input("CPF para Cancelamento*")
            if st.form_submit_button("Cancelar Agendamento"):
                if not cpf_cancelar:
                    st.error("❌ Informe o CPF do cliente.")
                else:
                    cancelar_agendamento(cpf_cancelar)

with col2:
    with st.expander("🔒 Área do Administrador", expanded=False):
        senha = st.text_input("Senha do administrador:", type="password")
        if senha == senha_admin:
            st.success("✅ Acesso concedido")
            df_agenda = carregar_agenda()
            st.markdown('<div class="card-title">📖 Agenda Completa</div>', unsafe_allow_html=True)

            colf1, colf2 = st.columns(2)
            with colf1:
                data_filtro = st.date_input("Filtrar por data:")
            with colf2:
                filtro_servico = st.selectbox("Filtrar por serviço:", ["Todos", servico])

            if not df_agenda.empty:
                data_str = data_filtro.strftime("%d/%m/%Y")
                filtrado = df_agenda[df_agenda['Data'] == data_str]
                if filtro_servico != "Todos":
                    filtrado = filtrado[filtrado['Serviço'] == filtro_servico]

                if not filtrado.empty:
                    st.dataframe(filtrado, use_container_width=True, hide_index=True)
                    st.markdown(f"**Total de agendamentos:** {len(filtrado)}")

                    colx1, colx2 = st.columns(2)
                    with colx1:
                        if st.button("Exportar para Excel"):
                            filtrado.to_excel("agenda_exportada.xlsx", index=False)
                            with open("agenda_exportada.xlsx", "rb") as f:
                                st.download_button("⬇️ Baixar Excel", f, file_name=f"agenda_{data_str.replace('/', '-')}.xlsx")
                    with colx2:
                        if st.button("Exportar para CSV"):
                            filtrado.to_csv("agenda_exportada.csv", index=False)
                            with open("agenda_exportada.csv", "rb") as f:
                                st.download_button("⬇️ Baixar CSV", f, file_name=f"agenda_{data_str.replace('/', '-')}.csv")
                else:
                    st.info("ℹ️ Nenhum agendamento encontrado com os filtros selecionados.")
            else:
                st.info("ℹ️ Nenhum agendamento cadastrado.")
        elif senha:
            st.error("❌ Senha incorreta.")

# === RODAPÉ ===
st.markdown("""
    <div style="text-align: center; margin-top: 3rem; color: #666; font-size: 0.9rem;">
        <hr style="border: 0.5px solid #eee; margin-bottom: 1rem;">
        <p>© 2025 Auto Truck Proteção Veicular - Todos os direitos reservados</p>
        <p>Contato: (31) 3370-9888 | Whatsapp (31)99302-2405 Av. José Faria da Rocha, 3772 - Eldorado- Contagem- MG </p>
    </div>
""", unsafe_allow_html=True)

