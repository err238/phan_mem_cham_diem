def calculate_total(df, weights):

    if abs(sum(weights.values()) - 1) > 0.0001:

        raise Exception("Tổng hệ số phải bằng 1")

    total = 0

    for col, w in weights.items():

        if col not in df.columns:

            raise Exception(f"Thiếu cột {col}")

        total += df[col] * w

    df["Total"] = total

    return df