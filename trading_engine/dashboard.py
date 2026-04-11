from rich.table import Table
from rich.console import Console
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn

console = Console()

class Dashboard:
    def __init__(self, account, position_managers, risk_managers, order_books, my_execution_engine):
        self.position_managers = position_managers
        self.risk_managers = risk_managers
        self.my_execution_engine = my_execution_engine
        self.order_books = order_books
        self.account = account
    
    def display_positions(self, current_prices):
        table = Table(title="Portfolio Positions")

        # Columns
        table.add_column("Symbol", justify="left")
        table.add_column("Quantity", justify="right")
        table.add_column("Avg Price", justify="right")
        table.add_column("Current Price", justify="right")
        table.add_column("Unrealized P&L", justify="right")
        table.add_column("Realized P&L", justify="right")
        
        for symbol, position in self.position_managers[self.account.id].positions.items():
            qty = position.quantity
            avg_price = position.average_entry_price
            current_price = current_prices.get(symbol, 0)
            unrealized_pnl = position.unrealized_pnl(current_price)
            realized_pnl = position.realized_pnl
            unrealized_text = Text(f"{unrealized_pnl:.2f}")
            unrealized_text.stylize("green" if unrealized_pnl > 0 else "red")
            
            realized_text = Text(f"{realized_pnl:.2f}")
            realized_text.stylize("green" if realized_pnl > 0 else "red")
            table.add_row(symbol, 
                          str(qty), 
                          f"{avg_price:.2f}", 
                          f"{current_price:.2f}",
                          unrealized_text,
                          realized_text)
        console.print(table)
    
    def display_recent_orders(self, my_orders, limit=10):
        table = Table(title="Orders")

        # Columns
        table.add_column("Symbol", justify="left")
        table.add_column("order Id", justify="right")
        table.add_column("side", justify="right")
        table.add_column("quantity", justify="right")
        table.add_column("price", justify="right")
        table.add_column("status", justify="right")
        reverse_order = my_orders[-limit:]
        for order in reversed(reverse_order):
            symbol = order.symbol
            order_id = order.order_id
            qty = order.quantity
            side = order.side
            price = order.price
            status = order.status
           
            side_text = Text(f"{side}")
            side_text.stylize("green" if side == "BUY" else "red")
            
            table.add_row(symbol, 
                          str(order_id),
                          side_text, 
                          str(qty), 
                          f"{price:.2f}",
                          status)
            
        console.print(table)
        
    def display_pnl_summary(self, current_prices):
        for symbol, position in self.position_managers[self.account.id].positions.items():
            realized_pnl = position.realized_pnl
            unrealized_pnl = position.unrealized_pnl(current_prices[symbol])
            total_pnl = realized_pnl + unrealized_pnl
            
            unrealized_text = Text(f"Unrealized P&L: {unrealized_pnl:.2f}")
            unrealized_text.stylize("green" if unrealized_pnl > 0 else "red")
            
            realized_text = Text(f"Realized P&L:   {realized_pnl:.2f}")
            realized_text.stylize("green" if realized_pnl > 0 else "red")
        
            total_text = Text(f"Total P&L:      {total_pnl:.2f}")
            total_text.stylize("green" if total_pnl > 0 else "red")
            
            console.print(symbol)
            console.print("---------------------------------------------------------")
            console.print(unrealized_text)
            console.print(realized_text)
            console.print(total_text)

            
        console.print("---------------------------------------------------------")
        total_pnl_portfolio = self.position_managers[self.account.id].get_total_pnl(current_prices)
        total_text_p = Text(f"Total Portfolio P&L:      {total_pnl_portfolio:.2f}")
        total_text_p.stylize("green" if total_pnl_portfolio > 0 else "red")
        console.print(total_text_p)

        
    def display_risk_status(self, current_prices):
        max_position_limit = self.risk_managers[self.account.id].max_position_size
        max_exposure_limit  = self.risk_managers[self.account.id].max_total_exposure
        max_daily_loss  = self.risk_managers[self.account.id].max_daily_loss
        positions = self.position_managers[self.account.id].positions
        total_exposure = sum(
                                [position.quantity*current_prices[position.symbol] 
                                for position in positions.values() 
                                if position.symbol in current_prices])
        
        daily_pnl = self.position_managers[self.account.id].get_total_pnl(current_prices)
        
        largest_position = 0
        for symbol, position in positions.items():
            qty = abs(position.quantity)        
            largest_position = max(largest_position, qty)
        
        pos_usage = largest_position / max_position_limit if max_position_limit else 0
        exp_usage = total_exposure / max_exposure_limit if max_exposure_limit else 0
        loss_usage = max(0, -daily_pnl) / max_daily_loss if max_daily_loss else 0
        
        def get_color(usage):
            if usage >= 0.9:
                return "red"
            elif usage >= 0.75:
                return "yellow"
            else:
                return "green"
        
        progress = Progress(
            TextColumn("[bold]{task.description}"),
            BarColumn(),
            TextColumn("{task.percentage:>5.1f}%"),
            console=console
        )
    
        with progress:
            progress.add_task(
                description=f"[{get_color(pos_usage)}]Position Usage",
                total=100,
                completed=min(pos_usage * 100, 100),
            )
    
            progress.add_task(
                description=f"[{get_color(exp_usage)}]Exposure Usage",
                total=100,
                completed=min(exp_usage * 100, 100),
            )
    
            progress.add_task(
                description=f"[{get_color(loss_usage)}]Daily Loss Usage",
                total=100,
                completed=min(loss_usage * 100, 100),
            )
    
            # render once
            progress.refresh()
    
    def refresh(self, current_prices, orders):
        # clear console
        console.clear(True)
        # print(current_prices, orders)
        # print("position_manager:", self.position_managers[self.account.id].positions)
        # print("risk_manager:", self.risk_managers[self.account.id].max_position_size)
        # print("account: ", self.account)


        console.print("\n#################################################\n")
        console.print("Positions\n")
        self.display_positions(current_prices)
        console.print("\n#################################################\n")
        console.print("Recent orders\n")
        self.display_recent_orders(self.my_execution_engine.order_dict.get(self.account.id, []))
        console.print("\n#################################################\n")
        console.print("Daily PNL\n")
        self.display_pnl_summary(current_prices)
        console.print("\n#################################################\n")
        console.print("Risk Status\n")
        self.display_risk_status(current_prices)
        


        
        
        