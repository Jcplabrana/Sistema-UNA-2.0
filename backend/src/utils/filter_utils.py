import pandas as pd

include_keywords = [
    "Evento", "Organização Evento", "Feira", "Confraternização", "Congresso", "Hospedagem", "Palco", "Microfone",
    "Cadeiras", "Mesa", "transmissão", "sala de reunião", "Buffet", "Cine", "som", "ótica", "TV e projetores",
    "Serviços de locação de veículos", "motos", "Hotelaria", "Agenciamento de passagens aéreas", "marítimas",
    "terrestres", "Fornecimento de alimentação", "copa", "café", "Serviços gráficos", "impressos", "edições",
    "Organização de eventos", "Sonorização", "Iluminação", "Propaganda", "assessoria de imprensa", "Brindes",
    "medalhas", "troféus", "brasões", "distintivos"
]
exclude_keywords = [
    "Aquisição", "arma de fogo", "alimentícios", "passagens aérea", "ramo alimentício", "almoço",
    "Fornecimento de Refeições", "Fornecimento de alimentação preparada", "Agência de publicidade",
    "Agências de Propaganda", "Agências de publicidade", "Agência de propaganda e publicidade",
    "Preparo de refeições", "Marmitex"
]

all_cities = [
    "Guarulhos", "Campinas", "São Gonçalo", "São Bernardo do Campo", "Duque de Caxias", "Nova Iguaçu",
    "Santo André", "Osasco", "Sorocaba", "Uberlândia", "Ribeirão Preto",
    "São José dos Campos", "Cuiabá", "Jaboatão dos Guararapes", "Contagem", "Joinville", "Feira de Santana",
    "Aracaju", "Londrina", "Juiz de Fora", "Florianópolis",
    "Aparecida de Goiânia", "Serra", "Campos dos Goytacazes", "Belford Roxo", "Niterói", "São José do Rio Preto",
    "Ananindeua", "Vila Velha", "Caxias do Sul", "Porto Velho",
    "Mogi das Cruzes", "Jundiaí", "Macapá", "São João de Meriti", "Piracicaba", "Campina Grande", "Santos", "Mauá",
    "Montes Claros", "Boa Vista", "Betim", "Maringá", "Anápolis",
    "Diadema", "Carapicuíba", "Petrolina", "Bauru", "Caruaru", "Vitória da Conquista", "Itaquaquecetuba",
    "Rio Branco", "Blumenau", "Ponta Grossa", "Caucaia", "Cariacica", "Franca",
    "Olinda", "Praia Grande", "Cascavel", "Canoas", "Paulista", "Uberaba", "Santarém", "São Vicente",
    "Ribeirão das Neves", "São José dos Pinhais", "Pelotas", "Barueri", "Taubaté",
    "Suzano", "Palmas", "Guarujá", "Cotia", "Taboão da Serra", "Volta Redonda", "Indaiatuba", "São Carlos",
    "Embu das Artes", "Rondonópolis", "Araraquara", "Jacareí", "Marília",
    "Americana", "Hortolândia", "Ipatinga", "Novo Hamburgo", "Sete Lagoas", "Presidente Prudente", "Viamão",
    "São Leopoldo", "Rio Claro", "Santa Bárbara d'Oeste", "Bragança Paulista",
    "Itu", "São Caetano do Sul", "Poços de Caldas", "Atibaia", "Itapecerica da Serra", "Mogi Guaçu",
    "Franco da Rocha", "Varginha", "Caraguatatuba", "Três Lagoas", "Araras", "Resende",
    "Sertãozinho", "Valinhos", "Barretos", "Itatiba", "Jandira", "Cubatão", "Sorriso",
    "Aracaju", "Belém", "Belo Horizonte", "Boa Vista", "Brasília", "Campo Grande",
    "Cuiabá", "Curitiba", "Florianópolis", "Fortaleza", "Goiânia", "João Pessoa",
    "Macapá", "Maceió", "Manaus", "Natal", "Palmas", "Porto Alegre", "Porto Velho",
    "Recife", "Rio Branco", "Rio de Janeiro", "Salvador", "São Luís", "São Paulo",
    "Teresina", "Vitória", "Distrito Federal"
]

def apply_filters(df_all):
    if not df_all.empty:
        mask_include = df_all['Objeto'].str.contains('|'.join(include_keywords), case=False, na=False)
        mask_exclude = df_all['Objeto'].str.contains('|'.join(exclude_keywords), case=False, na=False)
        filtered_df = df_all[mask_include & ~mask_exclude & df_all['Cidade'].isin(all_cities)].copy()

        filtered_df = filtered_df.drop_duplicates(
            subset=['Objeto', 'Modalidade', 'N Licitação', 'Cidade', 'Valor Edital'], keep='first')

        def convert_to_float(value):
            try:
                return float(value.replace('.', '').replace(',', '.'))
            except ValueError:
                return None

        filtered_df['Valor Edital Float'] = filtered_df['Valor Edital'].apply(convert_to_float)
        filtered_df = filtered_df[
            (filtered_df['Valor Edital Float'].isna()) | (filtered_df['Valor Edital Float'] >= 100000)].drop(
            columns=['Valor Edital Float'])

        return filtered_df
    else:
        return df_all
