import json

# Carica i dati dal file JSON
with open('input.json') as f:
    data = json.load(f)

# Inizializza un dizionario vuoto per tenere traccia dei codici IPN utilizzati in ogni categoria
used_ipns = {}

# Scorre tutti gli elementi nel file JSON
for item in data:

    # Estrae il codice IPN come intero
    ipn_code = int(item['IPN - Numero di riferimento interno'])

    # Estrae i primi 6 numeri del codice IPN, che rappresentano la categoria
    ipn_code = str(ipn_code).rjust(11, '0')
    category = ipn_code[:6].replace(' ', '0')

    # Aggiunge il codice IPN al dizionario dei codici utilizzati nella categoria corrente
    if category in used_ipns:
        used_ipns[category].add(ipn_code)
    else:
        used_ipns[category] = set([ipn_code])

# Calcola il valore massimo di IPN delle ultime 5 cifre per ogni categoria
max_last_5_digits = {}
for category, ipns in used_ipns.items():
    max_last_5_digits[category] = max(int(ipn[-5:]) for ipn in ipns)

# Numero di IPN liberi da generare per ogni categoria
num_ipns_to_generate = 5

for category, ipns in used_ipns.items():
    ipns_list = sorted(list(ipns))
    if len(ipns_list) == 0:
        max_last_5_digits[category] = int(category + "000001")
        continue
    max_last_5_digits[category] = int(ipns_list[-1][-5:])
    num_generated = 0
    if len(ipns_list) > 1:
        for i in range(len(ipns_list)-1):
            diff = int(ipns_list[i+1][-5:]) - int(ipns_list[i][-5:])
            if diff > 1:
                next_ipn = str(int(ipns_list[i][-5:])+1).rjust(5, '0')
                new_ipn = f"{category}{next_ipn}"
                print(
                    f"Prossimo codice IPN libero per la categoria {category}: {new_ipn}")
                num_generated += 1
                if num_generated >= num_ipns_to_generate:
                    break
        if num_generated >= num_ipns_to_generate:
            print()
            continue
    max_digits = int(ipns_list[-1][-5:])
    for i in range(num_generated, num_ipns_to_generate):
        next_ipn = str(max_digits + i + 1).rjust(5, '0')
        new_ipn = f"{category}{next_ipn}"
        print(
            f"Prossimo codice IPN libero per la categoria {category}: {new_ipn}")
    print()
