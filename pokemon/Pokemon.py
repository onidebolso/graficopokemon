import csv
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

class PokemonAnalyzer:
    def __init__(self, csv_file):
        self.df = self._carregar_csv(csv_file)
        self.types = [
            'Normal', 'Fire', 'Water', 'Grass', 'Electric', 'Ice', 'Fighting',
            'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost',
            'Dark', 'Dragon', 'Steel', 'Fairy'
        ]

    def _carregar_csv(self, caminho):
        pokemons = []
        with open(caminho, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                for col in ['Total', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed', 'Generation']:
                    row[col] = int(row[col]) if row[col].isdigit() else 0
                row['Legendary'] = row['Legendary'].strip().lower() in ('true', '1')
                pokemons.append(row)
        return pokemons

    def _filtrar_por_tipo(self, tipo):
        return [p for p in self.df if p['Type 1'] == tipo or p['Type 2'] == tipo]

    def top_10_lendarios_por_tipo(self):
        lendarios = [p for p in self.df if p['Legendary']]
        lendarios_por_tipo = {}
        for p in lendarios:
            t = p['Type 1']
            lendarios_por_tipo.setdefault(t, []).append(p['Name'])
        tipos_ordenados = sorted(lendarios_por_tipo.items(), key=lambda x: len(x[1]), reverse=True)[:10]

        print("=== TOP 10 TIPOS COM MAIS POKÉMONS LENDÁRIOS ===")
        for tipo, pokemons in tipos_ordenados:
            print(f"\n{tipo} ({len(pokemons)} lendários):")
            for nome in pokemons[:10]:
                print(f"  - {nome}")
            if len(pokemons) > 10:
                print(f"  ... e mais {len(pokemons) - 10}")

    def top_10_por_tipo(self, tipo, criterio='Total'):
        pokemons = self._filtrar_por_tipo(tipo)
        top_10 = sorted(pokemons, key=lambda x: x[criterio], reverse=True)[:10]
        print(f"=== TOP 10 POKÉMONS DO TIPO {tipo.upper()} POR {criterio.upper()} ===")
        for p in top_10:
            tipos = f"{p['Type 1']}" + (f"/{p['Type 2']}" if p['Type 2'] else "")
            print(f"{p['Name']} - {tipos}: {p[criterio]}")

    def top_10_por_tipo_vida(self, tipo):
        self.top_10_por_tipo(tipo, 'HP')

    def comparar_tipos(self, tipo1, tipo2):
        def medias(pokemons):
            campos = ['Total', 'HP', 'Attack', 'Defense']
            medias = {}
            for c in campos:
                medias[c] = sum(p[c] for p in pokemons) / len(pokemons) if pokemons else 0
            return medias

        t1 = self._filtrar_por_tipo(tipo1)
        t2 = self._filtrar_por_tipo(tipo2)

        m1 = medias(t1)
        m2 = medias(t2)

        print(f"=== COMPARAÇÃO: {tipo1.upper()} vs {tipo2.upper()} ===")
        print(f"Médias - {tipo1}: {m1}")
        print(f"Médias - {tipo2}: {m2}")

    def comparar_pokemons(self, nome1, nome2):
        p1 = next((p for p in self.df if p['Name'].lower() == nome1.lower()), None)
        p2 = next((p for p in self.df if p['Name'].lower() == nome2.lower()), None)
        if not p1 or not p2:
            print("Um dos pokémons não foi encontrado.")
            return

        print(f"=== COMPARAÇÃO: {p1['Name'].upper()} vs {p2['Name'].upper()} ===")
        stats = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed', 'Total']
        for s in stats:
            diff = p1[s] - p2[s]
            vencedor = p1['Name'] if diff > 0 else p2['Name'] if diff < 0 else 'Empate'
            print(f"{s}: {p1[s]} vs {p2[s]} → {vencedor} ({diff:+})")

        if p1['Total'] > p2['Total']:
            print(f"\n🎉 {p1['Name']} é mais forte ({p1['Total']} vs {p2['Total']})")
        elif p2['Total'] > p1['Total']:
            print(f"\n🎉 {p2['Name']} é mais forte ({p2['Total']} vs {p1['Total']})")
        else:
            print("\n⚖️ Empate!")

    def pesquisa_filtrada(self, **filters):
        resultado = self.df
        filtros_processados = {}
        for coluna, valor in filters.items():
            coluna_formatada = coluna.replace('_', ' ').title()
            val = valor.strip().lower()

            if val in ('true', 'false'):
                filtros_processados[coluna_formatada] = (val == 'true')
            else:
                try:
                    filtros_processados[coluna_formatada] = int(val)
                except ValueError:
                    filtros_processados[coluna_formatada] = valor.strip().lower()
        def combina(pokemon, filtros):
            for col, val in filtros.items():
                if col not in pokemon:
                    return False
                dado = pokemon[col]
                if isinstance(val, bool):
                    if pokemon[col] != val:
                        return False
                elif isinstance(val, int):
                    if isinstance(dado, int):
                        if dado != val:
                            return False
                    else:
                        try:
                            if int(dado) != val:
                                return False
                        except:
                            return False
                else:
                    if str(dado).strip().lower() != val:
                        return False
            return True

        filtrados = [p for p in resultado if combina(p, filtros_processados)]

        print(f"\n=== RESULTADOS ({len(filtrados)} encontrados) ===")
        if not filtrados:
            print("Nenhum Pokémon encontrado com esses filtros.")
        else:
            for p in filtrados[:10]:
                tipos = f"{p['Type 1']}" + (f"/{p['Type 2']}" if p['Type 2'] else "")
                print(f"{p['Name']} - {tipos} | Total: {p['Total']} | Geração: {p['Generation']} | Lendário: {p['Legendary']}")

        return filtrados

    def analise_conjuntos(self, tipo1, tipo2):
        df1 = [p for p in self.df if p['Type 1'] == tipo1][:5]
        df2 = [p for p in self.df if p['Type 1'] == tipo2][:5]

        if not df1 or not df2:
            print("Um dos tipos não possui pokémons suficientes.")
            return

        print(f"=== ANÁLISE ENTRE {tipo1.upper()} E {tipo2.upper()} ===")
        stats = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed', 'Total']
        diff_acum = {s: 0 for s in stats}

        for i in range(5):
            p1, p2 = df1[i], df2[i]
            print(f"\n{p1['Name']} vs {p2['Name']}")
            for s in stats:
                diff = p1[s] - p2[s]
                diff_acum[s] += diff
                vencedor = tipo1 if diff > 0 else tipo2 if diff < 0 else "Empate"
                print(f"  {s}: {p1[s]} vs {p2[s]} → {vencedor} ({diff:+})")

        print("\n=== MÉDIAS DAS DIFERENÇAS ===")
        for s in stats:
            media = diff_acum[s] / 5
            vencedor = tipo1 if media > 0 else tipo2 if media < 0 else "Empate"
            print(f"{s}: {media:+.2f} → {vencedor}")

        unicos = len({p['Name'] for p in self._filtrar_por_tipo(tipo1)} |
                     {p['Name'] for p in self._filtrar_por_tipo(tipo2)})
        print(f"\nPokémons únicos no total: {unicos}")

def main():
    analyzer = PokemonAnalyzer('pokemon.csv')

    while True:
        print("\n" + "="*50)
        print("SISTEMA DE ANÁLISE DE POKÉMONS")
        print("="*50)
        print("1. Pokémons lendários por tipo")
        print("2. Top 10 pokémons por tipo")
        print("3. Top 10 por HP")
        print("4. Comparar tipos")
        print("5. Comparar pokémons")
        print("6. Pesquisa filtrada")
        print("7. Análise de tipos")
        print("8. Sair")

        op = input("\nEscolha uma opção: ")
        try:
            if op == '1':
                analyzer.top_10_lendarios_por_tipo()
            elif op == '2':
                t = input("Digite o tipo: ").capitalize()
                analyzer.top_10_por_tipo(t)
            elif op == '3':
                t = input("Digite o tipo: ").capitalize()
                analyzer.top_10_por_tipo_vida(t)
            elif op == '4':
                t1 = input("Tipo 1: ").capitalize()
                t2 = input("Tipo 2: ").capitalize()
                analyzer.comparar_tipos(t1, t2)
            elif op == '5':
                n1 = input("Pokémon 1: ")
                n2 = input("Pokémon 2: ")
                analyzer.comparar_pokemons(n1, n2)
            elif op == '6':
                filtros = {}
                print("Digite filtros (ex: Type_1=Fire, Generation=1, Legendary=True)")
                entrada = input("→ ")
                for parte in entrada.split(','):
                    if '=' in parte:
                        chave, valor = parte.split('=', 1)
                        filtros[chave.strip()] = valor.strip()
                analyzer.pesquisa_filtrada(**filtros)
            elif op == '7':
                t1 = input("Tipo 1: ").capitalize()
                t2 = input("Tipo 2: ").capitalize()
                analyzer.analise_conjuntos(t1, t2)
            elif op == '8':
                print("Saindo...")
                break
            else:
                print("Opção inválida.")
        except Exception as e:
            print("Erro:", e)

if __name__ == "__main__":
    main()
