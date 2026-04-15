from tabulate import tabulate

class Split:
    def __init__(self, split, X, y):
        self.split = split
        self.X = X
        self.y = y
        
def simple_split(df, train_pct=0.7, val_pct=0.15):
    n = len(df)
    train_end = int(n*train_pct)
    val_end = int(n * (train_pct + val_pct))
    train_data = df.iloc[:train_end].copy()
    val_data = df.iloc[train_end:val_end].copy()
    test_data = df.iloc[val_end:].copy()
    
    
    return {
            'train': make_split(train_data.copy()),
            'validation': make_split(val_data.copy()),
            'test': make_split(test_data.copy())
        }

def make_split(data_df):
    s = Split(
            data_df.copy(),
            data_df.drop(columns=['High', 'Low', 'Close', 'Volume', 'Target_Return']),
            data_df['Target_Return']
        )
        
    return s
    
def walk_forward_split(df, train_size=252, test_size=21):
    n = len(df)
    start = 0
    while True:
        train_end = start + train_size
        test_end = start + train_size + test_size
        if test_end > n:
            break
        train_df = df.iloc[start:train_end].copy()
        test_df = df.iloc[train_end:test_end].copy()
        
        yield train_df, test_df
        
        # move window forward
        start += test_size

def validate_no_leakage(train_df, test_df):
    return train_df.index.max() < test_df.index.min()    

def print_split_info(name, df):
    print("-"*60)
    print(name)
    print("-"*60)
    headers = ['first row date', 'last row date', 'number of samples']
    data = [[df.index.min(), df.index.max(), df.shape[0]]]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
    
    
    