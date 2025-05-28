from colorama import Fore, Style

def get_currency_input(prompt):
    while True:
        try:
            value = input(Fore.YELLOW + prompt + Style.RESET_ALL).strip()
            if value.startswith("$"):
                value = value[1:]
            return float(value)
        except ValueError:
            print(f"{Fore.RED}Invalid amount. Please enter numbers (e.g. 50 or -20.50){Style.RESET_ALL}")

def print_table(headers, rows):
    if not rows or not headers:
        print(f"{Fore.RED}No data to display{Style.RESET_ALL}")
        return

    col_widths = []
    for i in range(len(headers)):
        max_len = len(headers[i])
        for row in rows:
            if i < len(row):
                max_len = max(max_len, len(str(row[i])))
        col_widths.append(max_len)
    
    header_row = " | ".join(
        f"{Fore.CYAN}{header:<{width}}{Style.RESET_ALL}"
        for header, width in zip(headers, col_widths)
    )
    
    separator = "-" * (sum(col_widths) + 3 * (len(headers) - 1))
    
    print(f"\n{separator}")
    print(header_row)
    print(separator)
    
    for row in rows:
        row_data = list(row) + [""] * (len(headers) - len(row))
        print(" | ".join(
            f"{str(item):<{width}}"
            for item, width in zip(row_data[:len(headers)], col_widths)
        ))
    
    print(separator)
    print(f"{Fore.BLUE}End of table{Style.RESET_ALL}\n")