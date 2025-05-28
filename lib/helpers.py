from colorama import Fore, Style

def get_currency_input(prompt: str) -> float:
    """Get and validate currency input from user.
    
    Args:
        prompt: Message to display when asking for input
        
    Returns:
        Validated float number
        
    Example:
        >>> amount = get_currency_input("Enter amount: $")
        Enter amount: $50.25
        >>> print(amount)
        50.25
    """
    while True:
        try:
            value = input(Fore.YELLOW + prompt + Style.RESET_ALL).strip()
            value = value.replace('$', '').replace(',', '')
            num = float(value)
            
            if num == 0:
                print(f"{Fore.RED}Amount can't be zero{Style.RESET_ALL}")
                continue
                
            return num
        except ValueError:
            print(f"{Fore.RED}Invalid amount. Please enter like 50 or -20.50{Style.RESET_ALL}")

def print_table(headers: list, rows: list) -> None:
    """Print formatted table with headers and rows.
    
    Args:
        headers: List of column headers
        rows: List of lists containing row data
        
    Example:
        >>> headers = ["Name", "Age"]
        >>> rows = [["Alice", 30], ["Bob", 25]]
        >>> print_table(headers, rows)
    """
    if not rows or not headers:
        print(f"{Fore.RED}No data to display{Style.RESET_ALL}")
        return

    # Calculate column widths
    col_widths = [
        max(len(str(row[i])) if i < len(row) else 0 for row in [headers] + rows)
        for i in range(len(headers))
    ]

    # Build header
    header_parts = []
    for header, width in zip(headers, col_widths):
        header_parts.append(f"{Fore.CYAN}{header:<{width}}{Style.RESET_ALL}")
    
    separator = "-+-".join('-' * width for width in col_widths)
    
    # Print table
    print(f"\n{separator}")
    print(" | ".join(header_parts))
    print(separator)
    
    for row in rows:
        row_str = []
        for i, item in enumerate(row[:len(headers)]):
            row_str.append(f"{str(item):<{col_widths[i]}}")
        print(" | ".join(row_str))
    
    print(f"{separator}\n")