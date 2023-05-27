import pandas as pd
import requests
import time

def extend_dataframe(df):
    url = "https://real-time-product-search.p.rapidapi.com/search"

    headers = {
        "X-RapidAPI-Key": "117f8f95a0mshba88c83b1911e30p11685fjsn67151fcbd4f5",
        "X-RapidAPI-Host": "real-time-product-search.p.rapidapi.com"
    }

    # Replace string spaces with actual NaN
    df = df.replace(r'^\s*$', pd.NA, regex=True)

    # Convert EANto string, keeping NaNs as they are
    df['EAN'] = df['EAN'].apply(lambda x: str(int(x)) if pd.notnull(x) and str(x).isnumeric() else pd.NA)

    # Define additional columns
    additional_columns = ["product_description", "product_photos", "product_attributes"]

    extended_df = pd.DataFrame(columns=df.columns.tolist() + additional_columns)

    for i, row in df.iterrows():
        ean = row['EAN']  # Extract the EAN
        if pd.isna(ean):  # If EANis not provided, skip the product
            print(f"Skipping product {i+1} because EANis not provided.")
            continue
        querystring = {"q": ean, "country": "de", "language": "de"}
        try:
            response = requests.get(url, headers=headers, params=querystring)
            response_data = response.json()
            if response_data['data']:
                product_data = response_data['data'][0]

                # Add the new data to the row in the DataFrame
                new_row = row.tolist()
                for column in additional_columns:
                    if column in product_data:
                        new_row.append(product_data[column])
                    else:
                        print(f"No {column} data returned from API for product {i+1} with EAN{ean}.")
                        new_row.append(None)

                # Append the row to the extended DataFrame
                extended_df.loc[i] = new_row

            else:
                print(f"No data returned from API for product {i+1} with EAN{ean}.")
        except Exception as e:
            print(f"Error making API call for product {i+1} with EAN{ean}: {e}")
        time.sleep(1)  # pause for 1 second

    print("Data extended successfully.")
    return extended_df
