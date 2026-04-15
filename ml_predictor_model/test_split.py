from splitter import *
from data_collector import *
from features import prepare_features

def run_split_tests(df):

    print("\n" + "="*60)
    print("STATIC TRAIN / VAL / TEST SPLIT CHECK")
    print("="*60)

    splits = simple_split(df)

    train_df = splits['train'].split
    val_df = splits['validation'].split
    test_df = splits['test'].split

    # -------------------------
    # 2. PRINT INFO
    # -------------------------
    print_split_info("TRAIN", train_df)
    print_split_info("VALIDATION", val_df)
    print_split_info("TEST", test_df)

    # -------------------------
    # 3. VALIDATION CHECKS
    # -------------------------
    assert validate_no_leakage(train_df, test_df) 
    assert validate_no_leakage(val_df, test_df)

    print("\nNo leakage in static split!")

    # =========================
    # WALK-FORWARD TEST
    # =========================
    print("\n" + "="*60)
    print("WALK-FORWARD SPLIT CHECK (3 ITERATIONS)")
    print("="*60)

    for i, (train_df, test_df) in enumerate(walk_forward_split(df)):

        if i == 3:
            break

        print(f"\n🔄Iteration {i+1}")

        print_split_info("TRAIN", train_df)
        print_split_info("TEST", test_df)

        assert validate_no_leakage(train_df, test_df)
        print("No leakage in the split\n")

    print("\nWalk-forward validation passed!")


ticker = 'AAPL'
df = load_prices(file_path='./data/AAPL-stock_price.csv')
df = clean_data(df)
df = add_returns(df, ticker)
df = prepare_features(df, horizon=5)

run_split_tests(df)